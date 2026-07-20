# Dara Manqué : une plateforme de carte médicale intelligente combinant NFC réel et intelligence artificielle

**[Noms des auteurs]**, *[Établissement]*

---

**Résumé —** Au Sénégal comme dans de nombreux pays, le dossier médical du patient reste
fragmenté, majoritairement sur support papier (carnet de santé), ce qui complique la
continuité des soins, la prévention des accidents allergiques et la lutte contre le
nomadisme médical. Cet article présente *Dara Manqué*, une plateforme de carte médicale
intelligente qui remplace le carnet papier par une carte NFC agissant comme clé d'accès
sécurisée à un dossier centralisé côté serveur. La solution s'articule autour d'un backend
FastAPI/PostgreSQL, d'un portail web React (médecin et pharmacien), d'une application mobile
(patient) et d'un lecteur matériel NFC (ESP32 + module RC522) qui lit l'identifiant unique
(UID) intrinsèque d'une carte physique et le transmet au backend. Quatre axes de
différenciation guident le projet : (1) une carte NFC réelle et matérielle ; (2) une alerte
d'allergie assistée par un moteur de cross-réactivité médicament-allergie ; (3) un mode
d'urgence hors-ligne ; (4) une ordonnance signée à usage unique. Un module « Analytics IA »
en cours d'intégration expose deux modèles scikit-learn pré-entraînés — prévision d'affluence
hospitalière (réseau de neurones) et détection de nomadisme médical (Isolation Forest). Les
données alimentant ces modèles proviennent d'un jeu de démonstration synthétique et non de
données patient réelles.

**Termes d'indexation —** apprentissage automatique, carte médicale, détection d'anomalies,
FastAPI, Isolation Forest, NFC, RC522, santé numérique, scikit-learn.

---

## I. Introduction

Dans le contexte sanitaire sénégalais et plus largement ouest-africain, le suivi médical
d'un patient repose encore largement sur le carnet de santé papier. Ce support présente
plusieurs limites structurelles : il est facilement perdu ou détérioré, il n'est pas
consultable à distance, il fragmente l'historique du patient entre plusieurs praticiens et
établissements, et il n'offre aucun garde-fou automatique contre les erreurs de prescription.
Ces limites ont des conséquences directes : accidents allergiques évitables, redondance
d'examens, difficulté à reconstituer un dossier en situation d'urgence, et nomadisme médical
(un même patient multipliant les consultations et prescriptions auprès de praticiens
distincts sans coordination).

*Dara Manqué* propose de remplacer le carnet papier par une **carte médicale intelligente**.
La carte n'héberge pas les données médicales : elle agit comme une **clé d'accès** vers un
dossier centralisé et sécurisé côté serveur. L'ensemble des données cliniques (allergies,
maladies chroniques, consultations, ordonnances) réside dans une base de données unique,
accessible par les professionnels de santé autorisés.

Les contributions de ce travail sont les suivantes :

1. Une architecture complète et fonctionnelle (backend, web, mobile, matériel) autour d'une
   carte physique dont l'UID NFC sert d'identifiant.
2. Un lecteur matériel réel (ESP32 + RC522) intégré de bout en bout à la chaîne applicative.
3. Un moteur de détection de conflits médicament-allergie fondé sur des classes de
   cross-réactivité, intégré au flux de prescription.
4. L'amorce d'un module d'analyse par apprentissage automatique (prévision d'affluence et
   détection d'anomalies comportementales).

## II. État de l'art et positionnement

Le projet s'inscrit dans un cadre académique où une équipe concurrente développe un cahier
des charges identique. Le positionnement de *Dara Manqué* consiste donc à se différencier non
par le périmètre fonctionnel de base (dossier médical en ligne), mais par la profondeur
technique et l'innovation perçue. Là où une solution concurrente se limite à un « carnet de
santé en ligne », *Dara Manqué* vise une carte physique réelle, fonctionnant potentiellement
hors-ligne, difficilement falsifiable et augmentée d'intelligence artificielle.

Quatre axes de différenciation structurent cette ambition :

- **Axe 1 — Carte NFC réelle (livré).** Plutôt que de simuler la carte par un simple
  identifiant numérique, la solution s'appuie sur un lecteur matériel qui lit l'UID d'usine
  d'une carte RFID 13,56 MHz (norme ISO/IEC 14443).
- **Axe 2 — Alerte allergie assistée (livré).** Un moteur de cross-réactivité bloque les
  prescriptions en conflit avec les allergies connues du patient.
