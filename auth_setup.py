"""auth_setup.py — Run this ONCE on your local machine to authorise
Vincent's Google account and retrieve the OAuth2 tokens needed by Railway.

Steps:
  1. pip install google-auth-oauthlib
  2. Download client_secrets.json from Google Cloud Console (see README)
  3. python auth_setup.py
  4. A browser window opens — sign in as mr.oppong@gmail.com
  5. Copy the printed env vars into Railway
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar",
]


def main():
    flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n" + "=" * 64)
    print("  ✅  Authentification réussie !")
    print("  Copie ces variables dans Railway → Variables d'environnement")
    print("=" * 64)
    print(f"\nGMAIL_CLIENT_ID={creds.client_id}")
    print(f"GMAIL_CLIENT_SECRET={creds.client_secret}")
    print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
    print(f"GMAIL_TOKEN={creds.token}")
    print("\n" + "=" * 64 + "\n")


if __name__ == "__main__":
    main()
