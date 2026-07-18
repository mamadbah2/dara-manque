from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..models import Patient
from ..schemas import CardScanRequest, CardScanResponse, PatientResponse
from ..card_utils import normalize_uid

router = APIRouter(prefix="/cards", tags=["cards"])


@router.post("/scan", response_model=CardScanResponse)
def scan_card(body: CardScanRequest, db: Session = Depends(get_db)):
    """Called by the hardware reader (ESP32 + RC522) when a card is deposited.

    Resolves the card's UID to a patient. `known=false` means the card is not
    yet associated with any patient (candidate for enrollment).
    """
    uid = normalize_uid(body.uid)
    patient = db.query(Patient).filter(Patient.card_uid == uid).first()
    return CardScanResponse(
        uid=uid,
        known=patient is not None,
        patient=PatientResponse.model_validate(patient) if patient else None,
    )
