/// Parses and normalizes an NFC card payload into a canonical UID.
///
/// The hardware reader (ESP32 + RC522) — and the phone's NFC stack — yield a
/// card UID in hexadecimal, possibly with ':', '-' or space separators and in
/// any case. We normalize to compact uppercase hex, mirroring the backend
/// `normalize_uid`, so a card enrolled once always resolves on later scans.
String parseCardId(String payload) {
  final compact = payload.trim().replaceAll(RegExp(r'[\s:-]'), '');
  if (compact.isEmpty) {
    throw const FormatException('Le tag ne contient aucun identifiant.');
  }
  if (!RegExp(r'^[0-9a-fA-F]+$').hasMatch(compact)) {
    throw const FormatException('Identifiant de carte invalide.');
  }
  return compact.toUpperCase();
}
