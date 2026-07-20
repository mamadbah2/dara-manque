from fastapi import APIRouter, Depends

from ..deps import get_current_user
from ..models import User
from . import engine

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/affluence")
def affluence(_: User = Depends(get_current_user)):
    """Prévision d'affluence hospitalière sur 30 jours (dataset de démonstration)."""
    return engine.predict_affluence()


@router.get("/fraud")
def fraud(_: User = Depends(get_current_user)):
    """Patients au comportement atypique (nomadisme médical) — dataset de démo."""
    return engine.detect_fraud()
