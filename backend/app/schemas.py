from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from .models import PrescriptionStatus


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str


class PatientResponse(BaseModel):
    id: int
    full_name: str
    date_of_birth: Optional[date] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None

    model_config = {"from_attributes": True}


class ConsultationResponse(BaseModel):
    id: UUID
    date: datetime
    notes: Optional[str] = None
    diagnosis: Optional[str] = None
    doctor_name: str


class PrescriptionResponse(BaseModel):
    id: UUID
    created_at: datetime
    medications: str
    status: PrescriptionStatus
    doctor_name: str


class PrescriptionCreate(BaseModel):
    medications: str
    override_allergy: bool = False


class AllergyConflict(BaseModel):
    allergen_class: str
    allergy_term: str
    medication_term: str


class AllergyCheckRequest(BaseModel):
    medications: str


class AllergyCheckResponse(BaseModel):
    conflicts: list[AllergyConflict]
