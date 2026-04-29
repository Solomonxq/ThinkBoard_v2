from datetime import timedelta

import jwt
from app.core.config import settings
from app.utils.time import utcnow
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret_key = settings.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = settings.algorithm
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False

def create_token(data: dict) -> str:
    to_encode = data.copy()
    expire = utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, secret_key, ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def create_refresh_token(data:dict) -> str:
    to_encode = data.copy()
    expire = utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, secret_key, ALGORITHM)


def decode_refresh_token(token: str) -> dict | None:
    payload = decode_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None



