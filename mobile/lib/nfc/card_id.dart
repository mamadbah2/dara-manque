int parseCardId(String payload) {
  final trimmed = payload.trim();
  if (trimmed.isEmpty) {
    throw const FormatException('Le tag ne contient aucun identifiant.');
  }
  final id = int.tryParse(trimmed);
  if (id == null) {
    throw const FormatException('Identifiant de carte invalide.');
  }
  return id;
}
