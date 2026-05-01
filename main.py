"""main.py — daily job-search orchestrator.
Run automatically by Railway cron every weekday morning.

Pipeline :
  1. Load already-contacted companies from Google Sheets
  2. Research N new target companies (Claude + web search)
  3. For each company:
       a. Generate a personalised French cover letter (Claude)
       b. Create a Gmail draft (or send if AUTO_SEND=true)
       c. Add a follow-up reminder to Google Calendar
       d. Append a row to the Google Sheets dashboard
  4. Print a summary log
"""

import sys
from datetime import datetime, timedelta
import config
import sheets_client
import research
import cover_letter as cl
import gmail_client
import calendar_client


# ── Validation ───────────────────────────────────────────────────────────────

def validate_env():
    required = [
        ("GCP_PROJECT_ID", config.GCP_PROJECT_ID),
        ("SPREADSHEET_ID", config.SPREADSHEET_ID),
    ]
    missing = [name for name, val in required if not val]
    if missing:
        print("❌  Missing environment variables:")
        for m in missing:
            print(f"   - {m}")
        sys.exit(1)


# ── Main ─────────────────────────────────────────────────────────────────────

def run():
    print(f"\n{'='*62}")
    print(f"  🚀  Job Search Routine — {datetime.now().strftime('%A %d %B %Y, %H:%M')}")
    print(f"{'='*62}\n")

    validate_env()

    # Step 1 — Ensure headers exist & load history
    print("📋  Chargement des candidatures précédentes…")
    sheets_client.ensure_sheet_headers()
    already_contacted = sheets_client.get_contacted_companies()
    print(f"     {len(already_contacted)} entreprises déjà contactées.\n")

    # Step 2 — Research new companies
    print("🔍  Recherche de nouvelles entreprises cibles…")
    companies = research.research_companies(already_contacted)
    companies = companies[: config.MAX_COMPANIES_PER_DAY]
    print(f"     {len(companies)} nouvelles cibles trouvées.\n")

    if not companies:
        print("⚠️   Aucune nouvelle entreprise trouvée aujourd'hui. Fin du script.")
        return

    results   = []
    follow_up = (datetime.now() + timedelta(days=config.FOLLOW_UP_DAYS)).strftime(
        "%Y-%m-%d"
    )

    for i, company in enumerate(companies, 1):
        print(f"[{i}/{len(companies)}]  {company['name']} — {company.get('city','?')}")

        try:
            # 3a — Cover letter
            print("       ✍️   Rédaction de la lettre de motivation…")
            letter = cl.generate_cover_letter(company)

            # 3b — Gmail
            action_label = "Envoi email" if config.AUTO_SEND else "Création du brouillon Gmail"
            print(f"       📧  {action_label}…")
            gmail_result = gmail_client.create_draft_or_send(company, letter)
            print(f"       ✅  {gmail_result['type'].capitalize()} créé (id: {gmail_result['id'][:12]}…)")

            # 3c — Sheets (source of truth — must succeed for tracking)
            print("       📊  Mise à jour du tableau de bord…")
            status = "Envoyé" if config.AUTO_SEND else "Brouillon créé"
            sheets_client.add_application(company, gmail_result["thread_id"], follow_up, status)

            # 3d — Calendar (best-effort — failure does not block the row)
            print("       📅  Création du rappel de relance…")
            try:
                calendar_client.create_followup_event(company)
            except Exception as cal_exc:
                print(f"       ⚠️   Calendar non bloquant : {cal_exc}")

            print("       ✅  Terminé !\n")
            results.append({"company": company["name"], "ok": True})

        except Exception as exc:
            print(f"       ❌  Erreur : {exc}\n")
            results.append({"company": company["name"], "ok": False, "error": str(exc)})

    # Summary
    ok  = [r for r in results if r["ok"]]
    err = [r for r in results if not r["ok"]]

    print(f"\n{'='*62}")
    print(f"  📊  RÉSUMÉ")
    print(f"{'='*62}")
    print(f"  ✅  Succès    : {len(ok)}")
    for r in ok:
        print(f"       • {r['company']}")
    if err:
        print(f"  ❌  Échecs   : {len(err)}")
        for r in err:
            print(f"       • {r['company']} — {r.get('error','')}")
    total = len(already_contacted) + len(ok)
    print(f"\n  🎯  Total candidatures envoyées à ce jour : {total}")
    print(f"  📅  Relances planifiées pour : {follow_up}")
    print(f"{'='*62}\n")


if __name__ == "__main__":
    run()
