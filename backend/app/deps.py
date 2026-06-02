from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User, Role
from .security import decode_token

bearer = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_doctor(user: User = Depends(get_current_user)) -> User:
    if user.role != Role.doctor:
        raise HTTPException(status_code=403, detail="Doctor role required")
    return user


def require_pharmacist(user: User = Depends(get_current_user)) -> User:
    if user.role != Role.pharmacist:
        raise HTTPException(status_code=403, detail="Pharmacist role required")
    return user
