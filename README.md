# Natuurwaarnemer ERP

**Volledig lokaal, gratis ERP-systeem op basis van Home Assistant + n8n + SQLite — zonder cloud of abonnementen.**

Natuurwaarnemer ERP is een open-source bedrijfsbeheersysteem voor kleine ondernemers en ZZP'ers die hun facturatie, kosten, grootboek en klantenbeheer volledig zelf willen beheren. Het systeem draait op jouw eigen server of NAS, gebruikt uitsluitend gratis software en slaat alle gegevens lokaal op in SQLite.

---

## Projectdoelstelling

- **Geen abonnementen** — geen Moneybird, geen Exact Online, geen maandelijkse kosten
- **Geen cloud** — alle data blijft op jouw eigen hardware
- **Maximale controle** — open source, aanpasbaar naar eigen wensen
- **Volledig BTW-conform** — RGS grootboekschema, BTW-specificatie, 21%/9%/0%
- **Geautomatiseerd** — facturen aanmaken, PDF genereren, e-mailen en boeken in één klik

---

## Vereisten

| Component | Versie | Doel |
|---|---|---|
| [Home Assistant](https://www.home-assistant.io/) | 2024.1+ | Invoerschermen, dashboards, automations |
| [n8n](https://n8n.io/) | 1.x | Workflow-automatisering, API-koppeling |
| [SQLite](https://www.sqlite.org/) | 3.x | Lokale database |
| [Gotenberg](https://gotenberg.dev/) | 8.x | PDF-generatie via Docker |
| Docker | 20.x+ | Voor Gotenberg en optioneel n8n |
| SMTP-server | — | E-mail versturen via n8n |

---

## Mappenstructuur

```
Boekhouden-in-HA/
├── README.md
├── LICENSE
├── database/
│   ├── schema.sql              ← SQLite tabelstructuur
│   └── seed_grootboek.sql      ← RGS grootboekrekeningen
├── home-assistant/
│   ├── input_helpers.yaml      ← Input helpers voor formulieren
│   ├── automations.yaml        ← Automations → n8n webhooks
│   └── dashboard.yaml          ← Lovelace dashboard
├── n8n/
│   ├── workflow_factuur.json   ← Factuurflow
│   ├── workflow_kosten.json    ← Kostenregistratie
│   └── workflow_grootboek.json ← Rapportageflow
├── templates/
│   └── factuur_template.html   ← HTML/CSS factuurtemplate
└── docs/
    ├── installatie.md          ← Installatie-instructies
    └── roadmap.md              ← Roadmap
```

---

## Installatie

### Stap 1 — SQLite database aanmaken

```bash
sqlite3 /data/gippetto.db < database/schema.sql
```

### Stap 2 — Grootboek seed importeren

```bash
sqlite3 /data/gippetto.db < database/seed_grootboek.sql
```

### Stap 3 — HA input helpers kopiëren

Kopieer de inhoud van `home-assistant/input_helpers.yaml` naar jouw Home Assistant `/config/` map,
of voeg toe aan `configuration.yaml`:

```yaml
# configuration.yaml
homeassistant: !include_dir_merge_named includes/
```

Of plak de inhoud direct in `configuration.yaml` (of `input_select.yaml`, `input_text.yaml`, etc.).

### Stap 4 — HA automations toevoegen

Kopieer de inhoud van `home-assistant/automations.yaml` naar `/config/automations.yaml`
of voeg de automations toe via de HA UI onder **Instellingen → Automations**.

Voeg de webhook URLs toe aan `/config/secrets.yaml`:

```yaml
# secrets.yaml
n8n_webhook_factuur: "http://n8n:5678/webhook/factuur-aanmaken"
n8n_webhook_kosten: "http://n8n:5678/webhook/kosten-opslaan"
```

### Stap 5 — HA dashboard importeren

Ga naar **Instellingen → Dashboards → Dashboard toevoegen** en importeer `home-assistant/dashboard.yaml`
via de YAML-editor van een nieuw Lovelace dashboard.

### Stap 6 — n8n workflows importeren

1. Open n8n (standaard op `http://n8n:5678`)
2. Ga naar **Workflows → Importeren**
3. Importeer achtereenvolgens:
   - `n8n/workflow_factuur.json`
   - `n8n/workflow_kosten.json`
   - `n8n/workflow_grootboek.json`
4. Activeer alle drie de workflows

### Stap 7 — Gotenberg starten via Docker

```bash
docker run --rm -p 3000:3000 gotenberg/gotenberg:8
```

Of voeg toe aan je `docker-compose.yml` (zie `docs/installatie.md` voor volledig voorbeeld).

### Stap 8 — SMTP instellen in n8n

1. Ga in n8n naar **Credentials → Nieuw → SMTP**
2. Vul je SMTP-gegevens in (host, poort, gebruikersnaam, wachtwoord)
3. Koppel deze credential aan de **Send Email** node in `workflow_factuur`

### Stap 9 — n8n webhook URLs instellen in HA secrets.yaml

```yaml
# /config/secrets.yaml
n8n_webhook_factuur: "http://n8n:5678/webhook/factuur-aanmaken"
n8n_webhook_kosten: "http://n8n:5678/webhook/kosten-opslaan"
```

Herstart Home Assistant na het aanpassen van `secrets.yaml`.

---

## Factuurnummering

Facturen krijgen automatisch een uniek nummer in het formaat:

```
NW-YYYY-NNNN
```

Voorbeelden: `NW-2026-0001`, `NW-2026-0042`, `NW-2027-0001`

- **Prefix:** `NW` (Natuurwaarnemer)
- **Jaar:** automatisch huidig jaar
- **Teller:** 4-cijferig, reset elk jaar naar `0001`
- Instellingen beheerd via de `settings`-tabel in SQLite

---

## Grootboekschema (RGS)

Het systeem gebruikt het **Nederlandse Referentie Grootboekschema (RGS)** als basis:

| Reeks | Type | Omschrijving |
|---|---|---|
| 1000–1999 | Activa | Kas, bank, debiteuren, BTW-vordering |
| 3000–3999 | Eigen vermogen | Kapitaal, winstreserves |
| 4000–4999 | Passiva / Kosten | Crediteuren, BTW-schuld, bedrijfskosten |
| 8000–8999 | Omzet | Diensten, producten, vrijgesteld |

BTW-codes: `H` = hoog tarief (21%), `L` = laag tarief (9%), `V` = vrijgesteld, `G` = geen BTW

---

## Roadmap

Zie [docs/roadmap.md](docs/roadmap.md) voor de volledige roadmap.

**Fase 1 — Basis ERP:** database, HA invoerschermen, n8n factuurflow, PDF, grootboekboekingen, kosten, BTW-rapport  
**Fase 2 — Webshop:** WooCommerce koppeling, orderverwerking, automatische facturen, voorraadbeheer  
**Fase 3 — Rapportages:** omzet/kosten dashboards, BTW-aangifte, winst & verlies, jaaroverzicht

---

## Contributing

Bijdragen zijn welkom! Open een issue of pull request op GitHub.

1. Fork de repository
2. Maak een feature branch: `git checkout -b feature/mijn-feature`
3. Commit je wijzigingen: `git commit -m 'feat: voeg mijn feature toe'`
4. Push naar de branch: `git push origin feature/mijn-feature`
5. Open een Pull Request

---

## Licentie

Dit project is gelicenseerd onder de [MIT-licentie](LICENSE).  
Copyright © 2026 Natuurwaarnemer ERP Contributors
