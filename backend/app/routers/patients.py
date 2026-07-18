import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_db, require_doctor
from ..models import User, Patient, Prescription, PrescriptionStatus
from ..schemas import (
    PatientResponse, ConsultationResponse, PrescriptionResponse,
    PrescriptionCreate, AllergyCheckRequest, AllergyCheckResponse, AllergyConflict,
    PatientCreate,
)
from ..allergy_rules import check_allergy_conflicts
from ..card_utils import normalize_uid

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(
    body: PatientCreate,
    db: Session = Depends(get_db),
    doctor: User = Depends(require_doctor),
):
    """Enroll a new patient. For now the doctor is the card issuer: an optional
    `card_uid` (read from the hardware reader) links the physical card to the
    dossier at creation time."""
    card_uid = normalize_uid(body.card_uid) if body.card_uid else None
    if card_uid and db.query(Patient).filter(Patient.card_uid == card_uid).first():
        raise HTTPException(status_code=409, detail="Carte déjà associée à un patient")

    patient = Patient(
        full_name=body.full_name,
        date_of_birth=body.date_of_birth,
        allergies=body.allergies,
        chronic_conditions=body.chronic_conditions,
        card_uid=card_uid,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/{patient_id}/consultations", response_model=list[ConsultationResponse])
def get_consultations(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return [
        ConsultationResponse(
            id=c.id, date=c.date, notes=c.notes,
            diagnosis=c.diagnosis, doctor_name=c.doctor.full_name
        )
        for c in patient.consultations
    ]


@router.get("/{patient_id}/prescriptions", response_model=list[PrescriptionResponse])
def get_prescriptions(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    active = [p for p in patient.prescriptions if p.status == PrescriptionStatus.active]
    return [
        PrescriptionResponse(
            id=p.id, created_at=p.created_at, medications=p.medications,
            status=p.status, doctor_name=p.doctor.full_name
        )
        for p in active
    ]


@router.post("/{patient_id}/prescriptions/check", response_model=AllergyCheckResponse)
def check_prescription(
    patient_id: int,
    body: AllergyCheckRequest,
    db: Session = Depends(get_db),
    doctor: User = Depends(require_doctor),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    conflicts = check_allergy_conflicts(patient.allergies, body.medications)
    return AllergyCheckResponse(
        conflicts=[AllergyConflict(**c) for c in conflicts]
    )


@router.post("/{patient_id}/prescriptions", response_model=PrescriptionResponse, status_code=201)
def create_prescription(
    patient_id: int,
    body: PrescriptionCreate,
    db: Session = Depends(get_db),
    doctor: User = Depends(require_doctor),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    conflicts = check_allergy_conflicts(patient.allergies, body.medications)
    if conflicts and not body.override_allergy:
        raise HTTPException(status_code=409, detail={"conflicts": conflicts})

    override_note = None
    if conflicts:
        override_note = "; ".join(
            f"{c['allergen_class']}: {c['medication_term']}" for c in conflicts
        )

    prescription = Prescription(
        id=uuid.uuid4(), patient_id=patient_id, doctor_id=doctor.id,
        created_at=datetime.utcnow(), medications=body.medications,
        status=PrescriptionStatus.active, allergy_override=override_note,
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    return PrescriptionResponse(
        id=prescription.id, created_at=prescription.created_at,
        medications=prescription.medications, status=prescription.status,
        doctor_name=doctor.full_name,
    )
