import os
import base64
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import text
from .database import engine

SECRET_KEY = os.environ.get("MEDICAL_VA_SECRET_KEY")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS = {
    "va_joy": {"display_name": "VA Joy", "role": "va"},
    "employer": {"display_name": "Employer", "role": "employer"},
}


def _secret():
    if not SECRET_KEY or SECRET_KEY == "CHANGE_THIS_IN_SERVER_ENVIRONMENT":
        raise RuntimeError("MEDICAL_VA_SECRET_KEY is not configured")
    return SECRET_KEY


def _credential_hash():
    try:
        with engine.connect() as conn:
            return conn.execute(text("select password_hash from public.medical_va_credentials where id = 1")).scalar()
    except Exception:
        return None


def _verify_workspace_password(password: str) -> bool:
    stored = _credential_hash()
    if not stored or "." not in stored:
        return False
    try:
        salt_b64, digest_b64 = stored.split(".", 1)
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_user(username: str, password: str) -> bool:
    if username not in USERS:
        return False
    if _verify_workspace_password(password):
        return True
    return False


def create_access_token(subject: str, minutes: int = 480) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode({"sub": subject, "exp": expire}, _secret(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    try:
        return jwt.decode(token, _secret(), algorithms=[ALGORITHM]).get("sub")
    except Exception:
        return None
