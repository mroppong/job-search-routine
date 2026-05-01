"""cover_letter.py — generates a personalised French cover letter for each
company using Gemini, matching Vincent's strongest relevant experience to
the company's specific context."""

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
    """Return the body of a French cover letter (no sender header, no date)."""

    salutation = "Bonjour,"

    prompt = f"""Rédige le corps d'un email de candidature spontanée en français pour Vincent Oppong
qui postule chez {company['name']}.

=== PROFIL DE VINCENT ===
Nom : Vincent Oppong
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
- C'est un email, donc PAS de bloc d'adresse expéditeur, PAS de date, PAS de bloc destinataire
- Commence directement par la salutation : {salutation}
- Paragraph 1 : accroche percutante liée au contexte SPÉCIFIQUE de {company['name']} (pas générique)
- Paragraph 2 : 1-2 réalisations concrètes et chiffrées les plus pertinentes pour CE secteur
- Paragraph 3 : valeur ajoutée de sa spécialisation IA + tools modernes pour cette entreprise
- Paragraph 4 : call-to-action enthousiaste pour un entretien
- Termine par : "Cordialement," puis "Vincent Oppong" (rien d'autre — les coordonnées seront ajoutées automatiquement)
- NE PAS mentionner qu'il est disponible immédiatement (évite de sembler désespéré)
- NE PAS copier mot pour mot la lettre de motivation Conforama — même structure mais nouveau contenu

Retourne UNIQUEMENT le texte, sans commentaires ni balises HTML."""

    response = client.models.generate_content(model=config.MODEL, contents=prompt)
    return response.text.strip()
