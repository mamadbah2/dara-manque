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
