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
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Dara Manqué',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              const Text(
                'Entrez votre identifiant patient',
                style: TextStyle(color: Colors.grey),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 40),
              TextField(
                controller: _controller,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'ID Patient (ex: 1001)',
                  border: OutlineInputBorder(),
                ),
                onSubmitted: (_) => _access(),
              ),
              if (_error != null) ...[
                const SizedBox(height: 8),
                Text(_error!, style: const TextStyle(color: Colors.red)),
              ],
              const SizedBox(height: 16),
              FilledButton(
                onPressed: _loading ? null : _access,
                child: _loading
                    ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Text('Accéder'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
