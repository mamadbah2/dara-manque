import 'package:flutter/material.dart';
import '../api/client.dart';
import '../nfc/card_id.dart';
import '../nfc/card_reader.dart';
import '../nfc/card_reader_factory.dart';
import 'card_write_screen.dart';
import 'home_screen.dart';

class IdEntryScreen extends StatefulWidget {
  const IdEntryScreen({super.key, this.cardReader});

  final CardReader? cardReader;

  @override
  State<IdEntryScreen> createState() => _IdEntryScreenState();
}

class _IdEntryScreenState extends State<IdEntryScreen> {
  late final CardReader _cardReader = widget.cardReader ?? createCardReader();
  final _controller = TextEditingController();
  bool _loading = false;
  bool _scanning = false;
  bool _nfcAvailable = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _checkNfc();
  }

  Future<void> _checkNfc() async {
    bool available;
    try {
      available = await _cardReader.isAvailable();
    } catch (_) {
      available = false;
    }
    if (mounted) setState(() => _nfcAvailable = available);
  }

  @override
  void dispose() {
    _controller.dispose();
    _cardReader.cancelSession();
    super.dispose();
  }

  Future<void> _access() async {
    final id = int.tryParse(_controller.text.trim());
    if (id == null) {
      setState(() => _error = 'Veuillez entrer un identifiant valide.');
      return;
    }
    await _loadPatient(id);
  }

  Future<void> _scanCard() async {
    setState(() {
      _scanning = true;
      _error = null;
    });
    try {
      final payload = await _cardReader.readCardId();
      final id = parseCardId(payload);
      await _loadPatient(id);
    } catch (e) {
      if (mounted) {
        final message = e is FormatException ? e.message : e.toString().replaceAll('Exception: ', '');
        setState(() => _error = 'Lecture de la carte impossible : $message');
      }
    } finally {
      if (mounted) setState(() => _scanning = false);
    }
  }

  Future<void> _loadPatient(int id) async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final patient = await fetchPatient(id);
      if (!mounted) return;
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => HomeScreen(patient: patient)),
      );
    } catch (e) {
      setState(() => _error = e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _openCardWriter() {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => CardWriteScreen(cardReader: _cardReader)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 40),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 20),

              const Text(
                'Dara Manqué',
                style: TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1E293B),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 6),
              const Text(
                'Carnet de santé numérique',
                style: TextStyle(color: Color(0xFF64748B), fontSize: 14),
                textAlign: TextAlign.center,
              ),

              const SizedBox(height: 40),

              Center(
                child: _NfcCard(cardNumber: _controller.text),
              ),

              const SizedBox(height: 28),

              if (_nfcAvailable) ...[
                FilledButton.icon(
                  onPressed: _scanning ? null : _scanCard,
                  icon: _scanning
                      ? const SizedBox(
                          height: 18,
                          width: 18,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : const Icon(Icons.nfc),
                  label: Text(_scanning ? 'Scan en cours...' : 'Scanner ma carte'),
                ),
                const SizedBox(height: 16),
                const Row(
                  children: [
                    Expanded(child: Divider()),
                    Padding(
                      padding: EdgeInsets.symmetric(horizontal: 12),
                      child: Text('ou', style: TextStyle(color: Color(0xFF64748B))),
                    ),
                    Expanded(child: Divider()),
                  ],
                ),
                const SizedBox(height: 16),
              ] else ...[
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'NFC indisponible sur cet appareil — saisissez le numéro.',
                    style: TextStyle(color: Color(0xFF64748B), fontSize: 13),
                  ),
                ),
                const SizedBox(height: 20),
              ],

              TextField(
                controller: _controller,
                keyboardType: TextInputType.number,
                onChanged: (_) => setState(() {}),
                decoration: const InputDecoration(
                  labelText: 'Numéro de carte patient',
                  hintText: 'Ex : 1001',
                  prefixIcon: Icon(Icons.credit_card, color: Color(0xFF0D9488)),
                ),
                onSubmitted: (_) => _access(),
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

              const SizedBox(height: 20),

              FilledButton(
                onPressed: _loading ? null : _access,
                child: _loading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Text('Accéder à mon carnet de santé'),
              ),

              if (_nfcAvailable) ...[
                const SizedBox(height: 12),
                TextButton(
                  onPressed: _openCardWriter,
                  child: const Text('Programmer une carte'),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _NfcCard extends StatelessWidget {
  final String cardNumber;
  const _NfcCard({required this.cardNumber});

  String get _displayNumber {
    if (cardNumber.isEmpty) return '● ● ● ●';
    return cardNumber.length > 8 ? cardNumber.substring(0, 8) : cardNumber;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 300,
      height: 180,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF0D9488), Color(0xFF0F766E)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF0D9488).withAlpha(90),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Stack(
        children: [
          Positioned(
            top: -30, right: -30,
            child: Container(
              width: 120, height: 120,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.white.withAlpha(20),
              ),
            ),
          ),
          Positioned(
            bottom: -20, left: -20,
            child: Container(
              width: 90, height: 90,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.white.withAlpha(15),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(22),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 38, height: 28,
                  decoration: BoxDecoration(
                    color: const Color(0xFFD4AF37),
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const Spacer(),
                Text(
                  _displayNumber,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 3,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: const [
                    Flexible(
                      child: Text(
                        'Dara Manqué',
                        style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    SizedBox(width: 8),
                    Flexible(
                      child: Text(
                        'CARTE SANTÉ',
                        style: TextStyle(color: Colors.white70, fontSize: 10, letterSpacing: 1.5),
                        overflow: TextOverflow.ellipsis,
                        textAlign: TextAlign.right,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
