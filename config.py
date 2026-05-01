import os
from dotenv import load_dotenv
load_dotenv()

# ── Google Gemini via Vertex AI ──────────────────────────────────────────────
def _resolve_gcp_project():
    project = os.environ.get("GCP_PROJECT_ID", "")
    if project:
        return project
    sa_path = os.path.join(os.path.dirname(__file__), "service_account.json")
    if os.path.exists(sa_path):
        import json as _json
        with open(sa_path, encoding="utf-8") as f:
            return _json.load(f).get("project_id", "")
    return ""

GCP_PROJECT_ID = _resolve_gcp_project()
GCP_LOCATION   = os.environ.get("GCP_LOCATION", "us-central1")
MODEL          = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# ── Google Service Account (set via Railway env vars after encode_service_account.py) ─
SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON", "")

# ── App settings ─────────────────────────────────────────────────────────────
GMAIL_ADDRESS   = os.environ.get("GMAIL_ADDRESS", "mr.oppong@gmail.com")
SPREADSHEET_ID  = os.environ.get("SPREADSHEET_ID", "")   # paste Sheet ID from Google Drive
CALENDAR_ID     = os.environ.get("CALENDAR_ID", "primary")
_HERE = os.path.dirname(os.path.abspath(__file__))
CV_FILE_PATH         = os.environ.get("CV_FILE_PATH",         os.path.join(_HERE, "CV_Vincent_Oppong.pdf"))
CERT_NUMERIQUES_PATH = os.environ.get("CERT_NUMERIQUES_PATH", os.path.join(_HERE, "Certificats_numeriques.pdf"))
CERT_TRAVAIL_PATH    = os.environ.get("CERT_TRAVAIL_PATH",    os.path.join(_HERE, "Certificats_de_travail.pdf"))

MAX_COMPANIES_PER_DAY = int(os.environ.get("MAX_COMPANIES_PER_DAY", "5"))
FOLLOW_UP_DAYS        = int(os.environ.get("FOLLOW_UP_DAYS", "14"))
AUTO_SEND             = os.environ.get("AUTO_SEND", "false").lower() == "true"

# ── Vincent's professional profile ───────────────────────────────────────────
CANDIDATE = {
    "name":    "Vincent Oppong",
    "email":   "mr.oppong@gmail.com",
    "phone":   "+41 78 309 11 68",
    "address": "Route Aloys-Fauquez 73, 1018 Lausanne",
    "portfolio": "https://www.notion.so/Portfolio-2b8f70f532d481478c35f7cf6a0836a3",

    "target_location": "Lausanne and surroundings within 20 km (canton Vaud, Switzerland)",

    "target_roles": [
        "Community Manager",
        "Social Media Manager",
        "Content Manager / Head of Content",
        "Digital Marketing Manager",
        "SEO Specialist",
        "AI Content Specialist",
        "Responsable Marketing & Communication",
    ],

    "key_skills": [
        "Community Management & Brand Content (CADSCHOOL certified 2026)",
        "Content strategy & SEO (Semrush, Ahrefs, Surfer SEO)",
        "Paid media – Google Ads & Meta Ads (CPA/ROAS optimisation, A/B testing)",
        "Adobe Creative Suite (Photoshop, Illustrator, Premiere Pro, After Effects)",
        "WordPress website creation (Elementor, Divi) & conversion funnels",
        "AI tools – Claude, ChatGPT, Gemini, Jasper.ai",
        "CRM & marketing automation – HubSpot, Make.com, N8N, Sendinblue, Odoo",
        "Analytics – Google Analytics 4 & Google Tag Manager",
        "Multilingual production: French C1, English & Danish native, German A2",
    ],

    "key_achievements": [
        "+2 637 % de trafic organique en 24 mois chez 123 KID SA (Head of Content)",
        "ROAS de 4,6 sur les campagnes d'acquisition Google & Meta chez FuturPlus",
        "Triplement du trafic organique en moins de 5 mois chez 123 KID",
    ],

    "experience_summary": """
Ancien basketeur de haut niveau reconverti en marketeur digital polyvalent.
Parcours récent :
- Responsable Marketing & Communication — FuturPlus Sàrl, Lausanne (2024-2025)
- Head of Content — 123 KID SA, Lausanne (2021-2023)
- Chef de projet multimédia — COMM manager Sàrl, Belmont-sur-Lausanne (2021)
- Chef de projets multimédia — Agence Konsept, Lausanne (2020)
Formations : Certificat Community Mgmt & Brand Content (CADSCHOOL 2026),
Certificat Marketing Digital (CADSCHOOL 2023), A.P.Degree Multimedia Design &
Communication (Business Academy Aarhus, 2018).
""".strip(),
}
