# Universo Carletto

Monorepo per tutte le iniziative dedicate a Carletto.

## Struttura

```
apps/
  buongiorno-bot/   # Python bot: email giornaliera con citazioni, santi, bestemmie, foto
  website/          # Sito statico multi-pagina (GitHub Pages)
integrations/
  apps-script/      # Google Apps Script: form signup, unsubscribe webapp, welcome email
packages/
  branding/         # Asset condivisi (immagini, loghi)
```

## Apps

### 🤖 Buongiorno Bot (`apps/buongiorno-bot/`)

Bot Python che invia ogni mattina un'email personalizzata con contenuti di Carlo.
Eseguito automaticamente via GitHub Actions (`.github/workflows/morning_bot.yml`).

Vedi [`apps/buongiorno-bot/`](apps/buongiorno-bot/) per istruzioni locali.

### 🌐 Website (`apps/website/`)

Sito statico HTML/CSS servito da GitHub Pages tramite GitHub Actions (`.github/workflows/deploy_website.yml`).

**URL:** https://mnc00.github.io/Universo-Carletto/

## Integrations

### Google Apps Script (`integrations/apps-script/`)

Script Apps Script per:
- `01_grant_access/` — Form di iscrizione → accesso ai documenti condivisi
- `02_welcome_email/` — Email di benvenuto automatica
- `03_revoke_access/` — Revoca accesso in caso di disiscrizione
- `04_unsubscribe_webapp/` — Web App per disiscrizione sicura con link HMAC firmati

## Sviluppo Locale

```bash
# Dalla root del monorepo
cd apps/buongiorno-bot
python -m venv ../../.venv
pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m carlo_bot.main --dry-run
```

Il contesto architetturale completo è in [`CONTEXT.md`](CONTEXT.md).

L'obiettivo del progetto è allenare competenze pratiche di sviluppo software costruendo una piccola automazione end-to-end.

Competenze allenate:
- struttura di un piccolo progetto Python;
- gestione di file locali e configurazione;
- integrazione con un servizio esterno (Gmail SMTP);
- debugging;
- test minimi;
- refactor leggero;
- delivery incrementale.

---

## Cosa fa la V1

La V1:
- legge contatti, citazioni e altri testi da file locali;
- legge una foto casuale da una cartella locale;
- seleziona in modo casuale i contenuti;
- compone il testo della mail;
- allega una foto;
- invia la mail via Gmail SMTP;
- supporta invio per-destinatario con link di disiscrizione firmato opzionale;
- supporta dry run e invio reale da CLI;
- include test automatici minimi.

## Base V2 gia` implementata

Il progetto ora include una base tecnica per una V2 con storage remoto:
- backend di storage astratto con supporto `filesystem` e scaffold `google_workspace`;
- dataset separabili per `contacts` e per i contenuti collaborativi;
- supporto a foto inline lette anche da bytes, non solo da file locali;
- configurazione pronta per Google Drive e Google Sheets;
- web app Apps Script per la disiscrizione self-service firmata.

La V1 continua comunque a usare il backend locale come default.

### Fuori scope V1

Per ora non sono inclusi:
- scheduling automatico;
- Telegram, WhatsApp o altri canali;
- web app o GUI;
- database;
- cloud, Docker, CI/CD;
- storage online di foto e citazioni;
- personalizzazione avanzata per destinatario;
- dashboard o storico invii.

---

## Struttura del progetto

```text
.
├─ CONTEXT.md
├─ README.md
├─ .gitignore
├─ .env.example
├─ requirements.txt
├─ modifiche apps script/
│  ├─ 01_grant_access/
│  ├─ 02_welcome_email/
│  ├─ 03_revoke_access/
│  └─ 04_unsubscribe_webapp/
├─ scripts/
│  └─ rename_photos.py
├─ data/
│  ├─ contacts/
│  │  └─ contacts.json
│  ├─ quotes/
│  │  ├─ quotes.txt
│  │  ├─ saints.txt
│  │  └─ blasfemie.txt
│  └─ photos/
├─ src/
│  └─ carlo_bot/
│     ├─ __init__.py
│     ├─ main.py
│     ├─ bootstrap/
│     ├─ application/
│     ├─ domain/
│     ├─ infrastructure/
│     ├─ agents/
│     ├─ composer.py
│     ├─ config.py
│     ├─ email_sender.py
│     ├─ loaders.py
│     └─ picker.py
└─ test/
```

