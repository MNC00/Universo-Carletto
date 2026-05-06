# Carletto — Sito Web

Sito statico multi-pagina servito da GitHub Pages dalla cartella `/docs`.

## Struttura

```
docs/
├── index.html        ← Home: chi è Carletto, iniziative
├── bot.html          ← Pagina dedicata al Buongiorno Bot
├── contribuisci.html ← Come contribuire al progetto
├── styles.css        ← Stylesheet condiviso
├── SuperCarlo.jpg    ← Immagine brand
└── README.md         ← Questo file
```

## Deploy

Il sito è pubblicato automaticamente tramite GitHub Pages:
- **Branch:** `main`
- **Cartella:** `/docs`
- **URL:** https://mnc00.github.io/Carletto-Buongiorno-Bot/

Ogni push su `main` aggiorna il sito in ~1 minuto.

### 5. Accedi alla pagina

L'URL sarà nel formato:

```
https://[tuo-username].github.io/[nome-repo]/
```

Lo trovi anche nella stessa schermata Settings → Pages dopo la pubblicazione.

---

## Note

- Ogni volta che fai push di modifiche a `docs/`, GitHub Pages si aggiorna automaticamente.
- Se vuoi un dominio personalizzato (es. `carlobot.it`), puoi configurarlo nella stessa schermata Pages sotto "Custom domain".
- La pagina funziona anche offline aprendo `docs/index.html` direttamente nel browser per testarla prima del deploy.
