import bcrypt
import hashlib
import secrets
import string
import logging
from typing import Optional, Tuple

# Setup logger
logger = logging.getLogger(__name__)

def _pre_hash(password: str) -> bytes:
    """
    Pre-hash the password using SHA-256.
    This converts any password length into a fixed 64-character hex string,
    which fits perfectly within Bcrypt's 72-byte limit.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest().encode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    try:
        # We must pre-hash the input to match how it was stored
        hashed_input = _pre_hash(plain_password)
        # Convert hashed_password from string to bytes if needed
        if isinstance(hashed_password, str):
            hashed_password_bytes = hashed_password.encode('utf-8')
        else:
            hashed_password_bytes = hashed_password
            
        return bcrypt.checkpw(hashed_input, hashed_password_bytes)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Enforce length limit in our code
    if len(password) > 128:
        raise ValueError("Password must be shorter than 128 characters")
    
    # 1. Pre-hash with SHA-256 to bypass length limit
    hashed_input = _pre_hash(password)
    
    # 2. Salt and hash with Bcrypt directly (bypassing passlib)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(hashed_input, salt)
    
    # Return as string
    return hashed.decode('utf-8')

def generate_secure_password(length: int = 16) -> str:
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Updated limit to 128 characters matching schema
    if len(password) > 128:
        return False, "Password must be shorter than 128 characters"
        
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    if not any(c in string.punctuation for c in password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"

def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def sanitize_input(input_string: str) -> str:
    """Basic input sanitization"""
    if not input_string:
        return ""
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", ';', '(', ')', '&', '|']
    for char in dangerous_chars:
        input_string = input_string.replace(char, '')
    # Trim whitespace
    input_string = input_string.strip()
    return input_string