---

## Architettura

### Moduli principali

- `main.py`: entrypoint sottile compatibile con l'avvio storico.
- `bootstrap/`: parsing CLI e risoluzione runtime.
- `application/`: orchestrazione del workflow end-to-end.
- `domain/`: loader, picker e composer della business logic.
- `infrastructure/`: configurazione e adapter email SMTP.
- `agents/`: scaffold per task agentici atomici e registry.

I moduli canonici stanno nelle cartelle `bootstrap`, `application`, `domain` e `infrastructure`. Non ci sono piu` wrapper duplicati con lo stesso nome in posizioni diverse.

### Flusso applicativo

1. Caricamento configurazione da `.env`
2. Selezione del backend di storage
3. Lettura dati dal provider configurato
3. Selezione casuale dei contenuti
4. Generazione opzionale del link di disiscrizione firmato per ciascun destinatario
5. Composizione del messaggio
6. Costruzione della mail con allegato
7. Invio reale oppure dry run

---

## Prerequisiti

Per eseguire il progetto servono:

- Python 3.11+ consigliato
- un account Gmail personale
- una Gmail App Password
- un virtual environment Python attivo

---

## Setup locale

### 1. Clonare o copiare il progetto

Portati nella root del repository.

### 2. Creare il virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Installare le dipendenze

```bash
pip install -r requirements.txt
```

---

## Configurazione `.env`

Crea un file `.env` nella root del progetto.

Puoi partire da `.env.example`.

### Esempio completo

```env
APP_ENV=development

SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=tuoaccount@gmail.com
SMTP_PASSWORD=la_tua_app_password
SMTP_SENDER=tuoaccount@gmail.com

CONTACTS_FILE=data/contacts/contacts.json
QUOTES_FILE=data/quotes/quotes.txt
SAINTS_FILE=data/quotes/saints.txt
BLASFEMIE_FILE=data/quotes/blasfemie.txt
PHOTOS_DIR=data/photos

DRY_RUN=true

STORAGE_BACKEND=filesystem

GOOGLE_CREDENTIALS_FILE=service_account.json
GOOGLE_TOKEN_FILE=token.json
GOOGLE_CONTACTS_SPREADSHEET_ID=
GOOGLE_CONTENT_SPREADSHEET_ID=
GOOGLE_CONTACTS_SHEET_NAME=Contacts
GOOGLE_QUOTES_SHEET_NAME=Quotes
GOOGLE_SAINTS_SHEET_NAME=Saints
GOOGLE_BLASFEMIE_SHEET_NAME=Blasfemie
GOOGLE_PHOTOS_FOLDER_ID=

