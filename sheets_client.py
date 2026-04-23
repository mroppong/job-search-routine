"""sheets_client.py — reads previously contacted companies from the Google Sheet
and appends new application rows after each outreach."""

from datetime import datetime
from googleapiclient.discovery import build
import google_auth
import config


def _build_service():
    return build("sheets", "v4", credentials=google_auth.get_credentials())


# ── Setup ────────────────────────────────────────────────────────────────────

HEADERS = [
    "Date envoi",
    "Entreprise",
    "Poste visé",
    "Ville",
    "Site web",
    "Contact",
    "Email contact",
    "Statut",
    "Date relance",
    "Pourquoi bonne cible",
    "Gmail Draft/Message ID",
]


def ensure_sheet_headers():
    """Write column headers on first run if the sheet is empty."""
    service = _build_service()
    result  = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=config.SPREADSHEET_ID, range="Applications!A1:K1")
        .execute()
    )
    if not result.get("values"):
        service.spreadsheets().values().update(
            spreadsheetId=config.SPREADSHEET_ID,
            range="Applications!A1",
            valueInputOption="RAW",
            body={"values": [HEADERS]},
        ).execute()
        print("   📋  Sheet headers initialised.")


# ── Read ─────────────────────────────────────────────────────────────────────

def get_contacted_companies() -> list[str]:
    """Return the list of company names already in the sheet (column B)."""
    service = _build_service()
    result  = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=config.SPREADSHEET_ID, range="Applications!B2:B")
        .execute()
    )
    return [row[0] for row in result.get("values", []) if row]


# ── Write ────────────────────────────────────────────────────────────────────

def add_application(
    company: dict,
    message_id: str,
    follow_up_date: str,
    status: str = "Draft créé",
):
    """Append a new row for today's application."""
    service = _build_service()
    today   = datetime.now().strftime("%Y-%m-%d")

    row = [
        today,
        company["name"],
        "Community Manager / Spécialiste IA",
        company.get("city", ""),
        company.get("website", ""),
        company.get("contact_name") or "",
        company.get("contact_email", ""),
        status,
        follow_up_date,
        company.get("why_good_fit", ""),
        message_id,
    ]

    service.spreadsheets().values().append(
        spreadsheetId=config.SPREADSHEET_ID,
        range="Applications!A:K",
        valueInputOption="RAW",
        body={"values": [row]},
    ).execute()


def update_status(company_name: str, new_status: str):
    """Scan column B for company_name and update column H (Statut)."""
    service = _build_service()
    result  = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=config.SPREADSHEET_ID, range="Applications!B:B")
        .execute()
    )
    rows = result.get("values", [])
    for i, row in enumerate(rows, start=1):
        if row and row[0] == company_name:
            service.spreadsheets().values().update(
                spreadsheetId=config.SPREADSHEET_ID,
                range=f"Applications!H{i}",
                valueInputOption="RAW",
                body={"values": [[new_status]]},
            ).execute()
            return
