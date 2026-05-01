"""follow_up.py — generates a short French follow-up email for applications
that received no response after FOLLOW_UP_DAYS."""

from google import genai
import config
from google_auth import get_vertex_credentials

client = genai.Client(
    vertexai=True,
    project=config.GCP_PROJECT_ID,
    location=config.GCP_LOCATION,
    credentials=get_vertex_credentials(),
)


def generate_followup_email(app: dict) -> str:
    """Return a polite 2-paragraph follow-up email in French (plain text)."""
    send_date    = app.get("date_envoi", "récemment")
    company_name = app.get("company", "votre entreprise")

    prompt = f"""Rédige un court email de relance en français pour Vincent Oppong.
Il avait envoyé une candidature spontanée à {company_name} le {send_date} et n'a pas reçu de réponse.

=== INSTRUCTIONS ===
- Langue : français professionnel et naturel
- Ton : poli, chaleureux, jamais insistant ni désespéré
- Longueur : 2 paragraphes maximum — bref et respectueux du temps du lecteur
- Commence par : Bonjour,
- Paragraphe 1 : rappel discret de la candidature envoyée le {send_date}, sans reformuler toute la lettre
- Paragraphe 2 : renouvellement de l'intérêt pour {company_name}, invitation à échanger si un poste ou un besoin correspond
- Termine par : Cordialement,\n\nVincent Oppong
- NE PAS mentionner qu'il est disponible immédiatement
- NE PAS être insistant ou répétitif

Retourne UNIQUEMENT le texte de l'email, sans commentaires ni balises."""

    response = client.models.generate_content(model=config.MODEL, contents=prompt)
    return response.text.strip()
