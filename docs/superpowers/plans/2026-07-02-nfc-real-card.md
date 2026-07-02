# Carte NFC réelle — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remplacer la saisie manuelle de l'ID patient sur l'app mobile par un vrai scan NFC (avec fallback manuel conservé), testable sans matériel via une abstraction `CardReader`.

**Architecture:** Interface `CardReader` (Dart pur) avec deux implémentations — `NfcCardReader` (package `nfc_manager`, tag NDEF texte) et `MockCardReader` (dev/tests). `IdEntryScreen` consomme l'interface et bascule sur la saisie manuelle si le NFC est indisponible. Un nouvel écran `CardWriteScreen` permet le provisionnement (écrire l'ID sur un tag vierge).

**Tech Stack:** Flutter/Dart, `nfc_manager: ^4.2.1`, `nfc_manager_ndef: ^1.1.0`, `flutter_test`.

## Global Constraints

- Android uniquement — iOS explicitement hors périmètre (pas de config Xcode/Info.plist).
- Le tag NFC contient l'**ID patient en clair** dans un record NDEF texte (pas de binding UID matériel, pas de crypto).
- **Aucun changement backend** — `fetchPatient(int id)` reste inchangé.
- La **saisie manuelle reste un fallback fonctionnel** dans tous les cas (NFC indisponible, ou volontairement).
- Toute la logique NFC-spécifique doit être **testable sans matériel** via l'interface `CardReader` ; seul le geste physique final (scanner/écrire un vrai tag) nécessite un téléphone Android + un tag.
- Dépendances exactes : `nfc_manager: ^4.2.1`, `nfc_manager_ndef: ^1.1.0` (confirmées via pub.dev le 2026-07-02).
- Package racine de l'app mobile : `mobile` (imports `package:mobile/...`).

---

### Task 1: Parsing de l'ID de carte — `card_id.dart`

**Files:**
- Create: `mobile/lib/nfc/card_id.dart`
- Test: `mobile/test/card_id_test.dart`

**Interfaces:**
- Produces: `int parseCardId(String payload)` — lève `FormatException` (avec `.message` lisible) si `payload` est vide/blanc ou non numérique après trim.

- [ ] **Step 1: Write the failing test**

Create `mobile/test/card_id_test.dart`:

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/nfc/card_id.dart';

