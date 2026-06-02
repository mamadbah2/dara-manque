# Dara Manqué — MVP Design Spec

**Date :** 2026-06-02  
**Statut :** Approuvé

---

## Contexte

Dara Manqué dématérialise le carnet de santé traditionnel via une carte NFC liée à un patient. Pour le MVP, la carte NFC est simulée par un **identifiant numérique patient**. Aucune donnée médicale n'est stockée sur la carte ; tout réside côté serveur.

---

## Acteurs & Fonctionnalités MVP

### Patient (Flutter mobile)
- Saisir son ID numérique pour s'identifier
- Voir ses ordonnances actives
- Voir son historique de consultations

### Médecin (React web)
- Se connecter (email / mot de passe)
- Rechercher un patient par son ID
- Voir le dossier médical complet (infos, allergies, maladies chroniques, historique consultations)
- Créer une nouvelle ordonnance

### Pharmacien (React web)
- Se connecter (email / mot de passe)
- Rechercher un patient par son ID
- Voir les ordonnances actives du patient
- Marquer une ordonnance comme "traitée" (invalidation)

---

## Stack Technologique

| Couche | Technologie |
|---|---|
| Backend | FastAPI (Python) + PostgreSQL |
| ORM | SQLAlchemy + Alembic (migrations) |
| Auth | JWT (python-jose) |
| Web frontend | React + Vite (TypeScript) |
| Mobile | Flutter |
| Scaffolding | CLI officiels uniquement (pas de boilerplate manuel) |

**Règle de scaffolding :** utiliser exclusivement les commandes officielles des frameworks (`fastapi`, `npm create vite@latest`, `flutter create`) pour initialiser les projets.

---

## Architecture

```
dara-manque/
├── backend/          # FastAPI + PostgreSQL
├── web/              # React + Vite (Médecin & Pharmacien)
└── mobile/           # Flutter (Patient)
```

Trois projets indépendants. Le backend expose une API REST consommée par le web et le mobile.

---

## Modèle de données

### `users`
| Champ | Type | Notes |
|---|---|---|
| id | UUID | PK |
| email | VARCHAR | unique |
| password_hash | VARCHAR | bcrypt |
| role | ENUM | `doctor` / `pharmacist` |
| full_name | VARCHAR | |

### `patients`
| Champ | Type | Notes |
|---|---|---|
| id | INTEGER | PK, numéro affiché sur la carte |
| full_name | VARCHAR | |
| date_of_birth | DATE | |
| allergies | TEXT | |
| chronic_conditions | TEXT | |

### `consultations`
| Champ | Type | Notes |
|---|---|---|
| id | UUID | PK |
| patient_id | INTEGER | FK → patients |
| doctor_id | UUID | FK → users |
| date | TIMESTAMP | |
| notes | TEXT | |
| diagnosis | VARCHAR | |

### `prescriptions`
| Champ | Type | Notes |
|---|---|---|
| id | UUID | PK |
| patient_id | INTEGER | FK → patients |
| doctor_id | UUID | FK → users |
| created_at | TIMESTAMP | |
| medications | TEXT | liste libre pour MVP |
| status | ENUM | `active` / `treated` |

---

## API REST

### Auth
| Méthode | Route | Rôle | Description |
|---|---|---|---|
| POST | `/auth/login` | Public | Connexion, retourne JWT |

### Patients
| Méthode | Route | Rôle | Description |
|---|---|---|---|
| GET | `/patients/{id}` | Doctor / Pharmacist | Dossier patient |
| GET | `/patients/{id}/consultations` | Doctor | Historique consultations |
| GET | `/patients/{id}/prescriptions` | Doctor / Pharmacist | Ordonnances actives |
| POST | `/patients/{id}/prescriptions` | Doctor | Créer une ordonnance |
| PATCH | `/prescriptions/{id}/treat` | Pharmacist | Marquer comme traitée |

### Mobile (pas d'auth)
| Méthode | Route | Description |
|---|---|---|
| GET | `/patients/{id}` | Dossier simplifié pour patient |
| GET | `/patients/{id}/prescriptions` | Ordonnances actives |
| GET | `/patients/{id}/consultations` | Historique |

---

## Sécurité MVP

- Mots de passe hashés avec **bcrypt**
- JWT avec expiration (24h)
- Vérification du rôle sur chaque endpoint protégé (Doctor vs Pharmacist)
- Le patient n'a pas de compte — accès en lecture seule par ID uniquement

---

## Hors périmètre MVP

- Carte NFC physique (remplacée par ID numérique)
- Porte-monnaie électronique et paiement
- Gestion des rendez-vous
- Modules IA (fraude, comportement, prédiction)
- Déploiement cloud / Docker
- Tests automatisés
