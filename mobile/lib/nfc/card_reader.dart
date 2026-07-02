abstract class CardReader {
  /// true si le matériel NFC est présent et activé sur cet appareil.
  Future<bool> isAvailable();

  /// Démarre un scan, lit l'ID écrit sur le tag (record NDEF texte).
  /// Lève une FormatException lisible si le tag est vide/illisible.
  Future<String> readCardId();

  /// Écrit `id` comme record NDEF texte sur le tag approché.
  Future<void> writeCardId(String id);

  /// Annule une session de lecture/écriture en cours (no-op si aucune).
  Future<void> cancelSession();
}
