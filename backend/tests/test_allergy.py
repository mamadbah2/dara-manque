from app.allergy_rules import check_allergy_conflicts


def test_exact_match():
    conflicts = check_allergy_conflicts("Pénicilline", "Pénicilline 1g")
    assert len(conflicts) == 1
    assert conflicts[0]["allergen_class"] == "Pénicilline"


def test_cross_reactivity_penicillin():
    # Allergique Pénicilline, on prescrit Amoxicilline (même classe, mot différent)
    conflicts = check_allergy_conflicts("Pénicilline", "Amoxicilline 500mg - 3x/jour")
    assert len(conflicts) == 1
    assert conflicts[0]["allergen_class"] == "Pénicilline"
    assert conflicts[0]["medication_term"] == "amoxicilline"


def test_case_and_accent_insensitive():
    conflicts = check_allergy_conflicts("penicilline", "AMOXICILLINE")
    assert len(conflicts) == 1


def test_no_conflict():
    conflicts = check_allergy_conflicts("Pénicilline", "Paracétamol 1g")
    assert conflicts == []


def test_empty_allergies():
    assert check_allergy_conflicts(None, "Amoxicilline") == []
    assert check_allergy_conflicts("", "Amoxicilline") == []


def test_empty_medications():
    assert check_allergy_conflicts("Pénicilline", "") == []


def test_multiple_allergies():
    conflicts = check_allergy_conflicts("Pénicilline, Aspirine", "Ibuprofène 400mg")
    assert len(conflicts) == 1
    assert conflicts[0]["allergen_class"] == "Aspirine/AINS"


def test_no_false_positive_substring():
    # "ains" ne doit PAS matcher dans "bains"
    conflicts = check_allergy_conflicts("Aspirine", "Sels pour bains de bouche")
    assert conflicts == []
