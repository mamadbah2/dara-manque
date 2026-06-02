import 'package:flutter/material.dart';
import 'screens/id_entry_screen.dart';

void main() {
  runApp(const DaraManqueApp());
}

class DaraManqueApp extends StatelessWidget {
  const DaraManqueApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Dara Manqué',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1a73e8)),
        useMaterial3: true,
      ),
      home: const IdEntryScreen(),
    );
  }
}
