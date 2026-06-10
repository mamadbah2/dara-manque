import re
import unicodedata

# Chaque classe regroupe TOUS ses termes (nom de classe + médicaments membres +
# orthographes), en forme normalisée (minuscules, sans accents). La cross-réactivité
# tombe d'elle-même : allergie et médicament n'ont qu'à matcher la même classe.
ALLERGEN_CLASSES: dict[str, list[str]] = {
    "Pénicilline": [
        "penicilline", "amoxicilline", "ampicilline", "augmentin",
        "clamoxyl", "oxacilline", "cloxacilline",
    ],
    "Aspirine/AINS": [
        "aspirine", "acide acetylsalicylique", "aspegic", "ibuprofene",
        "diclofenac", "ketoprofene", "ains",
    ],
    "Sulfamides": [
        "sulfamide", "sulfamethoxazole", "bactrim", "cotrimoxazole",
    ],
    "Céphalosporines": [
        "cephalosporine", "ceftriaxone", "cefixime", "cefuroxime",
    ],
    "Codéine": [
        "codeine", "dafalgan codeine", "tramadol",
    ],
    "Iode": [
        "iode", "produit de contraste iode", "povidone iodee", "betadine",
    ],
}


def _normalize(text: str | None) -> str:
    """Minuscules, accents retirés, ponctuation → espaces, espaces compressés."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def _contains(haystack_norm: str, term: str) -> bool:
    """Correspondance sur mots entiers (gère les termes multi-mots)."""
    term_norm = _normalize(term)
    if not term_norm:
        return False
    return f" {term_norm} " in f" {haystack_norm} "


def check_allergy_conflicts(
    allergies_text: str | None, medications_text: str | None
) -> list[dict]:
    """Retourne la liste des conflits allergie↔médicament détectés."""
    allergies = _normalize(allergies_text)
    meds = _normalize(medications_text)
    if not allergies or not meds:
        return []

    conflicts: list[dict] = []
    for class_name, terms in ALLERGEN_CLASSES.items():
        allergy_term = next((t for t in terms if _contains(allergies, t)), None)
        if allergy_term is None:
            continue
        med_term = next((t for t in terms if _contains(meds, t)), None)
        if med_term is None:
            continue
        conflicts.append({
            "allergen_class": class_name,
            "allergy_term": allergy_term,
            "medication_term": med_term,
        })
    return conflicts
