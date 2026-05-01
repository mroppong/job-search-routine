"""Shared Google authentication — service account for Vertex AI / Sheets / Calendar,
OAuth 2.0 user credentials for Gmail (personal account requires user consent)."""

import base64
import json
import os

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import config

# ── Scopes ───────────────────────────────────────────────────────────────────

SHEETS_CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar",
]

VERTEX_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
]

# ── Service account (Vertex AI, Sheets, Calendar) ────────────────────────────

LOCAL_KEY_PATH = os.path.join(os.path.dirname(__file__), "service_account.json")


def _load_service_account_info():
    if config.SERVICE_ACCOUNT_JSON:
        decoded = base64.b64decode(config.SERVICE_ACCOUNT_JSON).decode("utf-8")
        return json.loads(decoded)
    if os.path.exists(LOCAL_KEY_PATH):
        with open(LOCAL_KEY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    raise RuntimeError(
        "No service account credentials found: set SERVICE_ACCOUNT_JSON env var "
        f"or place service_account.json at {LOCAL_KEY_PATH}"
    )


def get_credentials():
    """Service account credentials for Sheets and Calendar."""
    return service_account.Credentials.from_service_account_info(
        _load_service_account_info(), scopes=SHEETS_CALENDAR_SCOPES
    )


def get_vertex_credentials():
    """Service account credentials for Vertex AI (Gemini)."""
    return service_account.Credentials.from_service_account_info(
        _load_service_account_info(), scopes=VERTEX_SCOPES
    )


# ── OAuth 2.0 (Gmail — personal account) ─────────────────────────────────────

TOKEN_PATH = os.path.join(os.path.dirname(__file__), "token.json")
CLIENT_SECRETS_PATH = os.path.join(os.path.dirname(__file__), "client_secrets.json")


def get_gmail_credentials() -> Credentials:
    """OAuth 2.0 user credentials for Gmail.

    On Railway: built from GMAIL_REFRESH_TOKEN / GMAIL_CLIENT_ID / GMAIL_CLIENT_SECRET
    env vars set via auth_setup.py.
    Locally: loads / refreshes token.json, running the interactive browser flow
    the first time.
    """
    # --- Railway / env-var path ---
    refresh_token = os.environ.get("GMAIL_REFRESH_TOKEN")
    if refresh_token:
        creds = Credentials(
            token=os.environ.get("GMAIL_TOKEN"),
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ.get("GMAIL_CLIENT_ID"),
            client_secret=os.environ.get("GMAIL_CLIENT_SECRET"),
            scopes=GMAIL_SCOPES,
        )
        if not creds.valid:
            creds.refresh(Request())
        return creds

    # --- Local path: token.json ---
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, GMAIL_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_PATH, GMAIL_SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w", encoding="utf-8") as fh:
            fh.write(creds.to_json())

    return creds
