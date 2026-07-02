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
