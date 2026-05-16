# Context — Natuurwaarnemer ERP

> **Aangemaakt:** 2026-05-15  
> **Laatst bijgewerkt:** 2026-05-16  
> **Doel:** Overzicht van de huidige status van het project voor gebruik als context in Copilot Spaces en voor nieuwe bijdragers.

---

## Wat is dit project?

**Natuurwaarnemer ERP** is een volledig lokaal, gratis ERP-systeem voor kleine ondernemers en ZZP'ers, gebouwd op:

- **Home Assistant** — invoerschermen, dashboards, automations
- **n8n** — workflow-automatisering en API-koppelingen
- **MySQL** — database (draait lokaal, niet in de cloud)
- **Gotenberg** — PDF-generatie via Docker
- **SMTP** — e-mail versturen via n8n

Geen abonnementen, geen cloud, alle data blijft op eigen hardware. Volledig BTW-conform met RGS grootboekschema.

> **Let op:** De workflows zijn overgezet van SQLite naar **MySQL**. De `workflow_factuur.json` gebruikt nog SQLite via `executeCommand` — dit is een bekend openstaand punt.

---

## Repository structuur

```
Boekhouden-in-HA/
├── README.md                        ← Hoofddocumentatie
├── LICENSE                          ← MIT-licentie
├── context.md                       ← Dit bestand
├── database/
│   ├── schema.sql                   ✅ Aanwezig — SQLite tabelstructuur
│   └── seed_grootboek.sql           ✅ Aanwezig — RGS grootboekrekeningen (0xxx–9xxx)
├── home-assistant/
│   └── packages/
│       └── erp_input_helpers.yaml   ✅ Aanwezig — Input helpers, automations, rest_commands, template sensors
├── n8n/
│   ├── workflow_factuur.json        ✅ Aanwezig — Factuurflow (PDF + e-mail + grootboek, SQLite)
│   ├── workflow_kosten.json         ✅ Aanwezig — Kostenregistratie (MySQL, HA terugkoppeling)
│   ├── workflow_inkoop.json         ✅ Aanwezig — Inkoopfacturen (MySQL, HA terugkoppeling)
│   └── workflow_klanten.json        ✅ Aanwezig — Klanten opslaan (MySQL, HA terugkoppeling)
├── templates/
│   └── factuur_template.html        ⚠️ Aanwezig — nog aanpassen aan Natuurwaarnemer huisstijl
└── docs/
    ├── installatie.md               ✅ Aanwezig — Installatie-instructies
    └── roadmap.md                   ✅ Aanwezig — Roadmap
```

---

## Sessieverslag 2026-05-16

### Wat is gedaan in deze sessie

1. **workflow_kosten.json gefixed**
   - Omgezet van SQLite (`n8n-nodes-base.sqlite`) naar MySQL (`n8n-nodes-base.mySql`)
   - `responseMode` van webhook gezet op `responseNode`
   - HA terugkoppeling via HTTP Request toegevoegd naar `http://192.168.2.17:8123/api/webhook/natuurwaarnemer_erp_bevestiging`
   - Respond to Webhook node toegevoegd als eindnode

2. **workflow_inkoop.json gefixed**
   - Zelfde aanpassingen als kosten: MySQL, `responseNode`, HA terugkoppeling
   - Grootboek opzoeking via `ledger_accounts` tabel op code

3. **Workflows geïmporteerd in n8n**
   - `workflow_kosten.json` geïmporteerd via raw GitHub URL
   - `workflow_inkoop.json` geïmporteerd via raw GitHub URL
   - Import URLs:
     - `https://raw.githubusercontent.com/natuurwaarnemer/Boekhouden-in-HA/main/n8n/workflow_kosten.json`
     - `https://raw.githubusercontent.com/natuurwaarnemer/Boekhouden-in-HA/main/n8n/workflow_inkoop.json`

4. **context.md bijgewerkt** (dit bestand)

---

## Huidige status per fase

### ✅ Fase 1 — Basis ERP (grotendeels gereed)

| Onderdeel | Status | Bestand |
|---|---|---|
| SQLite database schema | ✅ Gereed | `database/schema.sql` |
| RGS grootboekschema (0xxx–9xxx) | ✅ Gereed | `database/seed_grootboek.sql` |
| HA package — input helpers | ✅ Gereed | `home-assistant/packages/erp_input_helpers.yaml` |
| HA package — rest_commands → n8n | ✅ Gereed | (onderdeel van package) |
| HA package — automations | ✅ Gereed | (onderdeel van package) |
| HA package — template sensors | ✅ Gereed | (onderdeel van package) |
| `initial: ""` op alle input_text | ✅ Gefixed 2026-05-15 | Voorkomt `unknown` na herstart |
| n8n factuurflow | ✅ Aanwezig (SQLite) | `n8n/workflow_factuur.json` |
| n8n kostenregistratie | ✅ Gereed (MySQL) | `n8n/workflow_kosten.json` |
| n8n inkoop workflow | ✅ Gereed (MySQL) | `n8n/workflow_inkoop.json` |
| n8n klanten workflow | ✅ Gereed (MySQL) | `n8n/workflow_klanten.json` |
| Alle workflows in n8n geladen | ✅ Gereed 2026-05-16 | — |
| HTML factuurtemplate (huisstijl) | ⚠️ Generiek aanwezig, nog aanpassen | `templates/factuur_template.html` |
| Spookfactuur test (end-to-end) | ❌ Nog uitvoeren | |
| PDF generatie via Gotenberg | ⚠️ Workflow aanwezig, nog niet getest | |
| Dashboard extra laag | ❌ Nog toevoegen | |
| BTW-rapport | ❌ Nog niet geïmplementeerd | |

