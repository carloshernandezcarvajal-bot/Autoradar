from cryptography.fernet import Fernet
import base64
import hashlib

from app.config import settings


def _get_fernet() -> Fernet:
    key = hashlib.sha256(settings.encryption_key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_plate(plate: str) -> str:
    f = _get_fernet()
    return f.encrypt(plate.encode()).decode()


def decrypt_plate(encrypted: str) -> str:
    f = _get_fernet()
    return f.decrypt(encrypted.encode()).decode()
