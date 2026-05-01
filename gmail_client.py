"""gmail_client.py — creates Gmail drafts (or sends directly when AUTO_SEND=true)
with the cover letter as body and Vincent's CV as attachment."""

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text   import MIMEText
from email.mime.application import MIMEApplication
from googleapiclient.discovery import build
import google_auth
import config


def _build_service():
    return build("gmail", "v1", credentials=google_auth.get_gmail_credentials())


def _build_message(company: dict, cover_letter: str) -> str:
    """Construct the raw RFC-2822 email and return base64url-encoded string."""
    msg = MIMEMultipart()
    msg["To"]   = company["contact_email"]
    msg["From"] = config.GMAIL_ADDRESS
    msg["Subject"] = (
        f"Candidature spontanée — Community Manager / Spécialiste IA | Vincent Oppong"
    )

    # Cover letter as plain-text body
    msg.attach(MIMEText(cover_letter, "plain", "utf-8"))

    import os as os_module

    attachments = [
        (config.CV_FILE_PATH,         "CV_Vincent_Oppong.pdf"),
        (config.CERT_NUMERIQUES_PATH, "Certificats_numériques.pdf"),
        (config.CERT_TRAVAIL_PATH,    "Certificats_de_travail.pdf"),
    ]
    for path, filename in attachments:
        if os_module.path.exists(path):
            with open(path, "rb") as f:
                data = f.read()
            part = MIMEApplication(data, _subtype="pdf")
            part.add_header("Content-Disposition", "attachment", filename=filename)
            msg.attach(part)
        else:
            print(f"   ⚠️  Attachment not found, skipping: {path}")

    return base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")


def create_draft_or_send(company: dict, cover_letter: str) -> dict:
    """
    If AUTO_SEND=false (default): creates a Gmail draft for Vincent to review.
    If AUTO_SEND=true: sends immediately.
    Returns {"type": "draft"|"sent", "id": <str>}
    """
    service = _build_service()
    raw     = _build_message(company, cover_letter)

    if config.AUTO_SEND:
        result = service.users().messages().send(
            userId="me",
            body={"raw": raw},
        ).execute()
        return {"type": "sent", "id": result["id"]}
    else:
        result = service.users().drafts().create(
            userId="me",
            body={"message": {"raw": raw}},
        ).execute()
        return {"type": "draft", "id": result["id"]}
