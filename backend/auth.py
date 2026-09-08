import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = os.environ.get("MEDICAL_VA_SECRET_KEY")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS = {
    "va_joy": {"display_name": "VA Joy", "role": "va", "password_hash_env": "VA_JOY_PASSWORD_HASH"},
    "employer": {"display_name": "Employer", "role": "employer", "password_hash_env": "EMPLOYER_PASSWORD_HASH"},
}

def _secret():
    if not SECRET_KEY or SECRET_KEY == "CHANGE_THIS_IN_SERVER_ENVIRONMENT":
        raise RuntimeError("MEDICAL_VA_SECRET_KEY is not configured")
    return SECRET_KEY

def _password_hash(username: str):
    user = USERS.get(username)
    if not user: return None
    return os.environ.get(user["password_hash_env"])

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_user(username: str, password: str) -> bool:
    stored = _password_hash(username)
    return bool(stored and pwd_context.verify(password, stored))

def create_access_token(subject: str, minutes: int = 480) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode({"sub": subject, "exp": expire}, _secret(), algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[str]:
    try:
        return jwt.decode(token, _secret(), algorithms=[ALGORITHM]).get("sub")
    except Exception:
        return None
