import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/nfc/card_id.dart';

void main() {
  group('parseCardId', () {
    test('normalizes a hex UID with colon separators', () {
      expect(parseCardId('04:a2:b3:c1'), '04A2B3C1');
    });

    test('uppercases a lowercase hex UID', () {
      expect(parseCardId('deadbeef'), 'DEADBEEF');
    });

    test('strips space and dash separators', () {
      expect(parseCardId('04 A2-B3 C1'), '04A2B3C1');
    });

    test('accepts a plain numeric string', () {
      expect(parseCardId('1001'), '1001');
    });

    test('trims surrounding whitespace', () {
      expect(parseCardId(' 04A2B3C1 '), '04A2B3C1');
    });

    test('throws FormatException on empty payload', () {
      expect(() => parseCardId(''), throwsFormatException);
    });

    test('throws FormatException on whitespace-only payload', () {
      expect(() => parseCardId('   '), throwsFormatException);
    });

    test('throws FormatException on non-hex payload', () {
      expect(() => parseCardId('xyz'), throwsFormatException);
    });
  });
}
