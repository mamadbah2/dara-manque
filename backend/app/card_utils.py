"""Helpers for NFC/RFID card UIDs.

The hardware reader (ESP32 + RC522) reads a card's intrinsic UID and may send
it in several textual shapes: lowercase/uppercase hex, with or without ':',
'-' or space separators. We normalise to a single canonical form so that a
card enrolled once is always resolved on later scans regardless of formatting.
"""


def normalize_uid(raw: str) -> str:
    """Return the canonical UID (compact, uppercase hex).

    Raises ValueError if the UID is empty after stripping separators.
    """
    if raw is None:
        raise ValueError("UID vide.")
    compact = raw.strip().replace(":", "").replace("-", "").replace(" ", "")
    if not compact:
        raise ValueError("UID vide.")
    return compact.upper()
