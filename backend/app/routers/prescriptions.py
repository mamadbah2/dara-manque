from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_db, require_pharmacist
from ..models import Prescription, PrescriptionStatus, User
from ..schemas import PrescriptionResponse

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])


@router.patch("/{prescription_id}/treat", response_model=PrescriptionResponse)
def treat_prescription(
    prescription_id: UUID,
    db: Session = Depends(get_db),
    pharmacist: User = Depends(require_pharmacist),
):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    if prescription.status == PrescriptionStatus.treated:
        raise HTTPException(status_code=400, detail="Prescription already treated")
    prescription.status = PrescriptionStatus.treated
    db.commit()
    db.refresh(prescription)
    return PrescriptionResponse(
        id=prescription.id, created_at=prescription.created_at,
        medications=prescription.medications, status=prescription.status,
        doctor_name=prescription.doctor.full_name,
    )
