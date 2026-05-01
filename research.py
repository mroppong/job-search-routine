"""research.py — uses Gemini with Google Search grounding to find fresh target
companies in the Lausanne / Vaud area that have not yet been contacted."""

import json
from google import genai
from google.genai import types
import config
from google_auth import get_vertex_credentials

client = genai.Client(
    vertexai=True,
    project=config.GCP_PROJECT_ID,
    location=config.GCP_LOCATION,
    credentials=get_vertex_credentials(),
)

GENERIC_PREFIXES = {
    "info", "contact", "hello", "bonjour", "admin",
    "rh", "recrutement", "marketing", "direction",
    "accueil", "secretariat", "office", "general",
}


def is_generic_email(email: str) -> bool:
    if not email:
        return True
    prefix = email.split("@")[0].lower()
    return prefix in GENERIC_PREFIXES


def find_contact(company: dict) -> dict:
    """Search specifically for a named decision-maker at the given company.

    Returns a dict with contact_name, contact_title, contact_email (any may be None).
    """
    name = company.get("name", "")
    website = company.get("website", "")
    domain = website.replace("https://", "").replace("http://", "").split("/")[0]

    prompt = f"""Tu es un assistant spécialisé dans la recherche de contacts professionnels.

Recherche le nom et les coordonnées d'un décideur chez "{name}" (site : {website}).

STRATÉGIE DE RECHERCHE — effectue ces recherches dans l'ordre :
1. "{name} responsable marketing LinkedIn"
2. "{name} directeur communication responsable digital"
3. "{name} équipe dirigeante RH recrutement"
4. Page équipe ou à-propos du site : {website}/equipe , {website}/team , {website}/a-propos
5. Si un nom est trouvé mais pas d'email direct, construis l'email probable depuis le domaine {domain} \
(ex : prenom.nom@{domain}, p.nom@{domain})

PRIORITÉ DES TITRES (du plus au moins préféré) :
- Responsable Marketing / Communication / Digital / Contenu
- Directeur Marketing / Communication
- Responsable RH / Recrutement
- Directeur Général (uniquement si c'est une très petite structure)

Retourne UNIQUEMENT du JSON valide (pas de texte avant ou après) :
{{
  "contact_name": "Prénom Nom ou null",
  "contact_title": "Titre exact ou null",
  "contact_email": "email@{domain} ou null"
}}

Si tu ne trouves aucun contact spécifique, retourne null pour tous les champs. \
Ne retourne JAMAIS un email générique (info@, contact@, rh@, etc.) dans ce résultat."""

    try:
        response = client.models.generate_content(
            model=config.MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )
        text = response.text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            return {}
        return json.loads(text[start:end])
    except Exception as e:
        print(f"⚠️  find_contact({name}): {e}")
        return {}


def research_companies(already_contacted: list[str]) -> list[dict]:
    """Return a list of company dicts for today's outreach batch."""

    skip_list = (
        ", ".join(already_contacted) if already_contacted else "aucune pour l'instant"
    )

    prompt = f"""Tu es un assistant de recherche d'emploi qui aide {config.CANDIDATE['name']}
à trouver des entreprises dans {config.CANDIDATE['target_location']} qui pourraient bénéficier
de ses compétences en community management, content creation, SEO et IA.

COMPÉTENCES CLÉS DE VINCENT :
{chr(10).join(f'- {s}' for s in config.CANDIDATE['key_skills'])}

POSTES VISÉS : {', '.join(config.CANDIDATE['target_roles'])}

ENTREPRISES DÉJÀ CONTACTÉES (à exclure absolument) :
{skip_list}

MISSION :
Recherche sur le web {config.MAX_COMPANIES_PER_DAY} entreprises NOUVELLES basées dans un rayon
de 30 km autour de Lausanne (canton de Vaud, Suisse) qui correspondent à ce profil EXACT :

PROFIL CIBLE (toutes ces conditions doivent être réunies) :
- PME en croissance active : entre 20 et 200 employés, en phase de développement ou d'expansion
- Signes de croissance récents : nouveaux produits/services lancés, nouvelles ouvertures,
  recrutements en cours, levée de fonds récente, ou expansion géographique
- Présence digitale perfectible : site web existant mais réseaux sociaux peu actifs
  ou stratégie de contenu absente/faible
- Secteurs variés acceptés : e-commerce, retail, tech/SaaS, services B2B, hôtellerie,
  bien-être, agences, industrie légère, immobilier, etc.

À EXCLURE ABSOLUMENT :
- Grandes entreprises (500+ employés) : déjà équipées d'équipes marketing complètes
- Micro-entreprises et indépendants (moins de 15 employés) : budget marketing insuffisant
- Institutions publiques, administrations, communes, cantons, agences gouvernementales
- Associations, fondations, ONG, organisations à but non lucratif
- Événements ponctuels ou saisonniers (courses, festivals, conférences annuelles)
- Entreprises déjà contactées dans la liste ci-dessus

Pour chaque entreprise, recherche :
- Le site web officiel
- L'email de contact RH ou marketing (sinon email général)
- Le nom et titre d'un contact si possible (directeur, responsable RH, etc.)
- L'état de leur présence sur les réseaux sociaux

Retourne UNIQUEMENT du JSON valide dans ce format exact (pas de texte avant ou après) :
{{
  "companies": [
    {{
      "name": "Nom de l'entreprise",
      "industry": "Secteur d'activité",
      "website": "https://...",
      "contact_email": "email@entreprise.ch",
      "contact_name": "Prénom Nom ou null",
      "contact_title": "Titre du contact ou null",
      "why_good_fit": "Raison spécifique en 1-2 phrases pourquoi Vincent serait utile",
      "social_presence": "Active / Faible / Inexistante",
      "city": "Ville"
    }}
  ]
}}"""

    response = client.models.generate_content(
        model=config.MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    full_text = response.text

    # Parse JSON — be tolerant of leading/trailing prose
    start = full_text.find("{")
    end   = full_text.rfind("}") + 1
    if start == -1 or end == 0:
        print("⚠️  research.py: no JSON found in Gemini response.")
        print(full_text[:500])
        return []

    try:
        data = json.loads(full_text[start:end])
        companies = data.get("companies", [])
    except json.JSONDecodeError as e:
        print(f"⚠️  research.py: JSON parse error — {e}")
        return []

    # Stage 2: targeted contact lookup per company
    for company in companies:
        name = company.get("name", "?")
        print(f"  🔍 Searching contact for {name}…")
        contact = find_contact(company)
        if contact.get("contact_name"):
            company["contact_name"] = contact["contact_name"]
            company["contact_title"] = contact.get("contact_title")
        if contact.get("contact_email") and not is_generic_email(contact["contact_email"]):
            company["contact_email"] = contact["contact_email"]

    return companies


if __name__ == "__main__":
    companies = research_companies([])
    print(json.dumps(companies, ensure_ascii=False, indent=2))
