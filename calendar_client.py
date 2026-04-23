"""calendar_client.py — creates a follow-up all-day event in Google Calendar
14 days after each application is sent."""

from datetime import datetime, timedelta
from googleapiclient.discovery import build
import google_auth
import config


def _build_service():
    return build("calendar", "v3", credentials=google_auth.get_credentials())


def create_followup_event(company: dict) -> str:
    """Create a follow-up reminder event and return its event ID."""
    service     = _build_service()
    follow_date = (datetime.now() + timedelta(days=config.FOLLOW_UP_DAYS)).strftime(
        "%Y-%m-%d"
    )

    event = {
        "summary": f"🔔 Relance : {company['name']}",
        "description": (
            f"Candidature spontanée envoyée le {datetime.now().strftime('%d.%m.%Y')}.\n\n"
            f"Entreprise : {company['name']}\n"
            f"Site       : {company.get('website', 'N/A')}\n"
            f"Contact    : {company.get('contact_name') or 'N/A'} "
            f"<{company.get('contact_email', 'N/A')}>\n\n"
            f"Pourquoi postulé :\n{company.get('why_good_fit', '')}\n\n"
            "✅ Action : envoyer un e-mail de relance poli si pas de réponse."
        ),
        "start": {"date": follow_date},
        "end":   {"date": follow_date},
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email",  "minutes": 9 * 60},   # 9 h du matin
                {"method": "popup",  "minutes": 9 * 60},
            ],
        },
        "colorId": "5",  # banana yellow — stands out
    }

    result = (
        service.events()
        .insert(calendarId=config.CALENDAR_ID, body=event)
        .execute()
    )
    return result["id"]
