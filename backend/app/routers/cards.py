from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..models import Patient
from ..schemas import CardScanRequest, CardScanResponse, LastScanResponse, PatientResponse
from ..card_utils import normalize_uid
from ..scan_state import record_scan, get_last_scan

router = APIRouter(prefix="/cards", tags=["cards"])


@router.post("/scan", response_model=CardScanResponse)
def scan_card(body: CardScanRequest, db: Session = Depends(get_db)):
    """Called by the hardware reader (ESP32 + RC522) when a card is deposited.

    Resolves the card's UID to a patient and records the scan so the web
    dashboard (which polls /cards/last-scan) can react. `known=false` means the
    card is not yet associated with any patient (candidate for enrollment).
    """
    uid = normalize_uid(body.uid)
    patient = db.query(Patient).filter(Patient.card_uid == uid).first()
    record_scan(uid, patient is not None, patient.id if patient else None)
    return CardScanResponse(
        uid=uid,
        known=patient is not None,
        patient=PatientResponse.model_validate(patient) if patient else None,
    )


@router.get("/last-scan", response_model=LastScanResponse)
def last_scan(db: Session = Depends(get_db)):
    """Polled by the web dashboard to learn what card was last presented on the
    reader. React when `seq` changes: `known` -> open the patient record,
    otherwise -> open the enrollment form prefilled with `uid`."""
    s = get_last_scan()
    patient = None
    if s["patient_id"] is not None:
        patient = db.query(Patient).filter(Patient.id == s["patient_id"]).first()
    return LastScanResponse(
        seq=s["seq"],
        uid=s["uid"],
        known=s["known"],
        patient=PatientResponse.model_validate(patient) if patient else None,
    )
