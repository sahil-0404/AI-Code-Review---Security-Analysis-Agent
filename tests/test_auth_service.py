from backend.services import auth_service


def test_signup_and_login_persisted_in_sqlite(tmp_path, monkeypatch):
    monkeypatch.setattr(auth_service, "AUTH_DB_PATH", tmp_path / "users.sqlite3")

    created = auth_service.create_user("Test User", "test@example.com", "secure-password")

    assert created["email"] == "test@example.com"
    assert auth_service.authenticate_user("test@example.com", "secure-password")["name"] == "Test User"
    assert auth_service.authenticate_user("test@example.com", "wrong-password") is None
