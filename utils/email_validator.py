import re
from typing import Optional


class EmailValidator:
    """Email validation utility"""
    
    # RFC 5322 compliant email regex
    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    )
    
    # Common disposable email domains
    DISPOSABLE_DOMAINS = {
        "tempmail.com", "guerrillamail.com", "mailinator.com", "10minutemail.com",
        "throwawaymail.com", "yopmail.com", "temp-mail.org", "fakeinbox.com",
        "sharklasers.com", "getairmail.com", "maildrop.cc", "trashmail.com"
    }
    
    @classmethod
    def is_valid_format(cls, email: str) -> bool:
        """Check if email has valid format"""
        return bool(cls.EMAIL_REGEX.match(email))
    
    @classmethod
    def is_disposable(cls, email: str) -> bool:
        """Check if email is from a disposable email service"""
        domain = email.split('@')[-1].lower()
        return domain in cls.DISPOSABLE_DOMAINS
    
    @classmethod
    def validate(cls, email: str) -> tuple[bool, Optional[str]]:
        """Validate email address"""
        if not email:
            return False, "Email is required"
        
        if not cls.is_valid_format(email):
            return False, "Invalid email format"
        
        if cls.is_disposable(email):
            return False, "Disposable email addresses are not allowed"
        
        # Check for common typos
        common_typos = {
            "gmial.com": "gmail.com",
            "gmal.com": "gmail.com",
            "gmail.cmo": "gmail.com",
            "gmail.con": "gmail.com",
            "yahooo.com": "yahoo.com",
            "yaho.com": "yahoo.com",
            "hotmal.com": "hotmail.com",
            "hotmai.com": "hotmail.com",
            "outlok.com": "outlook.com",
            "outllok.com": "outlook.com"
        }
        
        domain = email.split('@')[-1].lower()
        if domain in common_typos:
            suggestion = common_typos[domain]
            return False, f"Did you mean @{suggestion} instead of @{domain}?"
        
        return True, None
    
    @classmethod
    def normalize(cls, email: str) -> str:
        """Normalize email address (lowercase, trim)"""
        return email.strip().lower()
