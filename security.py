import bcrypt
from passlib.context import CryptContext
import hashlib
import os

# Set up password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password for storing.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a stored password against one provided by user
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate a new hashed password
    """
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + key.hex()

def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Verify a stored password against one provided by user
    """
    salt = bytes.fromhex(stored_password[:64])
    stored_key = stored_password[64:]
    new_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000).hex()
    return new_key == stored_key
