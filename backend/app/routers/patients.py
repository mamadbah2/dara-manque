import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_db, require_doctor
from ..models import User, Patient, Prescription, PrescriptionStatus
from ..schemas import PatientResponse, ConsultationResponse, PrescriptionResponse, PrescriptionCreate

router = APIRouter(prefix="/patients", tags=["patients"])


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
    prescription = Prescription(
        id=uuid.uuid4(), patient_id=patient_id, doctor_id=doctor.id,
        created_at=datetime.utcnow(), medications=body.medications,
        status=PrescriptionStatus.active,
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    return PrescriptionResponse(
        id=prescription.id, created_at=prescription.created_at,
        medications=prescription.medications, status=prescription.status,
        doctor_name=doctor.full_name,
    )
