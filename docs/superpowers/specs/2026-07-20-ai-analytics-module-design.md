# Module « Analytics IA » — Design

**Date :** 2026-07-20
**Statut :** Validé (brainstorming)
**Axe produit :** « Partie AI » de Dara Manqué (démo hackathon, objectif = impressionner le jury)

## Objectif

Intégrer un module d'intelligence artificielle **visible et impressionnant** dans la
solution Dara Manqué, à partir des modèles pré-entraînés fournis dans
`projet_medical_ia.zip`. Priorité à l'effet démo (« notre solution embarque de l'IA
qui tourne »), au sein d'**un seul produit cohérent** — l'app React existante.

## Périmètre

**Deux modèles retenus**, les plus visuels et autonomes :

1. **Prévision d'affluence hospitalière** — réseau de neurones (`MLPRegressor`) +
   `StandardScaler`. Prédit le nombre de patients pour les 30 prochains jours à partir
   de features temporelles (jour de la semaine, mois, saison, moyennes mobiles, lags).
2. **Détection de fraude / nomadisme médical** — `IsolationForest` + `StandardScaler`.
   Repère les patients au comportement anormal (nombreuses visites, multiples
   médecins/hôpitaux/médicaments distincts).

**Hors périmètre** (volontairement écartés pour rester focalisé) :
- Risque de réadmission (`RandomForest` de 105 Mo — trop lourd, cible arbitraire).
- NLP effets indésirables (l'axe allergie est déjà couvert par `allergy_rules.py`).
- Détection de pénurie/épidémie (moins parlant visuellement ; ré-intégrable plus tard).

## Contrainte de données (importante)

Les modèles ont été entraînés sur un **dataset Kaggle synthétique**
(`healthcare_dataset_2.csv`, colonnes anglaises : `Name, Age, Medical Condition,
Billing Amount, Room Number`…), **pas** sur le schéma réel de Dara Manqué
(`patients`, `prescriptions`, `cards`). Les features nécessaires (montant de
facturation, nº de chambre, historique de comptages) n'existent pas dans l'app.

**Décision :** le module tourne sur ce jeu de démonstration, pas sur les vraies
données patient. L'UI affichera un label discret **« données de démonstration »**
pour rester honnête vis-à-vis du jury.

## Principe directeur

Les deux modèles `.pkl` **effectuent une vraie inférence live** côté backend, mais sur
des **petits fichiers de features pré-calculés** (et non le CSV de 8 Mo agrégé à chaque
requête). On obtient : IA réellement exécutée, repo léger, réponses rapides, démo
robuste.

## Architecture

### Backend — nouveau module `backend/app/ai/`

```
backend/app/ai/
├── __init__.py
├── models/                       # commités (~250 Ko)
│   ├── affluence_neural_network.pkl
│   ├── affluence_scaler.pkl
│   ├── fraud_isolation_forest.pkl
│   └── fraud_scaler.pkl
├── data/                         # petits CSV pré-calculés, commités
│   ├── affluence_history.csv     # ~90 derniers jours agrégés (~2 Ko)
│   └── fraud_features.csv         # agrégats par patient
├── prep_ai_data.py               # script one-shot, NON lancé en prod
├── engine.py                     # chargement + inférence + cache mémoire
└── router.py                     # endpoints FastAPI
```

- **`prep_ai_data.py`** : lit le gros CSV Kaggle (gardé hors git, dans le zip
  d'origine) et génère `affluence_history.csv` et `fraud_features.csv`. Reproductible
  mais exécuté une seule fois par le dev. Le chemin du CSV source est passé en argument
  ou lu depuis une variable d'environnement ; le script échoue proprement s'il est
  absent.
- **`engine.py`** : charge les 4 `.pkl` et les 2 CSV **une fois au démarrage**
  (singleton module). Expose :
  - `predict_affluence() -> dict` : reconstruit les features des 30 prochains jours à
    partir de `affluence_history.csv`, applique le scaler + le MLP, renvoie historique
    récent + prévision. Résultat mis en cache mémoire (déterministe).
  - `detect_fraud() -> dict` : applique le scaler + l'IsolationForest sur
    `fraud_features.csv`, renvoie les patients marqués anormaux triés par score
    croissant (plus anormal en tête). Cache mémoire.
- **`router.py`** : deux endpoints protégés par JWT (`get_current_user`) :
  - `GET /ai/affluence`
  - `GET /ai/fraud`
- Enregistré dans `backend/app/main.py` via `app.include_router(ai.router)`.

### Contrats d'API

`GET /ai/affluence` →
```json
{
  "history": [ { "date": "2024-05-01", "patients": 28 }, ... ],
  "forecast": [ { "date": "2024-05-08", "predicted_patients": 27 }, ... ],
  "kpis": { "peak": 34, "peak_date": "2024-05-20", "average": 26 }
}
```

`GET /ai/fraud` →
```json
{
  "total": 42,
  "suspects": [
    { "patient": "Bobby Jackson", "visites": 7, "medecins_distincts": 5,
      "hopitaux_distincts": 4, "medicaments_distincts": 6, "score": -0.18 },
    ...
  ]
}
```

(`patient` = nom anonymisé/tronqué du dataset de démo ; pas d'ID Dara Manqué réel.)

### Dépendances backend

Ajouter à `backend/requirements.txt` : `scikit-learn`, `joblib`, `pandas`, `numpy`
(versions compatibles avec les `.pkl` fournis — voir `requirements.txt` du zip :
`scikit-learn>=1.5.0`, `joblib>=1.4.0`, `pandas>=2.2.0`).

### Frontend — React + Vite

- Nouvelle page `web/src/pages/analytics/AnalyticsPage.tsx`, route `/analytics`
  (protégée par `ProtectedRoute`), lien ajouté dans `AppShell`.
- Ajout de la dépendance **Recharts**.
- **Section Affluence** : `LineChart` historique + prévision (zone de prévision
  distinguée visuellement), 2-3 KPI (pic prévu + date, moyenne).
- **Section Fraude** : tableau des patients suspects avec badge de score
  (rouge/orange selon sévérité) + compteur « X patients à vérifier ».
- Appels via le client axios existant (`web/src/api/client.ts`), types ajoutés dans
  `web/src/api/types.ts`. Le token JWT est déjà injecté par le client.
- Label discret **« données de démonstration »** visible dans la page.

## Accès / rôles

Les deux endpoints sont ouverts à **tout utilisateur authentifié** (médecin +
pharmacien). Pas de rôle dédié — suffisant pour la démo.

## Gestion des erreurs

- Si un `.pkl` ou un CSV est manquant au démarrage, `engine.py` lève une erreur claire
  au chargement (fail-fast) plutôt que de renvoyer des données silencieusement fausses.
- Les endpoints renvoient 500 avec un message explicite si l'inférence échoue ; le
  frontend affiche un état d'erreur (« module IA indisponible ») plutôt qu'une page
  cassée.
- `prep_ai_data.py` échoue proprement avec un message si le CSV source est absent.

## Tests

- **Backend** `backend/tests/test_ai.py` :
  - `engine` charge modèles + CSV sans crash.
  - `predict_affluence()` renvoie 30 points de prévision + KPI cohérents.
  - `detect_fraud()` renvoie une liste triée par score.
  - `GET /ai/affluence` et `GET /ai/fraud` → 200 avec la forme attendue (avec auth).
  - Sans token → 401/403.
- **Vérification manuelle** : lancer le backend (port 9000), ouvrir `/analytics`,
  confirmer que les deux graphiques sont peuplés et le label présent.

## Décisions actées

- Objectif : démo qui impressionne le jury (vs rigueur clinique).
- Forme : intégré dans l'app React existante (vs Streamlit séparé).
- 2 modèles soignés : Affluence + Fraude (vs les 3, vs 1 seul).
- Lib graphes : Recharts.
- Label « données de démonstration » conservé.
- Le gros CSV Kaggle (8 Mo) et le modèle réadmission (105 Mo) ne sont **pas** commités.
