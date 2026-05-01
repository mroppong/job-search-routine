"""check_responses.py — daily script that:
  1. Detects replies to sent applications
  2. Sends automatic follow-up emails when the follow-up date has passed
  3. Closes applications with no response after a second follow-up window
"""

import sys
from datetime import date, datetime, timedelta
import config
import sheets_client
import gmail_client
import follow_up as fu


def run():
    print(f"\n{'='*62}")
    print(f"  🔍  Vérification des réponses — {date.today()}")
    print(f"{'='*62}\n")

    pending = sheets_client.get_pending_applications()
    if not pending:
        print("  ✅  Aucune candidature en attente.\n")
        return

    today   = date.today()
    replied = []
    relance = []
    closed  = []
    waiting = []

    for app in pending:
        company    = app["company"]
        thread_id  = app["message_id"]
        status     = app["status"]

        raw_date   = app.get("follow_up_date", "")
        try:
            follow_up_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError:
            print(f"  ⚠️  Date invalide pour {company} ({raw_date!r}), ignoré.")
            continue

        print(f"  [{status}]  {company}")

        # Step 1 — check for a reply
        try:
            if gmail_client.has_reply(thread_id):
                sheets_client.update_status(company, "Réponse reçue")
                print(f"         ✅  Réponse détectée — statut mis à jour.\n")
                replied.append(company)
                continue
        except Exception as exc:
            print(f"         ⚠️  Impossible de vérifier le thread : {exc}\n")
            waiting.append(company)
            continue

        # Step 2 — check whether follow-up date has passed
        if follow_up_date > today:
            days_left = (follow_up_date - today).days
            print(f"         ⏳  Relance dans {days_left} jour(s).\n")
            waiting.append(company)
            continue

        # Follow-up date has passed and no reply received
        if status == "Relancé":
            sheets_client.update_status(company, "Sans suite")
            print(f"         🔒  2ème fenêtre expirée — classé Sans suite.\n")
            closed.append(company)
        else:
            # status == "Envoyé" — send first follow-up
            print(f"         ✍️   Génération de l'email de relance…")
            try:
                letter = fu.generate_followup_email(app)
                result = gmail_client.send_followup(
                    company=app,
                    body=letter,
                    thread_id=thread_id,
                    original_message_id=thread_id,
                )
                new_date = (today + timedelta(days=config.FOLLOW_UP_DAYS)).strftime("%Y-%m-%d")
                sheets_client.update_status(company, "Relancé")
                sheets_client.update_followup_date(company, new_date)
                print(f"         📧  Relance envoyée (id: {result['id'][:12]}…)")
                print(f"         📅  Prochaine vérification : {new_date}\n")
                relance.append(company)
            except Exception as exc:
                print(f"         ❌  Erreur lors de la relance : {exc}\n")
                waiting.append(company)

    # Summary
    print(f"{'='*62}")
    print(f"  📊  RÉSUMÉ")
    print(f"{'='*62}")
    if replied:
        print(f"  ✅  Réponses reçues ({len(replied)}) : {', '.join(replied)}")
    if relance:
        print(f"  📧  Relances envoyées ({len(relance)}) : {', '.join(relance)}")
    if closed:
        print(f"  🔒  Classés Sans suite ({len(closed)}) : {', '.join(closed)}")
    if waiting:
        print(f"  ⏳  En attente ({len(waiting)}) : {', '.join(waiting)}")
    print(f"{'='*62}\n")


if __name__ == "__main__":
    run()
