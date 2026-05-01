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


def _letter_to_html(letter_text: str) -> str:
    """Wrap plain-text letter paragraphs in HTML, append portfolio link and contact footer."""
    paragraphs = [p.strip() for p in letter_text.split("\n\n") if p.strip()]
    body_html = "\n".join(
        f"<p>{p.replace(chr(10), '<br>')}</p>" for p in paragraphs
    )

    portfolio_url = config.CANDIDATE["portfolio"]
    portfolio_block = (
        f'<p><em><a href="{portfolio_url}">'
        f"Pour consulter mon portfolio cliquez ici"
        f"</a></em></p>"
    )

    c = config.CANDIDATE
    contact_block = (
        f'<p style="margin-top:24px;color:#555;font-size:0.9em;line-height:1.6;">'
        f'{c["address"]}<br>'
        f'{c["phone"]}<br>'
        f'{c["email"]}'
        f"</p>"
    )

    return (
        '<html><body style="font-family:Arial,sans-serif;font-size:14px;color:#222;">\n'
        f"{body_html}\n{portfolio_block}\n{contact_block}\n"
        "</body></html>"
    )


def _build_message(company: dict, cover_letter: str) -> str:
    """Construct the raw RFC-2822 email and return base64url-encoded string."""
    msg = MIMEMultipart()
    msg["To"]   = company["contact_email"]
    msg["From"] = config.GMAIL_ADDRESS
    msg["Subject"] = (
        f"Candidature spontanée — Community Manager / Spécialiste IA | Vincent Oppong"
    )

    msg.attach(MIMEText(_letter_to_html(cover_letter), "html", "utf-8"))

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
    Returns {"type": "draft"|"sent", "id": <str>, "thread_id": <str>}
    """
    service = _build_service()
    raw     = _build_message(company, cover_letter)

    if config.AUTO_SEND:
        result = service.users().messages().send(
            userId="me",
            body={"raw": raw},
        ).execute()
        return {"type": "sent", "id": result["id"], "thread_id": result["threadId"]}
    else:
        result = service.users().drafts().create(
            userId="me",
            body={"message": {"raw": raw}},
        ).execute()
        # Drafts don't have a threadId until sent; use the draft message id as placeholder
        msg_id = result.get("message", {}).get("id", result["id"])
        return {"type": "draft", "id": result["id"], "thread_id": msg_id}


def has_reply(thread_id: str) -> bool:
    """Return True if the Gmail thread has a message from someone other than Vincent."""
    service  = _build_service()
    thread   = service.users().threads().get(
        userId="me", id=thread_id, format="metadata"
    ).execute()
    messages = thread.get("messages", [])
    if len(messages) <= 1:
        return False
    for msg in messages[1:]:
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        if config.GMAIL_ADDRESS not in headers.get("From", ""):
            return True
    return False


def send_followup(company: dict, body: str, thread_id: str, original_message_id: str) -> dict:
    """Send a follow-up email as a reply in the original thread."""
    service = _build_service()

    # Fetch RFC 2822 Message-ID and Subject from the original sent message
    orig = service.users().messages().get(
        userId="me", id=original_message_id, format="metadata",
        metadataHeaders=["Message-ID", "Subject"],
    ).execute()
    headers    = {h["name"]: h["value"] for h in orig["payload"]["headers"]}
    rfc_msg_id = headers.get("Message-ID", "")
    subject    = headers.get("Subject", "Candidature spontanée")

    # Build reply MIME — no attachments on follow-ups
    msg = MIMEMultipart()
    msg["To"]         = company["contact_email"]
    msg["From"]       = config.GMAIL_ADDRESS
    msg["Subject"]    = f"Re: {subject}"
    msg["In-Reply-To"] = rfc_msg_id
    msg["References"] = rfc_msg_id
    msg.attach(MIMEText(_letter_to_html(body), "html", "utf-8"))

    raw    = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    result = service.users().messages().send(
        userId="me",
        body={"raw": raw, "threadId": thread_id},
    ).execute()
    return {"type": "sent", "id": result["id"], "thread_id": thread_id}
