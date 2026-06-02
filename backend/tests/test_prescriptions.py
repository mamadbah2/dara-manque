import uuid
from datetime import datetime
from app.models import Prescription, PrescriptionStatus


def _create_prescription(db, patient, doctor):
    p = Prescription(
        id=uuid.uuid4(), patient_id=patient.id, doctor_id=doctor.id,
        created_at=datetime.utcnow(), medications="Ibuprofène 400mg",
        status=PrescriptionStatus.active,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_treat_prescription(client, patient, doctor, pharmacist, db, doctor_token, pharmacist_token):
    p = _create_prescription(db, patient, doctor)
    res = client.patch(
        f"/prescriptions/{p.id}/treat",
        headers={"Authorization": f"Bearer {pharmacist_token}"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "treated"


def test_treat_already_treated(client, patient, doctor, pharmacist, db, pharmacist_token):
    p = _create_prescription(db, patient, doctor)
    client.patch(f"/prescriptions/{p.id}/treat", headers={"Authorization": f"Bearer {pharmacist_token}"})
    res = client.patch(f"/prescriptions/{p.id}/treat", headers={"Authorization": f"Bearer {pharmacist_token}"})
    assert res.status_code == 400


def test_treat_not_found(client, pharmacist_token):
    res = client.patch(
        f"/prescriptions/{uuid.uuid4()}/treat",
        headers={"Authorization": f"Bearer {pharmacist_token}"},
    )
    assert res.status_code == 404


def test_treat_requires_pharmacist(client, patient, doctor, db, doctor_token):
    p = _create_prescription(db, patient, doctor)
    res = client.patch(
        f"/prescriptions/{p.id}/treat",
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 403
