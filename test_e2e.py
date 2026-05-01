"""test_e2e.py — one-shot e2e test: cover letter + Gmail + Sheets for a single company."""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from datetime import datetime, timedelta
import config
import cover_letter as cl
import gmail_client
import sheets_client

company = {
    "name": "Flybotix",
    "industry": "Robotics, Drone Technology, Industrial Inspection",
    "website": "https://www.flybotix.com",
    "contact_email": "dvoppong@gmail.com",
    "contact_name": "Christopher Thomson",
    "contact_title": "Head of Sales & Marketing",
    "why_good_fit": (
        "Flybotix is rapidly expanding its market presence with a recent $10M Series A extension "
        "and new product launches. Vincent's skills in content strategy, SEO, and AI tools could "
        "significantly improve their digital outreach and optimize online conversion funnels."
    ),
    "social_presence": "Active",
    "city": "Lausanne",
}

print(f"✍️   Génération de la lettre de motivation pour {company['name']}…")
letter = cl.generate_cover_letter(company)
print("\n--- LETTRE ---")
print(letter)
print("--------------\n")

print("📧  Envoi de l'email…")
result = gmail_client.create_draft_or_send(company, letter)
print(f"✅  {result['type'].capitalize()} créé (id: {result['id']})")
print(f"    Destinataire : {company['contact_email']}")

print("📊  Mise à jour du tableau de bord…")
sheets_client.ensure_sheet_headers()
follow_up = (datetime.now() + timedelta(days=config.FOLLOW_UP_DAYS)).strftime("%Y-%m-%d")
status = "Envoyé" if config.AUTO_SEND else "Brouillon créé"
sheets_client.add_application(company, result["thread_id"], follow_up, status)
print(f"✅  Ligne ajoutée — relance prévue le {follow_up}")
