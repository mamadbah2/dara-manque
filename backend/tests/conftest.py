import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.deps import get_db
from app.models import User, Patient, Prescription, Consultation, Role, PrescriptionStatus
from app.security import hash_password
from datetime import datetime

TEST_DB_URL = "postgresql://postgres:postgres@localhost/test_dara_manque"
engine = create_engine(TEST_DB_URL)
TestingSession = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(setup_db):
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override():
        yield db
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def doctor(db):
    user = User(
        id=uuid.uuid4(),
        email="doctor@test.com",
        password_hash=hash_password("password123"),
        role=Role.doctor,
        full_name="Dr. Aminata Sow",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def pharmacist(db):
    user = User(
        id=uuid.uuid4(),
        email="pharmacist@test.com",
        password_hash=hash_password("password123"),
        role=Role.pharmacist,
        full_name="Pharmacien Ibrahima Ba",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def patient(db):
    p = Patient(
        id=1001,
        full_name="Mamadou Diallo",
        allergies="Pénicilline",
        chronic_conditions="Diabète type 2",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@pytest.fixture
def doctor_token(client, doctor):
    res = client.post("/auth/login", json={"email": "doctor@test.com", "password": "password123"})
    return res.json()["access_token"]


@pytest.fixture
def pharmacist_token(client, pharmacist):
    res = client.post("/auth/login", json={"email": "pharmacist@test.com", "password": "password123"})
    return res.json()["access_token"]
