# Universo Carletto

Monorepo per tutte le iniziative dedicate a Carletto.

## Struttura

```
.
├── .env                          # configurazione locale (non committato)
├── .env.example                  # template configurazione
├── service_account.json          # credenziali Google Service Account (non committato)
├── CONTEXT.md                    # contesto architetturale esteso
├── apps/
│   ├── buongiorno-bot/           # bot Python: email giornaliera
│   │   ├── requirements.txt
│   │   ├── data/                 # contatti, citazioni, foto, prompt LLM
│   │   ├── scripts/              # utility (es. rename_photos.py)
│   │   ├── src/carlo_bot/        # codice sorgente
│   │   └── test/                 # test automatici
│   └── website/                  # sito statico HTML/CSS (GitHub Pages)
├── integrations/
│   └── apps-script/              # Google Apps Script
│       ├── 01_grant_access/
│       ├── 02_welcome_email/
│       ├── 03_revoke_access/
│       └── 04_unsubscribe_webapp/
└── packages/
    └── branding/                 # asset condivisi
```

---

## Buongiorno Bot

Bot Python che ogni mattina alle 9:30 (ora italiana) invia un'email personalizzata a tutti i contatti attivi.

### Cosa include ogni mail

- una citazione casuale
- il santo del giorno
- una bestemmia casuale
- una foto di Carlo
- un link di disiscrizione firmato (HMAC-SHA256)

Il testo del corpo è generato da Gemini (con fallback a un template statico se il modello non è disponibile).

### Architettura

```
bootstrap/      → parsing CLI, caricamento config, risoluzione project root
application/    → orchestrazione workflow end-to-end
domain/         → loader, picker, composer (business logic pura)
infrastructure/ → SMTP, Google Sheets/Drive, config, unsubscribe
agents/         → scaffold task agentici
```

**Flusso:**
1. Carica config da `.env`
2. Inizializza il provider di storage (`filesystem` o `google_workspace`)
3. Legge contatti, citazioni, foto
4. Seleziona casualmente i contenuti
5. Genera il testo via LLM (o template statico)
6. Genera il link di disiscrizione per ogni destinatario
7. Costruisce la mail e la invia (o dry run)

### Automazione GitHub Actions

Il workflow `.github/workflows/morning_bot.yml` esegue il bot ogni giorno alle 9:30 CET/CEST usando i secret configurati nel repository.

---

## Setup locale

### Prerequisiti

- Python 3.11+
- Account Gmail con App Password abilitata

### 1. Creare il virtual environment (dalla root del monorepo)

**Windows PowerShell**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Installare le dipendenze

```bash
pip install -r apps/buongiorno-bot/requirements.txt
```

### 3. Configurare `.env`

Crea `.env` nella root del monorepo partendo da `.env.example`:

```env
APP_ENV=development

SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=tuoaccount@gmail.com
SMTP_PASSWORD=la_tua_app_password
SMTP_SENDER=tuoaccount@gmail.com

DRY_RUN=true

STORAGE_BACKEND=google_workspace

GOOGLE_CREDENTIALS_FILE=service_account.json
GOOGLE_TOKEN_FILE=token.json
GOOGLE_CONTACTS_SPREADSHEET_ID=<id_foglio_contatti>
GOOGLE_CONTENT_SPREADSHEET_ID=<id_foglio_contenuti>
GOOGLE_CONTACTS_SHEET_NAME=users
GOOGLE_QUOTES_SHEET_NAME=citazioni
GOOGLE_SAINTS_SHEET_NAME=santi
GOOGLE_BLASFEMIE_SHEET_NAME=blasfemie
GOOGLE_PHOTOS_FOLDER_ID=<id_cartella_drive>

UNSUBSCRIBE_BASE_URL=<url_webapp_apps_script>
UNSUBSCRIBE_SECRET=<secret_condiviso_con_apps_script>

GEMINI_API_KEY=<chiave_api_gemini>
LLM_PROMPT_FILE=apps/buongiorno-bot/data/prompts/system_prompt.txt
```

#### Variabili chiave

| Variabile | Descrizione |
|---|---|
| `SMTP_PASSWORD` | App Password Gmail (non la password normale) |
| `DRY_RUN` | `true` = compone ma non invia |
| `STORAGE_BACKEND` | `filesystem` (locale) o `google_workspace` |
| `GOOGLE_CREDENTIALS_FILE` | JSON del Service Account Google |
| `UNSUBSCRIBE_BASE_URL` | URL della web app Apps Script di disiscrizione |
| `UNSUBSCRIBE_SECRET` | Secret HMAC condiviso con la web app |
| `GEMINI_API_KEY` | Chiave API Gemini; se vuoto usa template statico |

> **Gmail**: attiva la verifica in due passaggi e genera una App Password. Non usare la password dell'account.

---

## Esecuzione

I comandi vanno eseguiti dalla root del monorepo.

### Dry run

**Windows PowerShell**
```powershell
$env:PYTHONPATH="apps/buongiorno-bot/src"; python -m carlo_bot.main --dry-run
```

**macOS / Linux**
```bash
PYTHONPATH=apps/buongiorno-bot/src python -m carlo_bot.main --dry-run
```

