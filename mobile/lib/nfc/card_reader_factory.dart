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
