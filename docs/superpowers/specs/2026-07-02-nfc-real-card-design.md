# Carte NFC réelle — Design Spec

**Date :** 2026-07-02
**Statut :** En revue
**Axe différenciateur :** #1 « NFC réel » (voir mémoire `project_differentiation`) — priorité 1

---

## Contexte

Aujourd'hui l'app mobile patient (`mobile/`) est un carnet de santé : sur `IdEntryScreen`, on **tape** un numéro de carte (ex. `1001`) → `fetchPatient(id)` → dossier (accueil, consultations, ordonnances). Un visuel de carte NFC purement décoratif existe déjà sur cet écran.

Le groupe concurrent garde l'ID **simulé** (saisie clavier). Le nom du projet, c'est la carte : **celui qui a une vraie carte NFC gagne.** On remplace le geste « taper un numéro » par « approcher une carte physique du téléphone ».

### Démo cible (~15 s)

1. (Une fois) On écrit `1001` sur un sticker NFC via l'écran « Programmer une carte » → on le colle sur une carte plastique « Dara Manqué ».
2. Devant le jury : on approche la carte du dos du téléphone → le dossier de Mamadou Diallo s'ouvre. Eux tapent un numéro ; nous, on scanne une carte.

---

## Décisions de design (validées)

1. **Contenu du tag :** l'**ID patient** écrit en clair sur le tag (record **NDEF texte**, ex. `"1001"`). Le serveur reste source de vérité ; le tag est un pointeur physique. Pas de changement backend.
2. **Le NFC augmente l'écran, ne le remplace pas :** bouton « Scanner ma carte » **+** saisie manuelle conservée en fallback (appareils sans NFC, résilience démo, chemin du mock).
3. **Provisionnement in-app :** petit écran « Programmer une carte » qui écrit l'ID sur un tag. Rend la démo auto-suffisante (pas d'app tierce).
4. **Testabilité par abstraction :** toute la logique passe derrière une interface `CardReader` → testable sans matériel ; seul le geste physique final exige le téléphone.

**Hors périmètre (YAGNI) :** iOS (Android uniquement), changement backend, binding sur l'UID matériel, signature/crypto (c'est l'axe #4 « ordonnance signée »).

---

## 1. Abstraction lecteur — `mobile/lib/nfc/card_reader.dart`

Interface isolée, sans dépendance UI, cœur de la testabilité.

```dart
abstract class CardReader {
  /// true si le matériel NFC est présent et actif.
  Future<bool> isAvailable();

  /// Démarre une session, lit le premier record NDEF texte, renvoie son payload
  /// (ex. "1001"). Lève une exception amicale si tag vide/illisible.
  Future<String> readCardId();

  /// Écrit `id` comme record NDEF texte sur le tag approché.
  Future<void> writeCardId(String id);
}
```

Deux implémentations :

- **`NfcCardReader`** (`mobile/lib/nfc/nfc_card_reader.dart`) — via le package `nfc_manager`. `isAvailable()` → `NfcManager.instance.isAvailable()`. `readCardId()` démarre une session, extrait le message NDEF, décode le premier record texte. `writeCardId()` écrit un `NdefMessage([NdefRecord.createText(id)])`. Session toujours arrêtée (succès ou erreur).
- **`MockCardReader`** (`mobile/lib/nfc/mock_card_reader.dart`) — `isAvailable()` → `true`, `readCardId()` renvoie un ID configurable (défaut `"1001"`) après un court délai, `writeCardId()` = no-op. Sert au dev sur émulateur/desktop et aux tests.

### Sélection du lecteur — `mobile/lib/nfc/card_reader_factory.dart`

```dart
CardReader createCardReader() {
  const useMock = bool.fromEnvironment('USE_MOCK_NFC', defaultValue: false);
  return useMock ? MockCardReader() : NfcCardReader();
}
```

- Prod / téléphone : `NfcCardReader`.
- Dev sans matériel : `flutter run --dart-define=USE_MOCK_NFC=true` → `MockCardReader`.
- Même sans le flag, si `isAvailable()` est `false` (desktop, émulateur), l'UI bascule automatiquement sur la saisie manuelle.

