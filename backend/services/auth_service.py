import hashlib
import hmac
import os
import sqlite3
from datetime import datetime, timezone

from backend.config import AUTH_DB_PATH

ITERATIONS = 260_000


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(AUTH_DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE COLLATE NOCASE,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_at TEXT NOT NULL
        )"""
    )
    return connection


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS).hex()


def create_user(name: str, email: str, password: str) -> dict:
    normalized_email = email.strip().lower()
    salt = os.urandom(16)
    with _connection() as connection:
        try:
            cursor = connection.execute(
                "INSERT INTO users (name, email, password_hash, salt, created_at) VALUES (?, ?, ?, ?, ?)",
                (name.strip(), normalized_email, _hash_password(password, salt), salt.hex(), datetime.now(timezone.utc).isoformat()),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("An account already exists for this email address.") from exc
    return {"id": cursor.lastrowid, "name": name.strip(), "email": normalized_email}


def authenticate_user(email: str, password: str) -> dict | None:
    with _connection() as connection:
        user = connection.execute("SELECT id, name, email, password_hash, salt FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
    if not user:
        return None
    candidate = _hash_password(password, bytes.fromhex(user["salt"]))
    if not hmac.compare_digest(candidate, user["password_hash"]):
        return None
    return {"id": user["id"], "name": user["name"], "email": user["email"]}