void main() {
  group('parseCardId', () {
    test('parses a plain numeric string', () {
      expect(parseCardId('1001'), 1001);
    });

    test('trims surrounding whitespace', () {
      expect(parseCardId(' 1001 '), 1001);
    });

    test('throws FormatException on empty payload', () {
      expect(() => parseCardId(''), throwsFormatException);
    });

    test('throws FormatException on whitespace-only payload', () {
      expect(() => parseCardId('   '), throwsFormatException);
    });

    test('throws FormatException on non-numeric payload', () {
      expect(() => parseCardId('abc'), throwsFormatException);
    });

    test('throws FormatException on mixed alphanumeric payload', () {
      expect(() => parseCardId('10a1'), throwsFormatException);
    });
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd mobile && flutter test test/card_id_test.dart`
Expected: FAIL — `Error: Error when reading 'lib/nfc/card_id.dart': No such file or directory` (or `Target of URI doesn't exist`).

- [ ] **Step 3: Write minimal implementation**

Create `mobile/lib/nfc/card_id.dart`:

```dart
int parseCardId(String payload) {
  final trimmed = payload.trim();
  if (trimmed.isEmpty) {
    throw const FormatException('Le tag ne contient aucun identifiant.');
  }
  final id = int.tryParse(trimmed);
  if (id == null) {
    throw const FormatException('Identifiant de carte invalide.');
  }
  return id;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd mobile && flutter test test/card_id_test.dart`
Expected: `00:0X +6: All tests passed!`

- [ ] **Step 5: Commit**

```bash
cd mobile && git add lib/nfc/card_id.dart test/card_id_test.dart
git commit -m "feat(mobile): add pure card-id parser for NFC payloads"
```

---

### Task 2: Abstraction `CardReader` + `MockCardReader`

**Files:**
- Create: `mobile/lib/nfc/card_reader.dart`
- Create: `mobile/lib/nfc/mock_card_reader.dart`
- Test: `mobile/test/card_reader_test.dart`

**Interfaces:**
- Consumes: nothing (Dart pur, aucune dépendance externe).
- Produces:
  - `abstract class CardReader { Future<bool> isAvailable(); Future<String> readCardId(); Future<void> writeCardId(String id); Future<void> cancelSession(); }`
  - `class MockCardReader implements CardReader` avec constructeur `MockCardReader({String mockId = '1001', Duration delay = const Duration(milliseconds: 500)})`.

- [ ] **Step 1: Write the failing test**

Create `mobile/test/card_reader_test.dart`:

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/nfc/mock_card_reader.dart';

void main() {
  group('MockCardReader', () {
    test('isAvailable returns true', () async {
      final reader = MockCardReader();
      expect(await reader.isAvailable(), isTrue);
    });

    test('readCardId returns the configured id', () async {
      final reader = MockCardReader(mockId: '2002', delay: Duration.zero);
      expect(await reader.readCardId(), '2002');
    });

    test('readCardId defaults to 1001', () async {
      final reader = MockCardReader(delay: Duration.zero);
      expect(await reader.readCardId(), '1001');
    });

    test('writeCardId completes without throwing', () async {
      final reader = MockCardReader(delay: Duration.zero);
      await expectLater(reader.writeCardId('1001'), completes);
    });

    test('cancelSession completes without throwing', () async {
      final reader = MockCardReader();
      await expectLater(reader.cancelSession(), completes);
    });
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd mobile && flutter test test/card_reader_test.dart`
Expected: FAIL — `Target of URI doesn't exist: 'package:mobile/nfc/mock_card_reader.dart'`.

- [ ] **Step 3: Write minimal implementation**

Create `mobile/lib/nfc/card_reader.dart`:

```dart
abstract class CardReader {
  /// true si le matériel NFC est présent et activé sur cet appareil.
  Future<bool> isAvailable();

  /// Démarre un scan, lit l'ID écrit sur le tag (record NDEF texte).
  /// Lève une FormatException lisible si le tag est vide/illisible.
  Future<String> readCardId();

  /// Écrit `id` comme record NDEF texte sur le tag approché.
  Future<void> writeCardId(String id);

  /// Annule une session de lecture/écriture en cours (no-op si aucune).
  Future<void> cancelSession();
}
```

Create `mobile/lib/nfc/mock_card_reader.dart`:

```dart
import 'card_reader.dart';

class MockCardReader implements CardReader {
  MockCardReader({this.mockId = '1001', this.delay = const Duration(milliseconds: 500)});

  final String mockId;
  final Duration delay;

  @override
  Future<bool> isAvailable() async => true;

  @override
  Future<String> readCardId() async {
    await Future.delayed(delay);
    return mockId;
  }

  @override
  Future<void> writeCardId(String id) async {
    await Future.delayed(delay);
  }

  @override
  Future<void> cancelSession() async {}
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd mobile && flutter test test/card_reader_test.dart`
Expected: `00:0X +5: All tests passed!`

- [ ] **Step 5: Commit**

```bash
cd mobile && git add lib/nfc/card_reader.dart lib/nfc/mock_card_reader.dart test/card_reader_test.dart
git commit -m "feat(mobile): add CardReader abstraction and mock implementation"
```

---

### Task 3: Implémentation réelle — `NfcCardReader`

**Files:**
- Modify: `mobile/pubspec.yaml`
- Modify: `mobile/android/app/src/main/AndroidManifest.xml`
- Create: `mobile/lib/nfc/nfc_card_reader.dart`

**Interfaces:**
- Consumes: `CardReader` (Task 2, `mobile/lib/nfc/card_reader.dart`).
- Produces: `class NfcCardReader implements CardReader` (constructeur sans argument `NfcCardReader()`).

> Pas de test automatisé possible ici : cette classe pilote le matériel NFC réel, qui n'existe pas en émulateur/CI. La vérification de ce task est statique (`flutter analyze`) ; la vérification fonctionnelle se fait au Task 7 (sur téléphone).

- [ ] **Step 1: Add NFC dependencies**

Edit `mobile/pubspec.yaml`, in the `dependencies:` block, after `http: ^1.2.0`:

```yaml
  http: ^1.2.0
  nfc_manager: ^4.2.1
  nfc_manager_ndef: ^1.1.0
```

- [ ] **Step 2: Install and verify**

Run: `cd mobile && flutter pub get`
Expected: `Got dependencies!` with no version-resolution errors.

- [ ] **Step 3: Add Android NFC permission and feature declaration**

Edit `mobile/android/app/src/main/AndroidManifest.xml`, add the permission and feature declaration as the first children of `<manifest>` (before `<application>`):

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.NFC" />
    <uses-feature android:name="android.hardware.nfc" android:required="false" />
    <application
```

(Only the opening `<application` line changes context — insert the two lines above immediately above it, leave the rest of the file untouched. `android:required="false"` lets the app install on devices without NFC hardware, which then use the manual-entry fallback.)

> **Corrigé le 2026-07-02** après implémentation : la version réellement publiée de
> `nfc_manager_ndef: ^1.1.0` (qui tire `ndef_record: ^1.4.2`) n'a pas de
> `NdefRecord.createText()` ; `Ndef.read()` renvoie `Future<NdefMessage?>` (nullable) et
> `Ndef.write()` prend un paramètre nommé `message:`. Le code ci-dessous construit le
> record texte NDEF manuellement (RTD "T", cf. `_createTextRecord`) — vérifié contre le
> code source installé sous `~/.pub-cache/hosted/pub.dev/`.

- [ ] **Step 4: Write the real implementation**

Create `mobile/lib/nfc/nfc_card_reader.dart`:

```dart
import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:nfc_manager/nfc_manager.dart';
import 'package:nfc_manager/ndef_record.dart';
import 'package:nfc_manager_ndef/nfc_manager_ndef.dart';

import 'card_reader.dart';

class NfcCardReader implements CardReader {
  static const _pollingOptions = {
    NfcPollingOption.iso14443,
    NfcPollingOption.iso15693,
    NfcPollingOption.iso18092,
  };

  static const _language = 'en';

  Completer<String>? _pendingRead;
  Completer<void>? _pendingWrite;

  @override
  Future<bool> isAvailable() async {
    final availability = await NfcManager.instance.checkAvailability();
    return availability == NfcAvailability.enabled;
  }

  @override
  Future<String> readCardId() {
    final completer = Completer<String>();
    _pendingRead = completer;
    NfcManager.instance.startSession(
      pollingOptions: _pollingOptions,
      onDiscovered: (NfcTag tag) async {
        try {
          final ndef = Ndef.from(tag);
          if (ndef == null) {
            throw const FormatException("Ce tag n'est pas au format NDEF.");
          }
          final message = await ndef.read();
          if (message == null || message.records.isEmpty) {
            throw const FormatException('Tag NFC vide.');
          }
          final id = _decodeTextPayload(message.records.first.payload);
          if (!completer.isCompleted) completer.complete(id);
        } catch (e) {
          if (!completer.isCompleted) completer.completeError(e);
        } finally {
          await NfcManager.instance.stopSession();
        }
      },
    );
    return completer.future;
  }

  @override
  Future<void> writeCardId(String id) {
    final completer = Completer<void>();
    _pendingWrite = completer;
    NfcManager.instance.startSession(
      pollingOptions: _pollingOptions,
      onDiscovered: (NfcTag tag) async {
        try {
          final ndef = Ndef.from(tag);
          if (ndef == null) {
            throw const FormatException('Ce tag ne supporte pas NDEF.');
          }
          await ndef.write(message: NdefMessage(records: [_createTextRecord(id)]));
          if (!completer.isCompleted) completer.complete();
        } catch (e) {
          if (!completer.isCompleted) completer.completeError(e);
        } finally {
          await NfcManager.instance.stopSession();
        }
      },
    );
    return completer.future;
  }

  @override
  Future<void> cancelSession() async {
    await NfcManager.instance.stopSession();
    if (_pendingRead != null && !_pendingRead!.isCompleted) {
      _pendingRead!.completeError(const FormatException('Scan annulé.'));
    }
    if (_pendingWrite != null && !_pendingWrite!.isCompleted) {
      _pendingWrite!.completeError(const FormatException('Écriture annulée.'));
    }
  }

  /// Construit un record NDEF "Text" (RTD "T") en UTF-8, langue "en".
  NdefRecord _createTextRecord(String text) {
    final languageBytes = utf8.encode(_language);
    final textBytes = utf8.encode(text);
    final payload = Uint8List.fromList([
      languageBytes.length,
      ...languageBytes,
      ...textBytes,
    ]);
    return NdefRecord(
      typeNameFormat: TypeNameFormat.wellKnown,
      type: Uint8List.fromList('T'.codeUnits),
      identifier: Uint8List(0),
      payload: payload,
    );
  }

  /// Décode un payload de record NDEF texte (statut + code langue + texte).
  /// On suppose un encodage UTF-8 : tous nos tags sont écrits par _createTextRecord,
  /// qui encode en UTF-8 par défaut.
  String _decodeTextPayload(Uint8List payload) {
    if (payload.isEmpty) {
      throw const FormatException('Tag NFC vide.');
    }
    final languageCodeLength = payload[0] & 0x3f;
    final textStart = 1 + languageCodeLength;
    if (textStart > payload.length) {
      throw const FormatException('Format de tag NFC invalide.');
    }
    return utf8.decode(payload.sublist(textStart));
  }
}
```

- [ ] **Step 5: Static verification**

Run: `cd mobile && flutter analyze lib/nfc/nfc_card_reader.dart`
Expected: `No issues found!`

- [ ] **Step 6: Commit**

```bash
cd mobile && git add pubspec.yaml pubspec.lock android/app/src/main/AndroidManifest.xml lib/nfc/nfc_card_reader.dart
git commit -m "feat(mobile): add real NfcCardReader backed by nfc_manager"
```

---

### Task 4: Sélection du lecteur — `card_reader_factory.dart`

**Files:**
- Create: `mobile/lib/nfc/card_reader_factory.dart`
- Test: `mobile/test/card_reader_factory_test.dart`

**Interfaces:**
- Consumes: `CardReader`, `MockCardReader` (Task 2), `NfcCardReader` (Task 3).
- Produces: `CardReader createCardReader({bool useMock = const bool.fromEnvironment('USE_MOCK_NFC', defaultValue: false)})`.

- [ ] **Step 1: Write the failing test**

Create `mobile/test/card_reader_factory_test.dart`:

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/nfc/card_reader_factory.dart';
import 'package:mobile/nfc/mock_card_reader.dart';
import 'package:mobile/nfc/nfc_card_reader.dart';

void main() {
  test('returns MockCardReader when useMock is true', () {
    expect(createCardReader(useMock: true), isA<MockCardReader>());
  });

  test('returns NfcCardReader when useMock is false', () {
    expect(createCardReader(useMock: false), isA<NfcCardReader>());
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd mobile && flutter test test/card_reader_factory_test.dart`
Expected: FAIL — `Target of URI doesn't exist: 'package:mobile/nfc/card_reader_factory.dart'`.

- [ ] **Step 3: Write minimal implementation**

Create `mobile/lib/nfc/card_reader_factory.dart`:

```dart
import 'card_reader.dart';
import 'mock_card_reader.dart';
import 'nfc_card_reader.dart';

/// `useMock` par défaut lit le flag de compilation `USE_MOCK_NFC`
/// (`flutter run --dart-define=USE_MOCK_NFC=true`), utile en dev sans matériel.
CardReader createCardReader({
  bool useMock = const bool.fromEnvironment('USE_MOCK_NFC', defaultValue: false),
}) {
  return useMock ? MockCardReader() : NfcCardReader();
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd mobile && flutter test test/card_reader_factory_test.dart`
Expected: `00:0X +2: All tests passed!`

- [ ] **Step 5: Commit**

```bash
cd mobile && git add lib/nfc/card_reader_factory.dart test/card_reader_factory_test.dart
git commit -m "feat(mobile): add card reader factory with mock override flag"
```

---

### Task 5: Écran de provisionnement — `CardWriteScreen`

**Files:**
- Create: `mobile/lib/screens/card_write_screen.dart`
- Test: `mobile/test/card_write_screen_test.dart`

**Interfaces:**
- Consumes: `CardReader` (Task 2), `parseCardId` (Task 1), `MockCardReader` (Task 2, for tests).
- Produces: `class CardWriteScreen extends StatefulWidget` with constructor `CardWriteScreen({super.key, required CardReader cardReader})`.

- [ ] **Step 1: Write the failing test**

Create `mobile/test/card_write_screen_test.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/nfc/mock_card_reader.dart';
import 'package:mobile/screens/card_write_screen.dart';

void main() {
  testWidgets('shows validation error for non-numeric input', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: CardWriteScreen(cardReader: MockCardReader(delay: Duration.zero)),
    ));

    await tester.enterText(find.byType(TextField), 'abc');
    await tester.tap(find.text('Écrire sur la carte'));
    await tester.pump();

    expect(find.text('Identifiant de carte invalide.'), findsOneWidget);
  });

  testWidgets('writes a valid id and shows success', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: CardWriteScreen(cardReader: MockCardReader(delay: Duration.zero)),
    ));

    await tester.enterText(find.byType(TextField), '1001');
    await tester.tap(find.text('Écrire sur la carte'));
    await tester.pumpAndSettle();

    expect(find.text('Carte programmée avec succès.'), findsOneWidget);
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd mobile && flutter test test/card_write_screen_test.dart`
Expected: FAIL — `Target of URI doesn't exist: 'package:mobile/screens/card_write_screen.dart'`.

- [ ] **Step 3: Write minimal implementation**

Create `mobile/lib/screens/card_write_screen.dart`:

```dart
import 'package:flutter/material.dart';
import '../nfc/card_id.dart';
import '../nfc/card_reader.dart';

class CardWriteScreen extends StatefulWidget {
  const CardWriteScreen({super.key, required this.cardReader});

  final CardReader cardReader;

  @override
  State<CardWriteScreen> createState() => _CardWriteScreenState();
}

class _CardWriteScreenState extends State<CardWriteScreen> {
  final _controller = TextEditingController();
  bool _writing = false;
  String? _error;
  bool _success = false;

  @override
  void dispose() {
    _controller.dispose();
    widget.cardReader.cancelSession();
    super.dispose();
  }

  Future<void> _write() async {
    final text = _controller.text.trim();
    try {
      parseCardId(text);
    } on FormatException catch (e) {
      setState(() => _error = e.message);
      return;
    }
    setState(() {
      _writing = true;
      _error = null;
      _success = false;
    });
    try {
      await widget.cardReader.writeCardId(text);
      if (mounted) setState(() => _success = true);
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e is FormatException ? e.message : "Échec de l'écriture sur la carte.";
        });
      }
    } finally {
      if (mounted) setState(() => _writing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Programmer une carte')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                "Saisissez le numéro de carte patient, puis approchez un tag NFC vierge du téléphone.",
                style: TextStyle(color: Color(0xFF64748B), fontSize: 14),
              ),
              const SizedBox(height: 20),
              TextField(
                controller: _controller,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Numéro de carte',
                  hintText: 'Ex : 1001',
                ),
              ),
              if (_error != null) ...[
                const SizedBox(height: 10),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFEF2F2),
                    borderRadius: BorderRadius.circular(8),
                    border: Border(left: BorderSide(color: const Color(0xFFDC2626), width: 3)),
                  ),
                  child: Text(_error!, style: const TextStyle(color: Color(0xFFDC2626), fontSize: 13)),
                ),
              ],
              if (_success) ...[
                const SizedBox(height: 10),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF0FDF4),
                    borderRadius: BorderRadius.circular(8),
                    border: Border(left: BorderSide(color: const Color(0xFF16A34A), width: 3)),
                  ),
                  child: const Text('Carte programmée avec succès.', style: TextStyle(color: Color(0xFF16A34A), fontSize: 13)),
                ),
              ],
              const SizedBox(height: 20),
              FilledButton(
                onPressed: _writing ? null : _write,
                child: _writing
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Text('Écrire sur la carte'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd mobile && flutter test test/card_write_screen_test.dart`
Expected: `00:0X +2: All tests passed!`

- [ ] **Step 5: Commit**

```bash
cd mobile && git add lib/screens/card_write_screen.dart test/card_write_screen_test.dart
git commit -m "feat(mobile): add card provisioning screen"
```

---

### Task 6: Intégration dans `IdEntryScreen`

**Files:**
- Modify: `mobile/lib/screens/id_entry_screen.dart` (full replacement of the `_IdEntryScreenState`-owning file; `_NfcCard` widget at the bottom is unchanged)
- Test: `mobile/test/id_entry_screen_test.dart`
- Regression: `mobile/test/widget_test.dart` (existing, unchanged — must still pass)

**Interfaces:**
- Consumes: `CardReader`, `MockCardReader` (Task 2), `createCardReader` (Task 4), `parseCardId` (Task 1), `CardWriteScreen` (Task 5), existing `fetchPatient` (`mobile/lib/api/client.dart`), existing `HomeScreen` (`mobile/lib/screens/home_screen.dart`).
- Produces: `IdEntryScreen` gains an optional `cardReader` constructor param (`const IdEntryScreen({super.key, this.cardReader})`), used by tests to inject a `MockCardReader`.

- [ ] **Step 1: Write the failing tests**

Create `mobile/test/id_entry_screen_test.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/nfc/mock_card_reader.dart';
import 'package:mobile/screens/id_entry_screen.dart';

class _UnavailableReader extends MockCardReader {
  @override
  Future<bool> isAvailable() async => false;
}

void main() {
  testWidgets('shows scan button and provisioning link when NFC is available', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: IdEntryScreen(cardReader: MockCardReader(delay: Duration.zero)),
    ));
    await tester.pumpAndSettle();

    expect(find.text('Scanner ma carte'), findsOneWidget);
    expect(find.text('Programmer une carte'), findsOneWidget);
  });

  testWidgets('shows manual fallback message when NFC is unavailable', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: IdEntryScreen(cardReader: _UnavailableReader()),
    ));
    await tester.pumpAndSettle();

    expect(find.text('Scanner ma carte'), findsNothing);
    expect(find.textContaining('NFC indisponible'), findsOneWidget);
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd mobile && flutter test test/id_entry_screen_test.dart`
Expected: FAIL — `The named parameter 'cardReader' isn't defined` (constructor doesn't accept it yet).

- [ ] **Step 3: Replace `mobile/lib/screens/id_entry_screen.dart`**

Replace the entire file content with:

```dart
import 'package:flutter/material.dart';
import '../api/client.dart';
import '../nfc/card_id.dart';
import '../nfc/card_reader.dart';
import '../nfc/card_reader_factory.dart';
import 'card_write_screen.dart';
import 'home_screen.dart';

class IdEntryScreen extends StatefulWidget {
  const IdEntryScreen({super.key, this.cardReader});

  final CardReader? cardReader;

  @override
  State<IdEntryScreen> createState() => _IdEntryScreenState();
}

class _IdEntryScreenState extends State<IdEntryScreen> {
  late final CardReader _cardReader = widget.cardReader ?? createCardReader();
  final _controller = TextEditingController();
  bool _loading = false;
  bool _scanning = false;
  bool _nfcAvailable = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _checkNfc();
  }

  Future<void> _checkNfc() async {
    bool available;
    try {
      available = await _cardReader.isAvailable();
    } catch (_) {
      available = false;
    }
    if (mounted) setState(() => _nfcAvailable = available);
  }

  @override
  void dispose() {
    _controller.dispose();
    _cardReader.cancelSession();
    super.dispose();
  }

  Future<void> _access() async {
    final id = int.tryParse(_controller.text.trim());
    if (id == null) {
      setState(() => _error = 'Veuillez entrer un identifiant valide.');
      return;
    }
    await _loadPatient(id);
  }

  Future<void> _scanCard() async {
    setState(() {
      _scanning = true;
      _error = null;
    });
    try {
      final payload = await _cardReader.readCardId();
      final id = parseCardId(payload);
      await _loadPatient(id);
    } catch (e) {
      if (mounted) {
        final message = e is FormatException ? e.message : e.toString().replaceAll('Exception: ', '');
        setState(() => _error = 'Lecture de la carte impossible : $message');
      }
    } finally {
      if (mounted) setState(() => _scanning = false);
    }
  }

  Future<void> _loadPatient(int id) async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final patient = await fetchPatient(id);
      if (!mounted) return;
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => HomeScreen(patient: patient)),
      );
    } catch (e) {
      setState(() => _error = e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _openCardWriter() {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => CardWriteScreen(cardReader: _cardReader)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 40),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 20),

              const Text(
                'Dara Manqué',
                style: TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1E293B),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 6),
              const Text(
                'Carnet de santé numérique',
                style: TextStyle(color: Color(0xFF64748B), fontSize: 14),
                textAlign: TextAlign.center,
              ),

              const SizedBox(height: 40),

              Center(
                child: _NfcCard(cardNumber: _controller.text),
              ),

              const SizedBox(height: 28),

              if (_nfcAvailable) ...[
                FilledButton.icon(
                  onPressed: _scanning ? null : _scanCard,
                  icon: _scanning
                      ? const SizedBox(
                          height: 18,
                          width: 18,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : const Icon(Icons.nfc),
                  label: Text(_scanning ? 'Scan en cours...' : 'Scanner ma carte'),
                ),
                const SizedBox(height: 16),
                const Row(
                  children: [
                    Expanded(child: Divider()),
                    Padding(
                      padding: EdgeInsets.symmetric(horizontal: 12),
                      child: Text('ou', style: TextStyle(color: Color(0xFF64748B))),
                    ),
                    Expanded(child: Divider()),
                  ],
                ),
                const SizedBox(height: 16),
              ] else ...[
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'NFC indisponible sur cet appareil — saisissez le numéro.',
                    style: TextStyle(color: Color(0xFF64748B), fontSize: 13),
                  ),
                ),
                const SizedBox(height: 20),
              ],

              TextField(
                controller: _controller,
                keyboardType: TextInputType.number,
                onChanged: (_) => setState(() {}),
                decoration: const InputDecoration(
                  labelText: 'Numéro de carte patient',
                  hintText: 'Ex : 1001',
                  prefixIcon: Icon(Icons.credit_card, color: Color(0xFF0D9488)),
                ),
                onSubmitted: (_) => _access(),
              ),

              if (_error != null) ...[
                const SizedBox(height: 10),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFEF2F2),
                    borderRadius: BorderRadius.circular(8),
                    border: Border(left: BorderSide(color: const Color(0xFFDC2626), width: 3)),
                  ),
                  child: Text(_error!, style: const TextStyle(color: Color(0xFFDC2626), fontSize: 13)),
                ),
              ],

              const SizedBox(height: 20),

              FilledButton(
                onPressed: _loading ? null : _access,
                child: _loading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Text('Accéder à mon carnet de santé'),
              ),

              if (_nfcAvailable) ...[
                const SizedBox(height: 12),
                TextButton(
                  onPressed: _openCardWriter,
                  child: const Text('Programmer une carte'),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _NfcCard extends StatelessWidget {
  final String cardNumber;
  const _NfcCard({required this.cardNumber});

  String get _displayNumber {
    if (cardNumber.isEmpty) return '● ● ● ●';
    return cardNumber.length > 8 ? cardNumber.substring(0, 8) : cardNumber;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 300,
      height: 180,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF0D9488), Color(0xFF0F766E)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF0D9488).withAlpha(90),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Stack(
        children: [
          Positioned(
            top: -30, right: -30,
            child: Container(
              width: 120, height: 120,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.white.withAlpha(20),
              ),
            ),
          ),
          Positioned(
            bottom: -20, left: -20,
            child: Container(
              width: 90, height: 90,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.white.withAlpha(15),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(22),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 38, height: 28,
                  decoration: BoxDecoration(
                    color: const Color(0xFFD4AF37),
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const Spacer(),
                Text(
                  _displayNumber,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 3,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: const [
                    Flexible(
                      child: Text(
                        'Dara Manqué',
                        style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    SizedBox(width: 8),
                    Flexible(
                      child: Text(
                        'CARTE SANTÉ',
                        style: TextStyle(color: Colors.white70, fontSize: 10, letterSpacing: 1.5),
                        overflow: TextOverflow.ellipsis,
                        textAlign: TextAlign.right,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

- [ ] **Step 4: Run new tests to verify they pass**

Run: `cd mobile && flutter test test/id_entry_screen_test.dart`
Expected: `00:0X +2: All tests passed!`

- [ ] **Step 5: Run full test suite (regression check)**

Run: `cd mobile && flutter test`
Expected: all tests pass, including the pre-existing `test/widget_test.dart` smoke test (`App smoke test — renders ID entry screen`). This confirms the real `createCardReader()` path (invoked when `cardReader` isn't injected) doesn't crash when the NFC platform channel is absent (test environment) — `_checkNfc`'s try/catch handles that by treating it as "NFC unavailable".

- [ ] **Step 6: Commit**

```bash
cd mobile && git add lib/screens/id_entry_screen.dart test/id_entry_screen_test.dart
git commit -m "feat(mobile): wire real NFC scan into id entry screen with manual fallback"
```

---

### Task 7: Vérification manuelle sur matériel réel

**Files:** aucun (checklist manuelle, pas de code).

Ce projet n'a pas de téléphone Android NFC ni de tag connecté à cette session. Cette tâche est **à exécuter par l'utilisateur** quand le matériel est disponible — elle ne peut pas être automatisée ni vérifiée par un agent.

- [ ] **Step 1: Build and install on a physical Android device with NFC**

Run: `cd mobile && flutter run --release` (device connecté en USB, débogage activé)

- [ ] **Step 2: Provisionner un tag**

Dans l'app : bouton « Programmer une carte » → saisir `1001` → « Écrire sur la carte » → approcher un tag NFC vierge (NTAG213/215/216) → vérifier le message « Carte programmée avec succès. »

- [ ] **Step 3: Scanner le tag programmé**

Retour à l'écran d'accueil → « Scanner ma carte » → approcher le même tag → vérifier que le dossier de Mamadou Diallo (patient 1001) s'ouvre.

- [ ] **Step 4: Vérifier le fallback**

Couper le NFC dans les réglages Android → relancer l'app → vérifier que le bouton scan disparaît, que le message « NFC indisponible... » s'affiche, et que la saisie manuelle de `1001` fonctionne toujours.

- [ ] **Step 5: Documenter le résultat**

Mettre à jour la mémoire `project_differentiation` (axe #1) pour marquer le NFC réel comme livré, avec la date du test matériel réussi.
