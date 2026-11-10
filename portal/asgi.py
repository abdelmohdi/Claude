"""Entry point for a production server: uvicorn portal.asgi:app"""
import os

from .app import create_app

app = create_app(os.environ.get("PORTAL_DB", "portal.sqlite3"))
