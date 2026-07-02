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
