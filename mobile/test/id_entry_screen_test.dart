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