## 2. Parsing — `mobile/lib/nfc/card_id.dart`

Fonction **pure**, testée unitairement :

```dart
int parseCardId(String payload) // trim ; vide → FormatException amicale ;
                                 // non-numérique → FormatException amicale
```

Isolée du NFC pour être testable sans aucune dépendance plateforme.

## 3. Écran de scan — modif de `mobile/lib/screens/id_entry_screen.dart`

- Injecter un `CardReader` (défaut `createCardReader()`), paramètre optionnel du constructeur pour les tests.
- Au `initState` : `isAvailable()` → `_nfcAvailable`.
- Si NFC dispo : bouton **« Scanner ma carte »** proéminent (réutiliser le visuel `_NfcCard` existant, animé pendant la lecture). Au tap : `readCardId()` → `parseCardId()` → `fetchPatient()` → `HomeScreen` (même navigation qu'aujourd'hui).
- Saisie manuelle **conservée** en dessous (fallback + accessibilité). Si NFC indispo : message « NFC indisponible sur cet appareil — saisissez le numéro ».
- Erreurs amicales : tag vide, illisible, ID non numérique, patient introuvable, session annulée.
- Accès discret à l'écran d'écriture (« Programmer une carte », action secondaire).

## 4. Écran d'écriture — `mobile/lib/screens/card_write_screen.dart`

Écran minimal : un champ numéro + bouton « Écrire sur la carte » → `writeCardId(id)` → « approchez le tag » → succès/erreur. C'est le provisionnement (sticker vierge → carte Dara Manqué).

## 5. Configuration Android

- `android/app/src/main/AndroidManifest.xml` :
  - `<uses-permission android:name="android.permission.NFC" />`
  - `<uses-feature android:name="android.hardware.nfc" android:required="false" />` (`required=false` → l'app s'installe aussi sur appareils sans NFC, qui utilisent le fallback manuel).
- `pubspec.yaml` : ajouter `nfc_manager`.
- iOS : hors périmètre.

## 6. Tests — `mobile/test/`

Réponse à « comment on teste sans brancher le téléphone » :

- **`test/card_id_test.dart`** — `parseCardId` : `"1001"` → 1001 ; `" 1001 "` → 1001 ; `""` → FormatException ; `"abc"` → FormatException ; `"10a1"` → FormatException.
- **`test/card_reader_test.dart`** — `MockCardReader` : `isAvailable()` true, `readCardId()` renvoie l'ID configuré, `writeCardId()` ne lève pas.
- **(optionnel) widget test** — `IdEntryScreen(cardReader: MockCardReader())` : présence du bouton scan quand NFC dispo, message de fallback quand indispo. (La navigation réelle appelle `fetchPatient` réseau → hors périmètre du test unitaire.)
- **Manuel / démo** — sur téléphone Android + tag : écrire `1001`, puis scanner → dossier chargé. Seul niveau exigeant du matériel.

`flutter test` tourne sans matériel et couvre toute la logique NFC-spécifique isolée.

---

## Fichiers touchés (récap)

**Créés :**
- `mobile/lib/nfc/card_reader.dart` (interface)
- `mobile/lib/nfc/nfc_card_reader.dart`
- `mobile/lib/nfc/mock_card_reader.dart`
- `mobile/lib/nfc/card_reader_factory.dart`
- `mobile/lib/nfc/card_id.dart`
- `mobile/lib/screens/card_write_screen.dart`
- `mobile/test/card_id_test.dart`
- `mobile/test/card_reader_test.dart`

**Modifiés :**
- `mobile/lib/screens/id_entry_screen.dart` (bouton scan + injection CardReader + fallback)
- `mobile/pubspec.yaml` (`nfc_manager`)
- `mobile/android/app/src/main/AndroidManifest.xml` (permission + feature NFC)

**Hors périmètre :** iOS, backend, binding UID, crypto/signature, mode hors-ligne (axe #3).
