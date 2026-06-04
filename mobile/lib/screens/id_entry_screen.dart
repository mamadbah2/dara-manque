import 'package:flutter/material.dart';
import '../api/client.dart';
import 'home_screen.dart';

class IdEntryScreen extends StatefulWidget {
  const IdEntryScreen({super.key});

  @override
  State<IdEntryScreen> createState() => _IdEntryScreenState();
}

class _IdEntryScreenState extends State<IdEntryScreen> {
  final _controller = TextEditingController();
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _access() async {
    final id = int.tryParse(_controller.text.trim());
    if (id == null) {
      setState(() => _error = 'Veuillez entrer un identifiant valide.');
      return;
    }
    setState(() { _loading = true; _error = null; });
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

              // Titre
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

              // Widget carte NFC
              Center(
                child: _NfcCard(cardNumber: _controller.text),
              ),

              const SizedBox(height: 36),

              // Saisie ID
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
                        height: 20, width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Text('Accéder à mon carnet de santé'),
              ),
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
          // Cercles décoratifs
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
                // Puce NFC simulée
                Container(
                  width: 38, height: 28,
                  decoration: BoxDecoration(
                    color: const Color(0xFFD4AF37),
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const Spacer(),
                // Numéro
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
                    Text(
                      'Dara Manqué',
                      style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600),
                    ),
                    Text(
                      'CARTE SANTÉ',
                      style: TextStyle(color: Colors.white70, fontSize: 10, letterSpacing: 1.5),
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