UNSUBSCRIBE_BASE_URL=
UNSUBSCRIBE_SECRET=
```

### Significato delle variabili

- `APP_ENV`: ambiente corrente, per ora solo informativo.
- `SMTP_HOST`: host SMTP del provider.
- `SMTP_PORT`: porta SMTP.
- `SMTP_USERNAME`: username SMTP, nel caso Gmail coincide con l'indirizzo email.
- `SMTP_PASSWORD`: app password Gmail.
- `SMTP_SENDER`: mittente mostrato nella mail.
- `CONTACTS_FILE`: path del file contatti.
- `QUOTES_FILE`: path del file citazioni principali.
- `SAINTS_FILE`: path del file dei santi.
- `BLASFEMIE_FILE`: path del file delle blasfemie.
- `PHOTOS_DIR`: cartella delle immagini.
- `DRY_RUN`: se `true`, costruisce la mail ma non la invia.
- `STORAGE_BACKEND`: backend storage attivo, `filesystem` o `google_workspace`.
- `GOOGLE_CREDENTIALS_FILE`: file JSON del Service Account usato per leggere Google Sheets e Drive.
- `GOOGLE_TOKEN_FILE`: file token OAuth legacy; con il Service Account non viene usato nel flusso standard.
- gli altri `GOOGLE_*`: configurazione necessaria per la V2 con Drive e Sheets.
- `UNSUBSCRIBE_BASE_URL`: URL del Web App Apps Script che riceve le richieste di disiscrizione.
- `UNSUBSCRIBE_SECRET`: secret condivisa usata per firmare i link di disiscrizione.

### Disiscrizione self-service

Se configuri sia `UNSUBSCRIBE_BASE_URL` sia `UNSUBSCRIBE_SECRET`, il bot genera un link di disiscrizione firmato diverso per ogni destinatario e lo inserisce nel body plain text e HTML.

L'endpoint da pubblicare si trova in [modifiche apps script/04_unsubscribe_webapp/README.md](modifiche%20apps%20script/04_unsubscribe_webapp/README.md) e il codice Apps Script e in [modifiche apps script/04_unsubscribe_webapp/unsubscribe_webapp.gs](modifiche%20apps%20script/04_unsubscribe_webapp/unsubscribe_webapp.gs).

### Nota importante su Gmail

Per usare Gmail con questo progetto:
1. attiva la verifica in due passaggi;
2. genera una App Password;
3. usa quella password in `SMTP_PASSWORD`.

Non usare la password normale dell'account Gmail nel file `.env`.

---

## Formato dei dati

## 1. Contatti

Percorso:

```text
data/contacts/contacts.json
```

Formato:
- lista JSON di oggetti;
- campi obbligatori: `name`, `email`, `active`;
- il bot invia solo ai contatti con `active: true`.

### Esempio

```json
[
  {
    "name": "Mario",
    "email": "mario@example.com",
    "active": true
  },
  {
    "name": "Giulia",
    "email": "giulia@example.com",
    "active": false
  }
]
```

---

## Esecuzione

Il progetto usa `src/` layout, quindi i comandi vanno eseguiti dalla root del repository impostando `PYTHONPATH=src`.

### Dry run

Esegue tutta la pipeline ma non invia la mail.

#### Windows PowerShell

```powershell
$env:PYTHONPATH="src"; python -m carlo_bot.main --dry-run
```

#### macOS / Linux

```bash
PYTHONPATH=src python -m carlo_bot.main --dry-run
```

### Invio reale

Invia realmente la mail.

### Uso del valore di default dal `.env`

Se non passi flag CLI, il comportamento segue il valore di `DRY_RUN` definito nel file `.env`.

#### Windows PowerShell

```powershell
$env:PYTHONPATH="src"; python -m carlo_bot.main
```

#### macOS / Linux

```bash
PYTHONPATH=src python -m carlo_bot.main
```
---

## CLI disponibile

Flag supportati:

- `--dry-run`: forza il dry run, anche se nel `.env` c'è `DRY_RUN=false`
- `--send`: forza l'invio reale, anche se nel `.env` c'è `DRY_RUN=true`

### Nota

I flag `--dry-run` e `--send` sono mutuamente esclusivi: non vanno usati insieme.

---

## Test

Per eseguire tutti i test:

### Windows PowerShell

```powershell
$env:PYTHONPATH="src"; python -m pytest
```

### macOS / Linux

```bash
PYTHONPATH=src python -m pytest
```

## Note operative

- Non committare mai `.env`.
- Prova prima tutto in dry run.
- Per i test reali usa inizialmente un solo destinatario attivo.
- Mantieni piccolo lo scope prima di passare alla V2.
- Il progetto usa input locali semplici per privilegiare comprensione e controllo.

---
```


