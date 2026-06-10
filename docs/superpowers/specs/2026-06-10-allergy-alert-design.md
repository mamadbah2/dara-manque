# Alerte allergie à la prescription — Design Spec

**Date :** 2026-06-10
**Statut :** Approuvé
**Axe différenciateur :** #2 « alerte allergie / interaction médicamenteuse » (voir mémoire `project_differentiation`)

---

## Contexte

Un groupe concurrent développe Dara Manqué à l'identique ; leur spec laisse l'IA « hors périmètre ». On livre **une** brique intelligente fonctionnelle : à la création d'une ordonnance, le système alerte le médecin si un médicament prescrit est incompatible avec une allergie connue du patient — **y compris par cross-réactivité** (allergie « Pénicilline » → prescription « Amoxicilline », mots différents, même classe).

Cadre : projet académique noté. On optimise la démo et la profondeur technique visible.

### Démo cible (15 s)

Patient 1001 (Mamadou Diallo) est allergique à la « Pénicilline » (déjà dans le seed). Le médecin tape « Amoxicilline 500mg » dans le formulaire d'ordonnance → **bandeau rouge instantané** : « ⚠ Risque d'allergie — Pénicilline : l'ordonnance contient amoxicilline ». Le bouton de création est verrouillé tant que le médecin n'a pas coché « Je confirme prescrire malgré l'allergie ».

---

## Décisions de design (validées)

1. **Déclenchement :** live côté frontend (pendant la frappe, debounce) **+** re-validation backend à la création (source de vérité).
2. **Comportement :** avertissement **bloquant avec confirmation** explicite (« Prescrire quand même »), pas de blocage dur.
3. **Intelligence :** classes d'allergènes avec **cross-réactivité** (pas de simple substring).
4. **Périmètre :** allergies uniquement cette itération (interactions médicament-médicament exclues).
5. **Audit :** colonne `allergy_override` + migration Alembic pour tracer les prescriptions forcées.

---

## 1. Moteur de connaissances — `backend/app/allergy_rules.py`

Module isolé, sans dépendance DB, testable unitairement.

### Données

`ALLERGEN_CLASSES : dict[str, list[str]]` — chaque classe regroupe **tous** ses termes (nom de classe + médicaments membres + orthographes/synonymes), normalisés (minuscules, sans accents) :

```python
ALLERGEN_CLASSES = {
    "Pénicilline":   ["penicilline", "amoxicilline", "ampicilline", "augmentin", "clamoxyl", "oxacilline", "cloxacilline"],
    "Aspirine/AINS": ["aspirine", "acide acetylsalicylique", "aspegic", "ibuprofene", "diclofenac", "ketoprofene", "ains"],
    "Sulfamides":    ["sulfamide", "sulfamethoxazole", "bactrim", "cotrimoxazole"],
    "Céphalosporines": ["cephalosporine", "ceftriaxone", "cefixime", "cefuroxime"],
    "Codéine":       ["codeine", "dafalgan codeine", "tramadol"],
    "Iode":          ["iode", "produit de contraste iode", "povidone iodee", "betadine"],
}
```

> ~6 classes couvrant les allergènes fréquents. Volontairement court mais réaliste. La base est facile à étendre.

### Fonction pure

```python
def check_allergy_conflicts(allergies_text: str | None, medications_text: str | None) -> list[dict]
```

Algorithme :
1. Normaliser les deux textes : minuscules, accents retirés (`é→e`), ponctuation/sauts de ligne → espaces.
2. Pour chaque classe `name -> terms` :
   - `allergy_term` = premier terme de la classe présent dans le texte allergies (sinon la classe est ignorée).
   - `medication_term` = premier terme de la classe présent dans le texte médicaments (sinon ignorée).
   - si les deux existent → conflit.
3. Retourner une liste de conflits :
   ```python
   {"allergen_class": "Pénicilline", "allergy_term": "penicilline", "medication_term": "amoxicilline"}
   ```

La cross-réactivité est automatique : `allergies="Pénicilline"` matche la classe par `penicilline`, `medications="Amoxicilline"` la matche par `amoxicilline` → même classe → conflit.

**Détection de termes** : correspondance sur mots entiers (frontières de mots) pour éviter les faux positifs (ex. « ains » ne doit pas matcher « bains »). On compare token par token après normalisation, en gérant les termes multi-mots (ex. « acide acetylsalicylique ») par recherche de sous-séquence.

---

## 2. Modèle de données — `backend/app/models.py`

Ajout sur `Prescription` :

```python
allergy_override = Column(Text, nullable=True)
```

- `NULL` : ordonnance sans conflit (cas normal).
- Rempli : ordonnance forcée malgré une alerte. Format : conflits sérialisés, ex. `"Pénicilline: amoxicilline"` (joindre plusieurs conflits par `; `).

### Migration Alembic

Nouvelle révision :
```python
def upgrade():
    op.add_column('prescriptions', sa.Column('allergy_override', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('prescriptions', 'allergy_override')
```

---

## 3. Schémas — `backend/app/schemas.py`

