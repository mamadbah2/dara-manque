import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/main.dart';

void main() {
  testWidgets('App smoke test — renders ID entry screen', (WidgetTester tester) async {
    await tester.pumpWidget(const DaraManqueApp());
    expect(find.text('Dara Manqué'), findsWidgets);
  });
}
