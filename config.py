"""Application configuration for the contact book web server."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Default settings for the Flask application."""

    BASE_DIR = str(BASE_DIR)
    CONTACTS_FILE = os.environ.get(
        "CONTACTS_FILE", str(BASE_DIR / "contacts.json")
    )
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    DEBUG = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}


class TestingConfig(Config):
    """Settings for isolated Flask test clients."""

    TESTING = True
