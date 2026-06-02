import uuid
from datetime import datetime
from app.models import Prescription, PrescriptionStatus


def test_get_patient(client, patient):
    res = client.get(f"/patients/{patient.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1001
    assert data["full_name"] == "Mamadou Diallo"
    assert data["allergies"] == "Pénicilline"


def test_get_patient_not_found(client):
    res = client.get("/patients/9999")
    assert res.status_code == 404


def test_get_prescriptions_empty(client, patient):
    res = client.get(f"/patients/{patient.id}/prescriptions")
    assert res.status_code == 200
    assert res.json() == []


def test_create_prescription(client, patient, doctor_token):
    res = client.post(
        f"/patients/{patient.id}/prescriptions",
        json={"medications": "Paracetamol 1g - 3x/jour"},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["medications"] == "Paracetamol 1g - 3x/jour"
    assert data["status"] == "active"


def test_get_prescriptions_returns_active_only(client, patient, doctor, db, doctor_token):
    p_active = Prescription(
        id=uuid.uuid4(), patient_id=patient.id, doctor_id=doctor.id,
        created_at=datetime.utcnow(), medications="Actif", status=PrescriptionStatus.active
    )
    p_treated = Prescription(
        id=uuid.uuid4(), patient_id=patient.id, doctor_id=doctor.id,
        created_at=datetime.utcnow(), medications="Traité", status=PrescriptionStatus.treated
    )
    db.add_all([p_active, p_treated])
    db.commit()

    res = client.get(f"/patients/{patient.id}/prescriptions")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["medications"] == "Actif"


def test_create_prescription_requires_doctor(client, patient, pharmacist_token):
    res = client.post(
        f"/patients/{patient.id}/prescriptions",
        json={"medications": "Test"},
        headers={"Authorization": f"Bearer {pharmacist_token}"},
    )
    assert res.status_code == 403


def test_create_prescription_no_auth(client, patient):
    res = client.post(
        f"/patients/{patient.id}/prescriptions",
        json={"medications": "Test"},
    )
    assert res.status_code in (401, 403)


def test_get_consultations_empty(client, patient):
    res = client.get(f"/patients/{patient.id}/consultations")
    assert res.status_code == 200
    assert res.json() == []
