"""Shared Google Service Account authentication — builds credentials
covering Gmail, Sheets and Calendar scopes using a JSON key file."""

from google.oauth2 import service_account
import config

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar",
]


def get_credentials():
    """Load credentials from SERVICE_ACCOUNT_JSON env var (base64-encoded)."""
    import json
    import base64
    
    # Decode the base64 service account JSON from env
    encoded = config.SERVICE_ACCOUNT_JSON
    decoded = base64.b64decode(encoded).decode('utf-8')
    service_account_info = json.loads(decoded)
    
    creds = service_account.Credentials.from_service_account_info(
        service_account_info, 
        scopes=SCOPES
    )
    return creds

