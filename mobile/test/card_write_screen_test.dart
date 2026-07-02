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

  testWidgets('clears stale success banner when a later submission fails validation', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: CardWriteScreen(cardReader: MockCardReader(delay: Duration.zero)),
    ));

    await tester.enterText(find.byType(TextField), '1001');
    await tester.tap(find.text('Écrire sur la carte'));
    await tester.pumpAndSettle();

    expect(find.text('Carte programmée avec succès.'), findsOneWidget);

    await tester.enterText(find.byType(TextField), 'abc');
    await tester.tap(find.text('Écrire sur la carte'));
    await tester.pump();

    expect(find.text('Carte programmée avec succès.'), findsNothing);
    expect(find.text('Identifiant de carte invalide.'), findsOneWidget);
  });
}
