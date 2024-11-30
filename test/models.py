from typing import List, Dict
import hashlib

class User:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password for secure storage."""
        return hashlib.sha256(password.encode()).hexdigest()
