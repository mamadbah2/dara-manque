import uuid
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Base, User, Patient, Consultation, Prescription, PrescriptionStatus, Role
from app.security import hash_password
from datetime import datetime, date

Base.metadata.create_all(bind=engine)
db = SessionLocal()

db.query(Prescription).delete()
db.query(Consultation).delete()
db.query(Patient).delete()
db.query(User).delete()
db.commit()

doctor = User(
    id=uuid.uuid4(), email="doctor@dara.com",
    password_hash=hash_password("password123"),
    role=Role.doctor, full_name="Dr. Aminata Sow",
)
pharmacist = User(
    id=uuid.uuid4(), email="pharmacist@dara.com",
    password_hash=hash_password("password123"),
    role=Role.pharmacist, full_name="Pharmacien Ibrahima Ba",
)
db.add_all([doctor, pharmacist])
db.commit()

patient = Patient(
    id=1001, full_name="Mamadou Diallo",
    date_of_birth=date(1985, 3, 12),
    allergies="Pénicilline",
    chronic_conditions="Diabète type 2",
)
db.add(patient)
db.commit()

c1 = Consultation(
    id=uuid.uuid4(), patient_id=1001, doctor_id=doctor.id,
    date=datetime(2026, 4, 10, 9, 30),
    notes="Patient présente une fatigue chronique.",
    diagnosis="Anémie ferriprive",
)
c2 = Consultation(
    id=uuid.uuid4(), patient_id=1001, doctor_id=doctor.id,
    date=datetime(2026, 5, 20, 14, 0),
    notes="Contrôle diabète. Glycémie stable.",
    diagnosis="Suivi diabète",
)
db.add_all([c1, c2])

p1 = Prescription(
    id=uuid.uuid4(), patient_id=1001, doctor_id=doctor.id,
    created_at=datetime(2026, 5, 20, 14, 0),
    medications="Metformine 500mg - 2x/jour\nVitamine B12 - 1x/jour",
    status=PrescriptionStatus.active,
)
db.add(p1)
db.commit()

print("Seed complete!")
print("Doctor:      doctor@dara.com / password123")
print("Pharmacist:  pharmacist@dara.com / password123")
print("Patient ID:  1001")
