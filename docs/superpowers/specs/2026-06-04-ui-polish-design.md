# Design Spec — UI Polish Dara Manqué

**Date:** 2026-06-04  
**Périmètre:** Web (React/Vite) + Mobile (Flutter) — présentation uniquement, aucun changement d'API

---

## 1. Identité visuelle commune

### Palette
| Token | Hex | Usage |
|---|---|---|
| `--primary` | `#0D9488` | Boutons, liens actifs, logo |
| `--primary-dark` | `#0F766E` | Hover/focus boutons |
| `--bg` | `#F0FAF7` | Fond global pages |
| `--surface` | `#FFFFFF` | Cartes, header |
| `--text` | `#1E293B` | Texte principal |
| `--text-muted` | `#64748B` | Labels, méta-données |
| `--border` | `#E2E8F0` | Bordures inputs/cartes |
| `--success` | `#16A34A` | Badge "Traitée" |
| `--warning` | `#D97706` | Badge "Active" |
| `--danger` | `#DC2626` | Messages d'erreur |

### Typographie (web)
- Font : `Inter` chargée via Google Fonts (fallback `system-ui, sans-serif`)
- Hiérarchie : titres `600`, corps `400`, labels `500`

### Composants partagés
- **Cartes** : `background #fff`, `border-radius 12px`, `box-shadow 0 1px 3px rgba(0,0,0,0.1), 0 4px 16px rgba(0,0,0,0.06)`, `padding 24px`
- **Badges de statut** : pill inline — `background` teinté + `color` saturé + `font-weight 600 font-size 12px`
- **Boutons primaires** : `background var(--primary)`, blanc, `border-radius 8px`, `padding 10px 20px`, hover `var(--primary-dark)`, transition douce
- **Inputs** : border `var(--border)`, `border-radius 8px`, focus ring `var(--primary)`, `padding 10px 14px`

---

## 2. Web — 5 pages

### 2.1 `index.css` (design system)
Remplacer le fichier actuel (4 lignes) par :
- Import Google Fonts Inter
- Variables CSS (palette complète)
- Classe `.card`, `.btn`, `.btn-outline`, `.badge`, `.badge-active`, `.badge-treated`, `.form-group`, `.alert-error`, `.avatar`
- Reset minimal + body/heading defaults

### 2.2 LoginPage
- Layout : `min-height: 100vh`, fond `var(--bg)`, carte centrée max-width 400px
- Logo en haut de carte : ✚ en teal + "Dara Manqué" semi-bold + sous-titre "Portail professionnel"
- Erreur inline en encart rouge doux (background `#FEF2F2`, bordure gauche rouge)
- Hint discret en bas de carte : credentials de démo (utile en présentation)
- Bouton plein "Se connecter" + état loading

### 2.3 AppShell (nouveau composant `src/components/AppShell.tsx`)
Header sticky blanc, shadow douce :
- Gauche : logo ✚ teal + "Dara Manqué"
- Droite : rôle traduit (Médecin / Pharmacien) + email en gris + bouton "Déconnexion" outline
- `<main>` slot : padding `24px`, max-width 1100px, centré

Toutes les pages authentifiées l'utilisent comme wrapper.

### 2.4 DoctorDashboard
- Carte de recherche centrée, icône loupe, input "N° de carte patient" + bouton "Rechercher"
- État erreur (patient introuvable) : encart doux avec message et icône
- État chargement : spinner inline dans le bouton

### 2.5 PatientRecord
- En-tête : avatar initiales (2 lettres, cercle teal), nom, badge âge, badge groupe sanguin
- Deux sections cartes côte à côte (ou empilées sur petit écran) : "Consultations" et "Prescriptions actives"
- Chaque consultation : date en gris + motif + notes
- Chaque prescription : médicament + badge statut coloré
- Bouton "Nouvelle ordonnance" en bas (ouvre PrescriptionForm)

### 2.6 PrescriptionForm
- Formulaire en carte, champs "Médicament" et "Instructions" groupés avec labels
- Bouton "Créer l'ordonnance" plein
- Succès : encart vert avec message, redirect automatique après 1,5s

### 2.7 PharmacistDashboard
- Même carte de recherche que Doctor
- Liste des prescriptions actives : card par prescription, médicament en semi-bold, badge "Active" ambre, bouton "Marquer traitée" outline
- Transition : après traitement, badge passe à "Traitée" vert + bouton disparaît (état optimiste avec rollback)

---

## 3. Mobile — 4 écrans

### 3.1 Thème global (`main.dart`)
```
ColorScheme.fromSeed(seedColor: Color(0xFF0D9488))
useMaterial3: true
```
Polices : par défaut Material 3 (Roboto/Noto).

### 3.2 IdEntryScreen — Carte NFC stylisée
Remplacement de la saisie brute par :
- **Widget carte** (Container décoré) : dégradé teal `#0D9488` → `#0F766E`, border-radius 16, largeur 300px, hauteur 180px (ratio carte de crédit), puce ▭ dorée simulée en haut-gauche, "Dara Manqué" en blanc, "CARTE SANTÉ NUMÉRIQUE" sous-titre, numéro masqué `••••` qui se remplace dynamiquement par les chiffres saisis
- Champ de saisie classique en dessous (label, style teal)
- Bouton "Accéder à mon carnet de santé" plein teal, large
- Fond clair `#F0FAF7`

### 3.3 HomeScreen
- `AppBar` sans élévation, couleur fond teal pâle, titre "Mon carnet de santé"
- Carte patient en haut : initiales (Avatar), nom, chips âge et groupe sanguin
- Deux `InkWell` / `Card` de navigation : "Mes ordonnances" (icône `local_pharmacy`) et "Mes consultations" (icône `medical_services`), avec chevron et sous-titre

### 3.4 PrescriptionsScreen & ConsultationsScreen
- `AppBar` avec bouton retour
- `ListView.builder` avec cartes Material 3 (`Card` avec `CardTheme`)
- Prescription : médicament en bold, instructions en gris, `Chip` de statut coloré (vert/ambre)
- Consultation : date + motif + notes
- État vide illustré : icône grande + texte centré "Aucune ordonnance active" / "Aucune consultation"

---

## 4. Contraintes d'implémentation

- **Aucun changement de logique** : seules les couches de présentation (JSX + CSS, widgets Flutter) sont modifiées. Toute la logique API, hooks, et state management est inchangée.
- **Pas de nouvelle dépendance NPM** (hors Google Fonts via `<link>` CSS). Pas de nouvelle dépendance Dart pub.
- **Gates de qualité** : `npm run build` doit rester clean, `flutter analyze` doit rester clean.
- **Commits** : un commit web ("style(web): redesign UI avec palette teal") + un commit mobile ("style(mobile): redesign UI Flutter avec carte NFC").

---

## 5. Hors scope

- Changements de logique API ou de routing
- Animations complexes
- Tests visuels automatisés
- Responsive avancé (tablette/desktop large)
- Internationalisation
