# Context — Natuurwaarnemer ERP

> **Aangemaakt:** 2026-05-15  
> **Doel:** Overzicht van de huidige status van het project voor gebruik als context in Copilot Spaces en voor nieuwe bijdragers.

---

## Wat is dit project?

**Natuurwaarnemer ERP** is een volledig lokaal, gratis ERP-systeem voor kleine ondernemers en ZZP'ers, gebouwd op:

- **Home Assistant** — invoerschermen, dashboards, automations
- **n8n** — workflow-automatisering en API-koppelingen
- **SQLite** — lokale database (geen cloud)
- **Gotenberg** — PDF-generatie via Docker
- **SMTP** — e-mail versturen via n8n

Geen abonnementen, geen cloud, alle data blijft op eigen hardware. Volledig BTW-conform met RGS grootboekschema.

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
│   ├── workflow_factuur.json        ✅ Aanwezig — Factuurflow (PDF + e-mail + grootboek)
│   ├── workflow_kosten.json         ✅ Aanwezig — Kostenregistratie
│   ├── workflow_inkoop.json         ❌ Nog aanmaken (morgen)
│   └── workflow_klanten.json        ❌ Nog aanmaken (morgen)
├── templates/
│   └── factuur_template.html        ⚠️ Aanwezig — nog aanpassen aan Natuurwaarnemer huisstijl
└── docs/
    ├── installatie.md               ✅ Aanwezig — Installatie-instructies
    └── roadmap.md                   ✅ Aanwezig — Roadmap
```

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
| n8n factuurflow | ✅ Aanwezig | `n8n/workflow_factuur.json` |
| n8n kostenregistratie | ✅ Aanwezig | `n8n/workflow_kosten.json` |
| n8n inkoop workflow | ❌ Nog aanmaken | `n8n/workflow_inkoop.json` |
| n8n klanten workflow | ❌ Nog aanmaken | `n8n/workflow_klanten.json` |
| HTML factuurtemplate (huisstijl) | ⚠️ Generiek aanwezig, nog aanpassen | `templates/factuur_template.html` |
| Spookfactuur test (end-to-end) | ❌ Nog uitvoeren | Morgen |
| PDF generatie via Gotenberg | ⚠️ Workflow aanwezig, nog niet getest |  |
| Dashboard extra laag | ❌ Nog toevoegen | Morgen |
| BTW-rapport | ❌ Nog niet geïmplementeerd | |

### ❌ Fase 2 — Webshop (nog niet gestart)

- WooCommerce webhook → n8n
- Orders opslaan in SQLite
- Automatisch facturen genereren
- Voorraad bijwerken

### ❌ Fase 3 — Rapportages (nog niet gestart)

- Omzet/kosten dashboards per maand
- BTW-aangifte rapport
- Winst & verlies overzicht
- Jaaroverzicht export

---

## 📋 TODO — Morgen (2026-05-16)

- [ ] **workflow_inkoop.json** aanmaken in n8n map
- [ ] **workflow_klanten.json** aanmaken in n8n map
- [ ] **Spookfactuur test** — end-to-end testen of de hele factuurflow werkt
- [ ] **Factuurontwerp** aanpassen aan Natuurwaarnemer huisstijl (`templates/factuur_template.html`)
- [ ] **Dashboard extra laag** toevoegen aan het Lovelace dashboard
- [ ] **Paperless-ngx integratie** onderzoeken (gratis, zelfgehost, Docker) — voor archiveren van factuur-PDF's

---

## Technische details

### Factuurnummering

Formaat: `NW-YYYY-NNNN`  
Voorbeelden: `NW-2026-0001`, `NW-2026-0042`

- Prefix `NW` (Natuurwaarnemer)
- Jaar automatisch huidig jaar
- 4-cijferige teller, reset elk jaar naar `0001`
- Beheerd via `settings`-tabel in SQLite

### BTW-codes

| Code | Betekenis |
|---|---|
| `H` | Hoog tarief (21%) |
| `L` | Laag tarief (9%) |
| `V` | Vrijgesteld |
| `G` | Geen BTW |

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
| SQLite | 3.x | Lokale database |
| Gotenberg | 8.x | PDF-generatie |
| Docker | 20.x+ | Voor Gotenberg (en optioneel n8n) |
| SMTP-server | — | E-mail versturen |
| Paperless-ngx | latest | (TODO) Document archivering — gratis, zelfgehost |

---

## Bekende openstaande punten

- [ ] workflow_inkoop.json en workflow_klanten.json nog aanmaken
- [ ] Spookfactuur end-to-end test nog uitvoeren
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