### Invio reale

**Windows PowerShell**
```powershell
$env:PYTHONPATH="apps/buongiorno-bot/src"; python -m carlo_bot.main --send
```

**macOS / Linux**
```bash
PYTHONPATH=apps/buongiorno-bot/src python -m carlo_bot.main --send
```

### Flag CLI

| Flag | Descrizione |
|---|---|
| `--dry-run` | Forza dry run (ignora `DRY_RUN` nel `.env`) |
| `--send` | Forza invio reale (ignora `DRY_RUN` nel `.env`) |

I due flag sono mutuamente esclusivi.

---

## Test

**Windows PowerShell**
```powershell
$env:PYTHONPATH="apps/buongiorno-bot/src"; python -m pytest apps/buongiorno-bot/test
```

**macOS / Linux**
```bash
PYTHONPATH=apps/buongiorno-bot/src python -m pytest apps/buongiorno-bot/test
```

---

## Iscrizione e Disiscrizione

### Flusso di iscrizione

1. L'utente compila il Google Form
2. Il trigger `01_grant_access/grant_access.gs` si attiva automaticamente:
   - segna `active=true` nel foglio contatti
   - concede accesso editor al foglio contenuti e alla cartella foto
3. Il trigger `02_welcome_email/welcome_email.gs` invia una mail di benvenuto

### Flusso di disiscrizione

1. Ogni email inviata dal bot contiene un link di disiscrizione firmato (HMAC-SHA256)
2. Il link punta alla web app `04_unsubscribe_webapp/unsubscribe-webapp.gs`
3. La web app:
   - verifica la firma HMAC
   - segna `active=false` nel foglio contatti
   - salva il timestamp in `unsubscribed_at`
   - mostra una pagina di conferma
4. Alla prossima esecuzione il bot salta il contatto disattivato

### Sicurezza del link

- La firma usa HMAC-SHA256 con secret condiviso tra bot e web app
- Senza il secret è impossibile forgiare un link valido
- L'email nel link è normalizzata (lowercase, trim) su entrambi i lati

---

## Google Apps Script

Gli script in `integrations/apps-script/` coprono il ciclo di vita degli iscritti:

| Cartella | Funzione |
|---|---|
| `01_grant_access/` | Form iscrizione → accesso ai documenti |
| `02_welcome_email/` | Email di benvenuto automatica |
| `03_revoke_access/` | Revoca accesso alla disiscrizione |
| `04_unsubscribe_webapp/` | Web App disiscrizione con link HMAC firmati |

### Deploy della web app di disiscrizione

1. Apri un nuovo progetto Apps Script su https://script.google.com
2. Copia il contenuto di `04_unsubscribe_webapp/unsubscribe-webapp.gs`
3. Copia il contenuto di `04_unsubscribe_webapp/appsscript.json` nel manifest (abilita "Mostra file manifest" nelle impostazioni progetto)
4. Verifica che `CONTACTS_SPREADSHEET_ID` e `UNSUBSCRIBE_SECRET` siano corretti
5. Distribuisci come Web App:
   - **Esegui come**: Me
   - **Accesso**: Chiunque (anche anonimi)
6. Copia l'URL generato e incollalo in `UNSUBSCRIBE_BASE_URL` nel `.env` e nei GitHub Secrets

> Lo scope richiesto è solo `https://www.googleapis.com/auth/spreadsheets`. Non serve Drive.

---

## Website

Sito statico in `apps/website/` deployato automaticamente su GitHub Pages via `.github/workflows/deploy_website.yml` ad ogni push su `main`.

**URL:** https://mnc00.github.io/Universo-Carletto/

---

## GitHub Actions — Secret richiesti

Da configurare in *Settings → Secrets and variables → Actions*:

| Secret | Descrizione |
|---|---|
| `SMTP_HOST` | Host SMTP |
| `SMTP_PORT` | Porta SMTP |
| `SMTP_USERNAME` | Username SMTP |
| `SMTP_PASSWORD` | App Password Gmail |
| `SMTP_SENDER` | Indirizzo mittente |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON del Service Account codificato in **base64** |
| `GOOGLE_CONTACTS_SPREADSHEET_ID` | ID foglio contatti |
| `GOOGLE_CONTENT_SPREADSHEET_ID` | ID foglio contenuti |
| `GOOGLE_PHOTOS_FOLDER_ID` | ID cartella foto su Drive |
| `UNSUBSCRIBE_BASE_URL` | URL web app disiscrizione |
| `UNSUBSCRIBE_SECRET` | Secret HMAC |
| `GEMINI_API_KEY` | Chiave API Gemini |

> Per codificare il Service Account in base64:
> - Linux/macOS: `base64 -w 0 service_account.json`
> - PowerShell: `[Convert]::ToBase64String([IO.File]::ReadAllBytes("service_account.json"))`

---

## Note operative

- Non committare mai `.env` o `service_account.json`.
- Testa sempre in dry run prima di abilitare l'invio reale.
- Se Gemini restituisce un errore 503, il bot usa automaticamente il template statico.
- Il contesto architetturale completo è in [`CONTEXT.md`](CONTEXT.md).