- **Axe 3 — Urgence hors-ligne « break glass » (prévu).** Un instantané chiffré et signé
  (groupe sanguin, allergies, maladies chroniques) serait lisible sur la carte sans réseau.
- **Axe 4 — Ordonnance signée à usage unique (prévu).** Le médecin signe l'ordonnance, le
  pharmacien la « brûle » à la délivrance ; toute réutilisation ou falsification est rejetée
  cryptographiquement.

Les axes 1 et 2 sont implémentés et démontrables ; les axes 3 et 4 sont conçus mais non
encore développés.

## III. Architecture du système

*Dara Manqué* adopte une architecture répartie en quatre composants complémentaires.

**A. Backend — FastAPI et PostgreSQL.**
Le cœur applicatif est une API REST développée en Python 3.12 avec FastAPI, adossée à une
base PostgreSQL via l'ORM SQLAlchemy 2.0 et gérée en versions par Alembic. Le schéma de
données repose sur quatre entités principales : `users` (médecins et pharmaciens),
`patients` (dont la colonne `card_uid`, unique et indexée, porte l'UID de la carte),
`consultations` et `prescriptions`. L'authentification des professionnels s'appuie sur des
jetons JWT signés (python-jose) et un hachage de mot de passe bcrypt (passlib).

**B. Portail web — React.**
Un portail React 19 (TypeScript, Vite) sert les interfaces médecin et pharmacien : recherche
et consultation du dossier patient, création de prescriptions avec alerte d'allergie en
temps réel, et suivi/traitement des ordonnances. Une borne de lecture de carte
(« CardStation ») intégrée au tableau de bord médecin interroge périodiquement le backend
pour réagir aux cartes présentées sur le lecteur physique.

**C. Application mobile — patient.**
Une application mobile (Flutter) permet au patient de s'identifier par l'UID de sa carte et
de consulter ses prescriptions et consultations.

**D. Matériel — lecteur NFC ESP32 + RC522.**
Un microcontrôleur ESP32 piloté par un module RFID RC522 (13,56 MHz) lit l'UID intrinsèque
de la carte lorsqu'elle est posée. Un pont série (`serial_bridge.py`) lit l'UID sur le port
USB et le transmet au backend. Aucune donnée n'est gravée sur la carte : l'UID d'usine
suffit à l'identifier.

**Flux « carte scannée → dossier patient ».** La chaîne de bout en bout se déroule ainsi :
la carte est approchée du lecteur → l'ESP32 lit l'UID et l'imprime sur le port série
(`UID:<HEX>`) → le pont série effectue un `POST /cards/scan` → le backend normalise l'UID
(forme compacte majuscule, via `normalize_uid`), le résout en patient et enregistre le
scan dans un tampon mémoire (`scan_state`) muni d'un compteur `seq` → le tableau de bord web
interroge `GET /cards/last-scan` et, lorsque `seq` change, ouvre le dossier du patient
(carte connue) ou un formulaire d'enrôlement pré-rempli avec l'UID (carte inconnue).

## IV. Fonctionnalités clés

**A. Carte NFC réelle.**
Le modèle de données retient l'UID comme attribut du patient (`patients.card_uid`) et non
comme clé primaire : l'identifiant entier interne reste stable et l'UID reste optionnel et
unique. La normalisation d'UID (`card_utils.normalize_uid`) tolère les différentes formes
textuelles produites par le lecteur (majuscules/minuscules, séparateurs `:`, `-`, espaces),
si bien qu'une carte enrôlée une fois est toujours reconnue par la suite. L'endpoint
`POST /cards/scan` est public (appelé par le matériel) et l'endpoint `POST /patients`,
protégé (`require_doctor`), réalise l'enrôlement d'un patient avec son UID (le médecin est
l'émetteur de carte). La chaîne complète a été validée avec une carte physique réelle
(UID de test `237F4506`).

**B. Alerte allergie assistée par règles de cross-réactivité.**
Le module `allergy_rules.py` implémente un moteur de détection de conflits
médicament-allergie. Il regroupe les substances en **classes d'allergènes** (par exemple
Pénicilline : amoxicilline, ampicilline, Augmentin… ; Aspirine/AINS ; Sulfamides ;
Céphalosporines ; Codéine ; Iode). La cross-réactivité émerge naturellement de ce modèle :
allergie et médicament n'ont qu'à correspondre à la même classe. La comparaison s'effectue
sur texte normalisé (minuscules, accents retirés, ponctuation neutralisée) et par
correspondance de mots entiers, ce qui gère les termes multi-mots.

Ce moteur est intégré au flux de prescription. Un endpoint de vérification en temps réel
(`POST /patients/{id}/prescriptions/check`) alimente le formulaire web, qui affiche un
bandeau d'alerte dès qu'un conflit est détecté. La création d'ordonnance
(`POST /patients/{id}/prescriptions`) est **durcie** : en cas de conflit non confirmé, le
serveur renvoie une erreur HTTP 409 ; le médecin peut passer outre explicitement
(`override_allergy`), auquel cas la décision est **tracée** dans une colonne d'audit
(`allergy_override`, migration Alembic dédiée). Scénario de démonstration : un patient
allergique à la pénicilline se voit prescrire de l'amoxicilline → l'alerte se déclenche.

**C. Module « Analytics IA » (en cours d'intégration).**
Un module d'analyse par apprentissage automatique est conçu et planifié pour exposer deux
modèles scikit-learn pré-entraînés, choisis pour leur autonomie et leur lisibilité visuelle :

- **Prévision d'affluence hospitalière** — un réseau de neurones `MLPRegressor` associé à un
  `StandardScaler` prédit le nombre de patients pour les 30 prochains jours. Les
  caractéristiques (features) sont temporelles : jour de la semaine, mois, jour, indicateur
  de week-end, saison, moyenne mobile à 7 jours et retards (lags) à 1, 3 et 7 jours.
- **Détection de fraude / nomadisme médical** — un `IsolationForest` associé à un
  `StandardScaler` repère les patients au comportement atypique à partir de quatre
  caractéristiques agrégées : nombre de visites, nombres distincts de médecins, d'hôpitaux et
  de médicaments. Les patients marqués comme anomalies sont classés par score croissant (le
  plus anormal en tête).

Côté backend, un module `app/ai/` charge les modèles `.pkl` et de petits fichiers de
features pré-calculés une seule fois au démarrage (cache mémoire) et expose deux endpoints
protégés par JWT : `GET /ai/affluence` et `GET /ai/fraud`. Côté web, une page « Analytics IA »
affiche la courbe historique + prévision et le tableau des patients suspects à l'aide de la
bibliothèque de graphiques Recharts.

## V. Implémentation et choix techniques

La pile technique privilégie des technologies éprouvées et productives : FastAPI pour la
génération automatique de la documentation OpenAPI et la validation par Pydantic ;
SQLAlchemy 2.0 et Alembic pour la persistance et les migrations versionnées (création des
tables initiales, ajout de la colonne d'audit d'allergie, ajout de `card_uid`) ; React 19 +
TypeScript + Vite côté web ; Flutter côté mobile.

La **sécurité** repose sur JWT : à la connexion (`POST /auth/login`), le backend délivre un
jeton signé porteur du rôle, exigé ensuite par les endpoints protégés (dépendances
`get_current_user`, `require_doctor`). Le hachage des mots de passe utilise bcrypt.

Le **pont matériel/écran** est volontairement simple : un tampon mémoire mono-processus
(`scan_state`) muni d'un compteur monotone `seq` relie le lecteur (qui écrit) et l'écran
(qui interroge). Ce choix, adapté à une démonstration mono-poste, serait remplacé par un
stockage partagé (Redis ou table dédiée) en déploiement multi-postes.

L'**intégration des modèles** privilégie une inférence réelle mais frugale : les modèles
`.pkl` effectuent une vraie prédiction, mais sur de petits fichiers de features pré-calculés
plutôt que sur le jeu de données brut agrégé à chaque requête. La version de scikit-learn est
épinglée (1.9.0) pour garantir la dé-sérialisation des modèles. Les artefacts lourds (jeu de
données brut de plusieurs mégaoctets, modèle de réadmission de 105 Mo) ne sont pas versionnés.

La **qualité** est soutenue par une suite de tests pytest côté backend (plus de quarante
tests couvrant l'authentification, les patients, les prescriptions, les cartes et le moteur
d'allergie).

## VI. Résultats et démonstration

Les éléments suivants sont fonctionnels et démontrables :

- **Chaîne NFC matérielle complète** : une carte physique réelle, lue par l'ESP32 + RC522,
  déclenche via le pont série l'ouverture du dossier patient (ou du formulaire d'enrôlement)
  sur le portail web, sans intervention manuelle.
- **API REST** documentée (Swagger/OpenAPI) exposant l'authentification, les dossiers
  patients, les consultations, les prescriptions et les endpoints de carte.
- **Alerte d'allergie en temps réel** dans le formulaire de prescription, avec blocage 409 et
  audit de la dérogation.
- **Module Analytics IA** conçu et planifié : endpoints `/ai/affluence` et `/ai/fraud` et
  page web avec graphiques Recharts (historique + prévision, tableau des suspects).

Pour la démonstration sans matériel, un simulateur (`sim_card.py`) rejoue les scénarios de
carte connue et de carte inconnue.

## VII. Limites et travaux futurs

Plusieurs limites sont assumées à ce stade, cohérentes avec un projet académique de
démonstration :

- **Données de l'IA synthétiques.** Les modèles d'affluence et de fraude ont été entraînés
  sur un jeu de données Kaggle **synthétique** (colonnes anglaises : nom, âge, montant de
  facturation, numéro de chambre…) qui **ne correspond pas** au schéma réel de *Dara Manqué*.
  Le module tourne donc sur un **jeu de démonstration**, et non sur de vraies données patient ;
  l'interface l'indique explicitement par un label « données de démonstration ». Aucune
  métrique de performance clinique n'est revendiquée ; toute valeur affichée est indicative.
- **Posture de sécurité de démonstration.** Certains endpoints (scan de carte, lecture de
  dossier) sont volontairement non authentifiés pour la démonstration ; un durcissement (clé
  device partagée, authentification des lectures de dossier, limitation de débit
  anti-énumération, cookies `httpOnly`) est nécessaire avant tout usage réel.
- **Axes 3 et 4 non réalisés.** Le mode d'urgence hors-ligne et l'ordonnance signée à usage
  unique restent à l'état de conception.
- **Relation médecin-patient non contrainte** et absence d'authentification patient dans le
  périmètre actuel.

Les travaux futurs porteront sur le ré-entraînement des modèles sur un schéma représentatif,
la mise en œuvre des axes 3 et 4, l'extension du moteur d'interactions aux couples
médicament-médicament, et le durcissement de sécurité.

## VIII. Conclusion

*Dara Manqué* démontre qu'une carte médicale intelligente réellement matérielle, couplée à un
dossier centralisé et à des garde-fous cliniques automatiques, est atteignable avec une pile
open source moderne. La chaîne NFC de bout en bout et l'alerte d'allergie assistée
constituent des différenciateurs concrets et démontrables, tandis que le module Analytics IA
illustre la valeur ajoutée de l'apprentissage automatique pour la planification hospitalière
et la détection du nomadisme médical. En restant transparent sur la nature de démonstration
des données d'IA et sur la posture de sécurité provisoire, le projet trace une trajectoire
claire vers une solution déployable.

## Références

[1] S. Ramírez, « FastAPI », documentation officielle. [En ligne]. Disponible :
https://fastapi.tiangolo.com

[2] F. Pedregosa *et al.*, « Scikit-learn: Machine Learning in Python », *Journal of Machine
Learning Research*, vol. 12, p. 2825–2830, 2011.

[3] F. T. Liu, K. M. Ting et Z.-H. Zhou, « Isolation Forest », in *Proc. 8th IEEE
International Conference on Data Mining (ICDM)*, 2008, p. 413–422.

[4] Meta Open Source, « React – A JavaScript library for building user interfaces ».
[En ligne]. Disponible : https://react.dev

[5] The SQLAlchemy authors, « SQLAlchemy – The Python SQL Toolkit and Object Relational
Mapper ». [En ligne]. Disponible : https://www.sqlalchemy.org

[6] ISO/IEC 14443, *Cards and security devices for personal identification — Contactless
proximity objects*, International Organization for Standardization, Genève, Suisse.

[7] The PostgreSQL Global Development Group, « PostgreSQL: The World's Most Advanced Open
Source Relational Database ». [En ligne]. Disponible : https://www.postgresql.org

[8] NXP Semiconductors, « MFRC522 — Standard performance MIFARE and NTAG frontend »,
fiche technique, 2016.

[9] Espressif Systems, « ESP32 Series Datasheet ». [En ligne]. Disponible :
https://www.espressif.com

[10] D. E. Rumelhart, G. E. Hinton et R. J. Williams, « Learning representations by
back-propagating errors », *Nature*, vol. 323, p. 533–536, 1986.

[11] Google, « Flutter – Build apps for any screen ». [En ligne]. Disponible :
https://flutter.dev
