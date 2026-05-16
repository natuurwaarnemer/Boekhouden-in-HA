# 🧾 Natuurwaarnemer ERP

**Volledig lokaal, gratis ERP-systeem voor ZZP'ers en kleine ondernemers.**  
Gebouwd op Home Assistant + n8n + SQLite. Geen cloud. Geen abonnement. Jouw data, op jouw hardware.

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-☕-yellow)](https://www.buymeacoffee.com/natuurwaarnemer)

> ☕ **[Buy me a coffee](https://www.buymeacoffee.com/natuurwaarnemer)** — vind je dit project handig? Een kleine bijdrage wordt enorm gewaardeerd!

---

## ⚠️ Disclaimer

> Dit systeem is gebouwd voor **eigen gebruik** en wordt aangeboden als open-source project.  
> De gebruiker is **zelf verantwoordelijk** voor:
> - De juistheid van de administratie
> - Naleving van fiscale wetgeving (BTW-aangifte, bewaarplicht 7 jaar)
> - Eventuele fouten in boekingen of facturen
>
> Dit pakket **vervangt geen accountant**. Gebruik op eigen risico. MIT-licentie van toepassing.

---

## 🎯 Wat doet dit systeem?

- 📄 **Facturen aanmaken** — invullen in HA, PDF genereren, e-mailen, boeken in grootboek
- 🛒 **Inkoop registreren** — leveranciersfacturen opslaan en boeken
- 👥 **Klanten beheren** — klantgegevens opslaan, herbruikbaar in factuurscherm
- 💸 **Kosten registreren** — bedrijfskosten vastleggen met grootboekrekening
- 📊 **Grootboek** — automatische dubbele boekhouding via RGS schema

---

## 🖥️ Twee dozen — zo werkt het

> **Belangrijk:** dit systeem draait op **twee aparte apparaten** (of VM's/containers).

```
┌─────────────────────────┐        ┌─────────────────────────┐
│      DOOS 1             │        │      DOOS 2             │
│   Home Assistant        │──────▶ │        n8n              │
│                         │  HTTP  │                         │
│  • Invoerschermen       │  POST  │  • Verwerkt de data     │
│  • Dashboard            │        │  • Slaat op in SQLite   │
│  • Knoppen & statussen  │◀────── │  • Genereert PDF        │
│                         │  JSON  │  • Verstuurt e-mail     │
└─────────────────────────┘        │  • Boekt in grootboek   │
                                   └─────────────────────────┘
                                             │
                                   ┌─────────┴─────────┐
                                   │     Optioneel      │
                                   │   Paperless-ngx    │
                                   │  (PDF archivering) │
                                   └───────────────────┘
```

| Doos | Wat draait hier | Poort |
|---|---|---|
| **Doos 1** | Home Assistant | 8123 |
| **Doos 2** | n8n | 5678 |
| **Doos 2** | SQLite (via n8n) | — |
| **Doos 2** | Gotenberg (Docker) | 3000 |
| **Doos 2** *(optioneel)* | Paperless-ngx (Docker) | 8000 |

---

## 📦 Componenten

### Verplicht

| Component | Doos | Doel |
|---|---|---|
| [Home Assistant](https://www.home-assistant.io/) 2024.1+ | Doos 1 | Invoerschermen, dashboards, automations |
| [n8n](https://n8n.io/) 1.x | Doos 2 | Workflow-automatisering, webhooks |
| [SQLite](https://www.sqlite.org/) 3.x | Doos 2 | Lokale database |
| [Gotenberg](https://gotenberg.dev/) 8.x | Doos 2 | PDF-generatie via Docker |
| Docker 20.x+ | Doos 2 | Voor Gotenberg |
| SMTP-server | — | E-mail versturen |

### Optioneel

| Component | Doos | Doel |
|---|---|---|
| [Paperless-ngx](https://docs.paperless-ngx.com/) | Doos 2 | Archiveren van factuur-PDF's, OCR, doorzoekbaar |

---

## 🚀 Installatie — 5 stappen

### Stap 1 — Doos 2: Database aanmaken

```bash
sqlite3 /data/erp.db < database/schema.sql
sqlite3 /data/erp.db < database/seed_grootboek.sql
```

### Stap 2 — Doos 2: n8n workflows importeren

1. Open n8n op `http://doos2-ip:5678`
2. Ga naar **Workflows → Importeren**
3. Importeer achtereenvolgens:
   - `n8n/workflow_factuur.json`
   - `n8n/workflow_kosten.json`
   - `n8n/workflow_inkoop.json`
   - `n8n/workflow_klanten.json`
4. Zet alle workflows op **Active** ✅

### Stap 3 — Doos 2: Gotenberg starten

```yaml
# docker-compose.yml
services:
  gotenberg:
    image: gotenberg/gotenberg:8
    ports:
      - "3000:3000"
```

### Stap 4 — Doos 1: HA package kopiëren

Kopieer `home-assistant/packages/erp_input_helpers.yaml` naar `/config/packages/`

Zorg dat `configuration.yaml` dit bevat:
```yaml
homeassistant:
  packages: !include_dir_named packages/
```

Voeg toe aan `/config/secrets.yaml`:
```yaml
n8n_webhook_factuur: "http://doos2-ip:5678/webhook/factuur-aanmaken"
n8n_webhook_kosten:  "http://doos2-ip:5678/webhook/kosten-opslaan"
n8n_webhook_inkoop:  "http://doos2-ip:5678/webhook/inkoop-opslaan"
n8n_webhook_klant:   "http://doos2-ip:5678/webhook/klant-opslaan"
```

Herstart Home Assistant.

### Stap 5 — Doos 1: Dashboard importeren

Ga naar **Instellingen → Dashboards → Toevoegen** en importeer `home-assistant/dashboard.yaml`.

---

### Optioneel: Paperless-ngx installeren (Doos 2)

```yaml
# toevoegen aan docker-compose.yml
  paperless-ngx:
    image: ghcr.io/paperless-ngx/paperless-ngx:latest
    ports:
      - "8000:8000"
    volumes:
      - ./paperless/data:/usr/src/paperless/data
      - ./paperless/media:/usr/src/paperless/media
```

Na installatie: n8n stuurt gegenereerde factuur-PDF's automatisch naar Paperless via de REST API.

---

## 📁 Mappenstructuur

```
Boekhouden-in-HA/
├── README.md
├── LICENSE
├── context.md                          ← Projectstatus voor Copilot Spaces
├── database/
│   ├── schema.sql                      ← SQLite tabelstructuur
│   └── seed_grootboek.sql              ← RGS grootboekrekeningen (0xxx–9xxx)
├── home-assistant/
│   └── packages/
│       └── erp_input_helpers.yaml      ← Alles-in-één HA package
├── n8n/
│   ├── workflow_factuur.json           ← Factuurflow (PDF + e-mail + grootboek)
│   ├── workflow_kosten.json            ← Kostenregistratie
│   ├── workflow_inkoop.json            ← Inkoopfacturen
│   └── workflow_klanten.json          ← Klantenbeheer
├── templates/
│   └── factuur_template.html          ← HTML/CSS factuurtemplate (huisstijl)
└── docs/
    ├── installatie.md                 ← Uitgebreide installatie-instructies
    └── roadmap.md                     ← Roadmap
```

---

## 📊 Grootboekschema (RGS)

| Reeks | Type |
|---|---|
| 0000–0999 | Vaste activa |
| 1000–1999 | Vlottende activa (kas, bank, debiteuren) |
| 2000–2999 | Voorraden |
| 3000–3999 | Eigen vermogen |
| 4000–4999 | Passiva / Kosten |
| 5000–5999 | Personeelskosten |
| 6000–6999 | Financiële kosten |
| 7000–7999 | Overige bedrijfskosten |
| 8000–8999 | Omzet |
| 9000–9999 | Resultaat |

BTW-codes: `H` = 21%, `L` = 9%, `V` = vrijgesteld, `G` = geen BTW

---

## 🤝 Contributing

Bijdragen zijn welkom! Open een issue of pull request.

1. Fork de repository
2. Maak een feature branch: `git checkout -b feature/mijn-feature`
3. Commit: `git commit -m 'feat: omschrijving'`
4. Push: `git push origin feature/mijn-feature`
5. Open een Pull Request

---

## 📄 Licentie

[MIT-licentie](LICENSE) — Copyright © 2026 Natuurwaarnemer ERP Contributors

---

> ☕ **[Buy me a coffee](https://www.buymeacoffee.com/natuurwaarnemer)** — vind je dit project handig? Bedankt!
