import pytest
from Backend.security import get_password_hash, verify_password

def test_password_hashing_correctness():
    password = "KhlFanPass123!"
    hashed = get_password_hash(password)
    
    # Assert that the hash is generated and is not the plain-text password
    assert hashed != password
    assert hashed.startswith("$2b$")  # Bcrypt identifier
    
    # Assert that verification works
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_empty_password_hashing():
    password = ""
    hashed = get_password_hash(password)
    assert verify_password("", hashed) is True
