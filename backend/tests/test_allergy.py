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


def test_check_endpoint_detects_cross_reactivity(client, patient, doctor, doctor_token):
    res = client.post(
        f"/patients/{patient.id}/prescriptions/check",
        json={"medications": "Amoxicilline 500mg"},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 200
    conflicts = res.json()["conflicts"]
    assert len(conflicts) == 1
    assert conflicts[0]["allergen_class"] == "Pénicilline"


def test_check_endpoint_no_conflict(client, patient, doctor, doctor_token):
    res = client.post(
        f"/patients/{patient.id}/prescriptions/check",
        json={"medications": "Paracétamol 1g"},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 200
    assert res.json()["conflicts"] == []


def test_check_endpoint_requires_doctor(client, patient, pharmacist, pharmacist_token):
    res = client.post(
        f"/patients/{patient.id}/prescriptions/check",
        json={"medications": "Amoxicilline"},
        headers={"Authorization": f"Bearer {pharmacist_token}"},
    )
    assert res.status_code == 403


def test_check_endpoint_patient_not_found(client, doctor, doctor_token):
    res = client.post(
        "/patients/9999/prescriptions/check",
        json={"medications": "Amoxicilline"},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 404


def test_create_blocked_on_conflict(client, patient, doctor, doctor_token, db):
    from app.models import Prescription
    res = client.post(
        f"/patients/{patient.id}/prescriptions",
        json={"medications": "Amoxicilline 500mg"},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 409
    assert res.json()["detail"]["conflicts"][0]["allergen_class"] == "Pénicilline"
    # Aucune ordonnance ne doit avoir été créée
    assert db.query(Prescription).count() == 0


def test_create_allowed_with_override(client, patient, doctor, doctor_token, db):
    from app.models import Prescription
    res = client.post(
        f"/patients/{patient.id}/prescriptions",
        json={"medications": "Amoxicilline 500mg", "override_allergy": True},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 201
    p = db.query(Prescription).one()
    assert p.allergy_override is not None
    assert "amoxicilline" in p.allergy_override


def test_create_no_conflict_succeeds(client, patient, doctor, doctor_token, db):
    from app.models import Prescription
    res = client.post(
        f"/patients/{patient.id}/prescriptions",
        json={"medications": "Paracétamol 1g"},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 201
    p = db.query(Prescription).one()
    assert p.allergy_override is None
