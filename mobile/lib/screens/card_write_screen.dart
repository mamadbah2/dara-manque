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
