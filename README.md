Voici une proposition complète de `README.md` structurée pour servir de véritable fil conducteur à la réalisation de votre application "Dara Manqué". Les choix technologiques proposés s'inscrivent parfaitement dans une architecture distribuée moderne, robuste et taillée pour un projet de cette envergure.

---

# 🏥 Dara Manqué — Smart Health Card

## 📖 Contexte et Description

**Dara Manqué** est une implémentation spécifique et innovante du projet transversal. Ce système dématérialise complètement le carnet de santé traditionnel en le remplaçant par une carte NFC intelligente.

Chaque carte est liée de manière unique à un patient, agissant comme une clé d'accès sécurisée. Pour des raisons de sécurité et de fiabilité, aucune donnée médicale n'est stockée sur la carte physique ; l'ensemble des dossiers, historiques et ordonnances réside de manière sécurisée sur une base de données côté serveur. Le système fait le pont entre les technologies monétiques (paiement NFC), la cybersécurité (chiffrement) et la gestion des systèmes d'information hospitaliers.

## 👥 Acteurs et Fonctionnalités Clés

### 1. Le Patient (Utilisateur Mobile)

* Dispose de la carte NFC personnelle.
* 
**Application Mobile :** Permet de scanner sa propre carte avec son smartphone pour consulter son historique de consultations, ses ordonnances en cours, le solde de son porte-monnaie électronique et ses prochains rendez-vous.



### 2. Le Médecin (Utilisateur Web)

* 
**Application Web :** Se connecte avec son compte après qu'un patient a scanné sa carte sur le lecteur.


* Accède au dossier médical complet : historique, maladies chroniques, allergies, anciennes ordonnances.


* Rédige de nouvelles ordonnances numériques et planifie des rendez-vous.



### 3. Le Pharmacien (Utilisateur Web)

* 
**Application Web :** Accède uniquement aux ordonnances actives du patient.


* Encaisse le paiement des médicaments via la fonctionnalité de paiement NFC de la carte.


* Marque l'ordonnance comme "traitée" pour empêcher toute double utilisation.



---

## 🛠️ Stack Technologique Recommandée

Pour répondre aux exigences de sécurité, de performance et pour adopter une architecture distribuée (Backend API / Frontend Web / Frontend Mobile), voici la stack moderne recommandée :

### Backend (API REST & Logique Métier)

* **Framework :** **Spring Boot (Java)**. Excellent pour la sécurité, la gestion des transactions complexes et l'intégration d'architectures robustes.
* **Base de données :** **MongoDB Atlas** (pour la flexibilité des dossiers médicaux sous forme de documents) ou **PostgreSQL** (pour les transactions financières et la gestion stricte des relations).
* 
**Sécurité :** Spring Security avec JWT (JSON Web Tokens) pour l'authentification des requêtes, couplé à un chiffrement AES pour les données sensibles.



### Frontend (Interfaces Utilisateurs)

* **Portail Web (Médecins & Pharmaciens) :** **Angular**. Framework idéal pour les applications d'entreprise et les tableaux de bord de gestion complexes.
* **Application Mobile (Patients) :** **Flutter**. Permet de compiler une application native performante (iOS/Android) avec une excellente gestion du module NFC du smartphone.

### Infrastructure & DevOps

* **Conteneurisation :** **Docker** (pour isoler l'API et la base de données) et **Kubernetes** pour l'orchestration si le système évolue à grande échelle.
* **Hébergement & CI/CD :** **Vercel** (pour le frontend Angular), **Render** ou une VM cloud (pour le backend Spring Boot).
* **Qualité de code :** **SonarCloud** pour l'analyse continue des vulnérabilités de sécurité et de la qualité du code.

---

## 🗺️ Ligne Directrice d'Implémentation (Roadmap)

Ce projet se divise en plusieurs phases d'implémentation logique :

### Phase 1 : Conception & Architecture 

1. Mise en place des dépôts Git (Backend, Frontend Web, Frontend Mobile).
2. Configuration des environnements de développement et de la base de données.
3. Modélisation finale de la base de données (entités : Patient, Médecin, Pharmacien, Ordonnance, Rendez-vous) à partir du diagramme de classes.

### Phase 2 : Core Backend & API 

1. Développement de l'API REST avec Spring Boot.
2. Mise en place de l'authentification (Médecins / Pharmaciens).
3. Création des endpoints de gestion : CRUD pour les dossiers médicaux, création d'ordonnances, validation de paiement.
4. Implémentation de la logique d'invalidation des ordonnances (statut actif/inactif).



### Phase 3 : Interfaces Web & Mobile

1. **Dashboard Angular :** Création des vues Médecin (consultation dossier, formulaire d'ordonnance) et Pharmacien (liste ordonnances actives, bouton d'encaissement).
2. 
**App Flutter :** Création de l'interface patient (Historique, RDV, Solde).



### Phase 4 : Intégration NFC & Sécurité

1. Intégration de la lecture NFC côté Frontend (Web via lecteur externe, Mobile via lecteur natif du téléphone).
2. Liaison de l'UID (identifiant unique) de la carte NFC au backend pour déclencher l'interface de connexion.


3. Tests de sécurité (protection contre le clonage et les attaques de rejeu).



---

## 🧠 Note sur l'Intelligence Artificielle (Hors Périmètre App Core)

Conformément à l'architecture du système, les modules d'Intelligence Artificielle requis (Détection de fraude via *Isolation Forest*, Analyse comportementale via *Random Forest*, et Prédiction d'affluence via *Réseau de neurones*)  sont **découplés** de l'application principale.

Leur implémentation dépend de l'entraînement de modèles spécifiques (généralement en Python/TensorFlow). L'application web/mobile se contentera d'envoyer et de recevoir des données de ces modèles via des points d'API dédiés (ex: une alerte si l'API IA renvoie une anomalie lors d'une transaction), sans avoir à gérer la logique d'entraînement en interne.