### ❌ Fase 2 — Webshop (nog niet gestart)

- WooCommerce webhook → n8n
- Orders opslaan in MySQL
- Automatisch facturen genereren
- Voorraad bijwerken

### ❌ Fase 3 — Rapportages (nog niet gestart)

- Omzet/kosten dashboards per maand
- BTW-aangifte rapport
- Winst & verlies overzicht
- Jaaroverzicht export

---

## 📋 TODO — Volgende sessie

- [ ] **Spookfactuur test** — end-to-end testen of de hele factuurflow werkt
- [ ] **workflow_factuur.json migreren naar MySQL** (consistent met kosten/inkoop/klanten)
- [ ] **HA terugkoppeling toevoegen aan workflow_factuur.json**
- [ ] **Factuurontwerp** aanpassen aan Natuurwaarnemer huisstijl (`templates/factuur_template.html`)
- [ ] **Dashboard extra laag** toevoegen aan het Lovelace dashboard
- [ ] **Paperless-ngx integratie** onderzoeken (gratis, zelfgehost, Docker) — voor archiveren van factuur-PDF's

---

## Technische details

### Webhook URLs (n8n productie)

| Workflow | Webhook URL |
|---|---|
| Factuur aanmaken | `http://192.168.2.35:5678/webhook/factuur-aanmaken` |
| Kosten opslaan | `http://192.168.2.35:5678/webhook/kosten-opslaan` |
| Inkoop opslaan | `http://192.168.2.35:5678/webhook/inkoop-opslaan` |
| Klant opslaan | `http://192.168.2.35:5678/webhook/klant-opslaan` |

### HA terugkoppeling webhook

n8n stuurt bevestigingen terug naar:
`http://192.168.2.17:8123/api/webhook/natuurwaarnemer_erp_bevestiging`

### Factuurnummering

Formaat: `F{YYYY}-{NNNN}`  
Voorbeelden: `F2026-0001`, `F2026-0042`

- Jaar automatisch huidig jaar
- 4-cijferige teller, beheerd via `settings`-tabel
- Teller wordt atomisch opgehoogd in de workflow

### BTW-codes

| Code | Betekenis |
|---|---|
| `21` | Hoog tarief (21%) |
| `9` | Laag tarief (9%) |
| `0` | Geen / Vrijgesteld |

### Grootboekschema (RGS)

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

---

## Vereisten

| Component | Versie | Doel |
|---|---|---|
| Home Assistant | 2024.1+ | Invoerschermen, dashboards, automations |
| n8n | 1.x | Workflow-automatisering |
| MySQL | 8.x | Lokale database |
| Gotenberg | 8.x | PDF-generatie |
| Docker | 20.x+ | Voor Gotenberg (en optioneel n8n) |
| SMTP-server | — | E-mail versturen |
| Paperless-ngx | latest | (TODO) Document archivering — gratis, zelfgehost |

---

## Bekende openstaande punten

- [ ] Spookfactuur end-to-end test nog uitvoeren
- [ ] workflow_factuur.json nog migreren van SQLite naar MySQL
- [ ] HA terugkoppeling ontbreekt nog in workflow_factuur.json
- [ ] Factuurtemplate aanpassen aan Natuurwaarnemer huisstijl
- [ ] Dashboard extra laag toevoegen
- [ ] Paperless-ngx integratie (document archivering)
- [ ] BTW-rapport is nog niet geïmplementeerd (Fase 1)
- [ ] Geen geautomatiseerde tests aanwezig
- [ ] Gotenberg-integratie nog niet end-to-end getest
- [ ] Fase 2 (Webshop) en Fase 3 (Rapportages) nog volledig te starten

---

## Toekomstige ideeën (buiten huidige scope)

- Bankkoppeling (Open Banking API)
- Scan & herken bonnetjes (OCR)
- Multi-user rechten
- Mobiele app
- Herinnerings-e-mails voor openstaande facturen
- Periodieke facturatie (abonnementen)
- Urenregistratie koppeling

---

## Links

- [README](README.md)
- [Installatie-instructies](docs/installatie.md)
- [Roadmap](docs/roadmap.md)
- [GitHub repository](https://github.com/natuurwaarnemer/Boekhouden-in-HA)
