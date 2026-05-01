"""cover_letter.py — generates a personalised French cover letter for each
company using Gemini, matching Vincent's strongest relevant experience to
the company's specific context."""

from datetime import datetime
from google import genai
import config
from google_auth import get_vertex_credentials

client = genai.Client(
    vertexai=True,
    project=config.GCP_PROJECT_ID,
    location=config.GCP_LOCATION,
    credentials=get_vertex_credentials(),
)


def generate_cover_letter(company: dict) -> str:
    """Return a fully formatted French cover letter for the given company."""

    today_fr = datetime.now().strftime("%d %B %Y").lstrip("0")  # e.g. "1 mai 2026"

    # Salutation
    if company.get("contact_name"):
        salutation = f"Madame, Monsieur {company['contact_name'].split()[-1]},"
    else:
        salutation = "Madame, Monsieur,"

    prompt = f"""Rédige une lettre de motivation professionnelle en français pour Vincent Oppong 
qui postule spontanément chez {company['name']}.

=== PROFIL DE VINCENT ===
Nom : Vincent Oppong
Adresse : Route Aloys-Fauquez 73, 1018 Lausanne
Téléphone : +41 78 309 11 68
Email : mr.oppong@gmail.com
Portfolio : {config.CANDIDATE['portfolio']}

Compétences clés :
{chr(10).join(f'- {s}' for s in config.CANDIDATE['key_skills'])}

Réalisations clés :
{chr(10).join(f'- {r}' for r in config.CANDIDATE['key_achievements'])}

Expérience :
{config.CANDIDATE['experience_summary']}

=== ENTREPRISE CIBLE ===
Nom : {company['name']}
Secteur : {company['industry']}
Site web : {company['website']}
Ville : {company['city']}
Présence sociale : {company['social_presence']}
Pourquoi bonne cible : {company['why_good_fit']}
Contact : {company.get('contact_name') or 'N/A'} — {company.get('contact_title') or 'N/A'}

=== INSTRUCTIONS DE RÉDACTION ===
- Langue : français professionnel et naturel (niveau C1)
- Ton : professionnel mais chaleureux, direct, pas de formules creuses
- Longueur : 3-4 paragraphes denses — ni trop court ni trop long
- Commence par les coordonnées expéditeur puis destinataire (format suisse standard)
- Date : {today_fr}
- Salutation : {salutation}
- Paragraph 1 : accroche percutante liée au contexte SPÉCIFIQUE de {company['name']} (pas générique)
- Paragraph 2 : 1-2 réalisations concrètes et chiffrées les plus pertinentes pour CE secteur
- Paragraph 3 : valeur ajoutée de sa spécialisation IA + tools modernes pour cette entreprise
- Paragraph 4 : call-to-action enthousiaste pour un entretien
- Signature : "Cordialement," puis "Vincent Oppong"
- NE PAS mentionner qu'il est disponible immédiatement (évite de sembler désespéré)
- NE PAS copier mot pour mot la lettre de motivation Conforama — même structure mais nouveau contenu

Retourne UNIQUEMENT le texte de la lettre, sans commentaires ni balises."""

    response = client.models.generate_content(model=config.MODEL, contents=prompt)
    return response.text.strip()
