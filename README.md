# 🚀 Job Search Routine — Vincent Oppong

Recherche d'emploi automatisée : tous les jours ouvrables, le script trouve 5 nouvelles 
entreprises dans la région lausannoise, rédige une lettre de motivation personnalisée, 
crée un brouillon Gmail avec le CV en pièce jointe, programme une relance dans Google 
Calendar et met à jour le tableau de bord Google Sheets.

---

## Architecture

```
Railway Cron (lun–ven, 7h00)
        │
        ▼
main.py (orchestrateur)
   ├── research.py      → Claude + web_search → 5 entreprises cibles
   ├── cover_letter.py  → Claude → lettre personnalisée en français
   ├── gmail_client.py  → Gmail API → brouillon (ou envoi direct)
   ├── calendar_client.py → Google Calendar API → rappel de relance J+14
   └── sheets_client.py   → Google Sheets API → mise à jour dashboard
```

---

## Setup en 5 étapes

### Étape 1 — Clé API Gemini

1. Va sur https://aistudio.google.com/app/apikey
2. Clique sur **"Create API key"**
3. Note-la : `GEMINI_API_KEY=AIza...`

---

### Étape 2 — Google Cloud Console (10 min)

1. Va sur https://console.cloud.google.com/
2. Crée un nouveau projet : `vincent-job-search`
3. Active ces 3 APIs (recherche dans "APIs & Services > Library") :
   - **Gmail API**
   - **Google Sheets API**
   - **Google Calendar API**

---

### Étape 3 — Créer un Service Account (5 min)

Un Service Account est plus simple qu'OAuth pour les scripts automatisés.

1. Va dans **"APIs & Services" → "Credentials"** (barre latérale)
2. Clique **"+ Create Credentials"** → **"Service Account"**
3. Remplis :
   - **Service account name** : `job-search-automation`
   - (L'ID se remplit automatiquement)
   - Clique **"Create and Continue"**
4. Saute les étapes optionnelles, clique **"Create Key"**
5. Choisis **"JSON"** → **"Create"**
   - Un fichier `service_account.json` se télécharge
   - **Sauvegarde-le dans le dossier `job-search-routine`**
6. **Copie l'adresse email du service account** (ressemble à `job-search-automation@vincent-job-search.iam.gserviceaccount.com`)

---

### Étape 4 — Partager ton Google Sheet et Calendar (5 min)

**Google Sheet :**
1. Ouvre ton **Job Search Dashboard**
2. Clique **"Share"** (haut à droite)
3. Colle l'adresse email du service account
4. Donne l'accès **"Editor"**
5. Clique **"Share"**

**Google Calendar :**
1. Va à https://calendar.google.com
2. Clique sur ton calendrier → **"Settings"**
3. **"Share with specific people"** → ajoute le service account
4. Accès : **"Make changes to events"**

---

### Étape 5 — Encoder le service account (2 min)

```bash
python encode_service_account.py service_account.json
```

Copie la chaîne `SERVICE_ACCOUNT_JSON=...` affichée.

---

### Étape 6 — Encoder ton CV (2 min)

```bash
python encode_cv.py CV_Vincent_Oppong.pdf
```

Copie la chaîne `CV_BASE64=...` affichée.

---

### Étape 5 — Déploiement sur Railway

1. Va sur https://railway.app et crée un compte gratuit
2. Crée un nouveau projet → **"Deploy from GitHub repo"**
   (pousse ce dossier sur GitHub d'abord : `git init && git add . && git commit -m "init" && git remote add origin <ton-repo> && git push`)
3. Dans Railway → ton projet → **"Add Service" → "Cron Job"**
4. Configure :
   - **Command** : `python main.py`
   - **Schedule** : `0 7 * * 1-5` (tous les jours ouvrables à 7h00)
5. Dans **Variables**, ajoute toutes les variables du fichier `.env.example` :

| Variable | Valeur |
|---|---|
| `GEMINI_API_KEY` | From Step 1 |
| `SERVICE_ACCOUNT_JSON` | From Step 5 |
| `GMAIL_ADDRESS` | `mr.oppong@gmail.com` |
| `SPREADSHEET_ID` | From the Google Sheet URL |
| `CALENDAR_ID` | `primary` |
| `CV_BASE64` | From Step 6 |
| `MAX_COMPANIES_PER_DAY` | `5` |
| `FOLLOW_UP_DAYS` | `14` |
| `AUTO_SEND` | `false` |

6. **Deploy** ✅

---

## Tester localement avant de déployer

```bash
# Créer un fichier .env avec tes vraies variables
cp .env.example .env
# (remplis .env avec tes vraies valeurs)

pip install python-dotenv
python -c "from dotenv import load_dotenv; load_dotenv(); import main; main.run()"
```

---

## Activer l'envoi automatique

Une fois que tu es satisfait de la qualité des brouillons (après 2-3 jours de test) :

Dans Railway → Variables → change `AUTO_SEND` de `false` à `true`.

⚠️ **Attention** : les emails seront envoyés automatiquement sans validation manuelle.

---

## Tableau de bord Google Sheets

Ouvre ton sheet "Job Search Dashboard" pour voir toutes tes candidatures :
https://docs.google.com/spreadsheets/d/1xp7SLZiqzHKamIh0P4WCYu3K0tsP0dFbxQjjyQOStig

Colonnes :
- **Date envoi** — date de la candidature
- **Entreprise** — nom
- **Poste visé** — rôle ciblé
- **Ville** — localisation
- **Site web** — URL
- **Contact** — nom du contact si trouvé
- **Email contact** — adresse d'envoi
- **Statut** — "Brouillon créé" ou "Envoyé", puis tu peux mettre à jour manuellement
- **Date relance** — J+14
- **Pourquoi bonne cible** — contexte généré par Claude
- **Gmail Draft/Message ID** — référence interne

---

## Coûts estimés

| Service | Coût |
|---|---|
| Railway Hobby plan | ~$5/mois |
| Anthropic API (5 entreprises/jour) | ~$2–4/mois |
| Google APIs | Gratuit (dans les limites) |
| **Total** | **~$7–10/mois** |

---

## Support

En cas de problème, vérifie les logs dans Railway → ton service → "Deployments" → logs.