```python
class AllergyConflict(BaseModel):
    allergen_class: str
    allergy_term: str
    medication_term: str

class AllergyCheckRequest(BaseModel):
    medications: str

class AllergyCheckResponse(BaseModel):
    conflicts: list[AllergyConflict]

class PrescriptionCreate(BaseModel):
    medications: str
    override_allergy: bool = False   # champ ajouté
```

`PrescriptionResponse` : inchangé (l'audit n'a pas besoin d'être renvoyé au client pour le MVP).

---

## 4. API — `backend/app/routers/patients.py`

### Nouveau : check live

```
POST /patients/{patient_id}/prescriptions/check   (médecin)
body  : { "medications": "..." }
200   : { "conflicts": [ AllergyConflict, ... ] }
404   : patient inconnu
```
Le serveur lit `patient.allergies` et appelle `check_allergy_conflicts`. Le frontend n'envoie jamais les allergies.

### Modifié : création durcie

```
POST /patients/{patient_id}/prescriptions   (médecin)
body : { "medications": "...", "override_allergy": false }
```
- Calculer `conflicts = check_allergy_conflicts(patient.allergies, body.medications)`.
- `conflicts` non vide **et** `override_allergy == False` → `HTTPException(409, detail={"conflicts": [...]})`.
- `conflicts` non vide **et** `override_allergy == True` → créer, écrire `allergy_override` (conflits sérialisés).
- `conflicts` vide → créer normalement (`allergy_override = NULL`).

---

## 5. Frontend

### `web/src/api/types.ts`
```ts
export interface AllergyConflict {
  allergen_class: string;
  allergy_term: string;
  medication_term: string;
}
```

### `web/src/api/client.ts`
```ts
export const checkPrescription = (patientId: number, medications: string) =>
  api.post<{ conflicts: AllergyConflict[] }>(
    `/patients/${patientId}/prescriptions/check`, { medications });
```
`createPrescription` gagne un paramètre `overrideAllergy: boolean` → envoyé comme `override_allergy`.

### `web/src/pages/doctor/PrescriptionForm.tsx`
- State : `conflicts: AllergyConflict[]`, `override: boolean`.
- `useEffect` sur `medications` avec **debounce ~400 ms** → `checkPrescription` → `setConflicts`. Texte vide → conflits vidés. Annuler le timer au démontage / changement.
- Si `conflicts.length > 0` :
  - **bandeau rouge** (`alert alert-error`) listant chaque conflit : « ⚠ Risque d'allergie — *{allergen_class}* : l'ordonnance contient *{medication_term}* ».
  - **case à cocher** « Je confirme prescrire malgré l'allergie » → `override`.
  - bouton « Créer l'ordonnance » `disabled` tant que `override == false`.
- Submit : `createPrescription(patientId, medications, override)`.
- Gestion défensive du `409` (si le live check a été contourné) : afficher les conflits renvoyés + forcer la confirmation, sans planter.
- Reset après succès : vider `medications`, `conflicts`, `override`.

---

## 6. Seed — `backend/seed.py`

Aucune modification nécessaire : patient 1001 est déjà allergique à « Pénicilline ». La démo Amoxicilline fonctionne tel quel. (Option : ajouter une ligne de commentaire documentant le scénario de démo.)

---

## 7. Tests

### Unitaires — `backend/tests/test_allergy.py`
- match exact : `allergies="Pénicilline"`, `medications="Pénicilline 1g"` → 1 conflit.
- cross-réactivité : `allergies="Pénicilline"`, `medications="Amoxicilline 500mg"` → 1 conflit (classe Pénicilline).
- insensible casse + accents : `allergies="penicilline"`, `medications="AMOXICILLINE"` → conflit.
- aucun conflit : `allergies="Pénicilline"`, `medications="Paracétamol 1g"` → 0.
- allergies vides / `None` → 0.
- multi-allergies : `allergies="Pénicilline, Aspirine"`, `medications="Ibuprofène"` → conflit classe Aspirine/AINS.
- pas de faux positif sur sous-chaîne (« ains » dans « bains ») → 0.

### API — `backend/tests/test_prescriptions.py` (ou test_allergy)
- `POST .../prescriptions/check` patient 1001 + « Amoxicilline » → 200, 1 conflit.
- create patient 1001 + « Amoxicilline » sans override → **409**, ordonnance non créée.
- create patient 1001 + « Amoxicilline » + `override_allergy=true` → **201**, `allergy_override` rempli en base.
- create patient 1001 + « Paracétamol » → **201**, `allergy_override` NULL.
- check/create exigent le rôle médecin (403 sinon) — couvert par les patterns existants.

---

## Fichiers touchés (récap)

**Créés :**
- `backend/app/allergy_rules.py`
- `backend/alembic/versions/<rev>_add_allergy_override.py`
- `backend/tests/test_allergy.py`

**Modifiés :**
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/routers/patients.py`
- `web/src/api/types.ts`
- `web/src/api/client.ts`
- `web/src/pages/doctor/PrescriptionForm.tsx`

**Hors périmètre :** interactions médicament-médicament, app mobile, UI d'édition de la base de connaissances.
