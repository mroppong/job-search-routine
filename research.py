"""research.py — uses Gemini with Google Search grounding to find fresh target
companies in the Lausanne / Vaud area that have not yet been contacted."""

import json
import google.generativeai as genai
import config

genai.configure(api_key=config.GEMINI_API_KEY)


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
de 20 km autour de Lausanne (canton de Vaud, Suisse) qui :
1. N'ont pas encore une présence digitale optimale OU qui cherchent à renforcer leur marketing
2. Opèrent dans des secteurs variés (e-commerce, retail, services, tech, agences, institutions, etc.)
3. Sont assez grandes pour avoir besoin d'un community manager ou spécialiste contenu (10+ employés)
4. Ont un site web et idéalement des réseaux sociaux

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

    model = genai.GenerativeModel(
        model_name=config.MODEL,
        tools="google_search_retrieval",   # Gemini's grounded web search
    )

    response = model.generate_content(prompt)
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
        return data.get("companies", [])
    except json.JSONDecodeError as e:
        print(f"⚠️  research.py: JSON parse error — {e}")
        return []
