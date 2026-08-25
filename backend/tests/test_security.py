from app.core.security import hash_password, verify_password


def test_password_round_trip():
    password = "StrongPass123!"
    hashed = hash_password(password)
    assert hashed.startswith("$argon2")
    assert verify_password(password, hashed)
    assert not verify_password("WrongPass123!", hashed)


def test_invalid_legacy_hash_is_safe():
    assert verify_password("password", "not-a-valid-argon2-hash") is False
