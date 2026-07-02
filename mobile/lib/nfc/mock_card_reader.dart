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
