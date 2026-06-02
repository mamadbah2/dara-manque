import uuid
import enum
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Date, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base


class Role(str, enum.Enum):
    doctor = "doctor"
    pharmacist = "pharmacist"


class PrescriptionStatus(str, enum.Enum):
    active = "active"
    treated = "treated"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)
    full_name = Column(String, nullable=False)


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    allergies = Column(Text, nullable=True)
    chronic_conditions = Column(Text, nullable=True)

    consultations = relationship("Consultation", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
    diagnosis = Column(String, nullable=True)

    patient = relationship("Patient", back_populates="consultations")
    doctor = relationship("User")


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    medications = Column(Text, nullable=False)
    status = Column(Enum(PrescriptionStatus), nullable=False, default=PrescriptionStatus.active)

    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("User")
