# Boekhouden in Home Assistant

Volledig ERP boekhoudsysteem gebouwd in **Home Assistant + n8n + MySQL**.
Facturen maken, inkopen boeken, BTW-rapport, winst & verlies — alles vanuit je HA dashboard.

---

## Wat zit erin

| Map/Bestand | Inhoud |
|---|---|
| `packages/` | HA YAML-packages (input helpers, dashboard-logica) |
| `n8n/` | 30 n8n workflow exports (JSON) |
| `sql/schema.sql` | Database schema + initiële data |
| `secrets.yaml.example` | Template voor je eigen secrets |
| `www/logo_nw.png` | Bedrijfslogo voor factuur-PDF |

### Dashboard-tabs
- **Klanten** — CRUD, automatisch klantnummer
- **Leveranciers** — CRUD, automatisch leveranciersnummer
- **Inkopen** — Boeken op grootboekrekening
- **Verkopen** — Factuurregels invoeren
- **Facturen** — Overzicht, bewerken, verwijderen (soft-delete)
- **Wachtrij** — Concept → PDF → verzenden per email
- **Rapporten** — BTW-rapport + accountant-PDF per kwartaal/maand
- **Winst & Verlies** — W&V per grootboekrekening
- **Instellingen** — Bedrijfsgegevens die op de PDF verschijnen

---

## Vereisten

- **Home Assistant** (OS of Supervised, versie 2024.x+)
- **n8n** (Docker, versie 1.x+) — voor webhooks en MySQL-queries
- **MySQL 8.x** (Docker) — database
- **Gotenberg** (Docker) — HTML naar PDF conversie
- **SMTP-server** — voor het versturen van facturen

---

## Installatie

### Stap 1 — MySQL opzetten

```bash
docker run -d \
  --name mysql-erp \
  -e MYSQL_ROOT_PASSWORD=jouwwachtwoord \
  -e MYSQL_DATABASE=erp \
  -e MYSQL_USER=erp_user \
  -e MYSQL_PASSWORD=jouwwachtwoord \
  -p 3306:3306 \
  mysql:8
```

Schema aanmaken:
```bash
mysql -h 127.0.0.1 -u erp_user -p erp < sql/schema.sql
```

### Stap 2 — Gotenberg opzetten

```bash
docker run -d \
  --name gotenberg \
  -p 3000:3000 \
  gotenberg/gotenberg:8
```

### Stap 3 — n8n opzetten

```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -e N8N_HOST=0.0.0.0 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

Open n8n via `http://jouw-ip:5678`.

#### MySQL-credential aanmaken in n8n
Ga naar **Credentials → New → MySQL** en vul in:
- Host: `jouw-mysql-ip`
- Database: `erp`
- User: `erp_user`
- Password: `jouwwachtwoord`

Noteer de credential-ID — die heb je nodig bij het importeren van de workflows.

#### Workflows importeren
Importeer alle JSON-bestanden uit de `n8n/` map via **Workflows → Import from file**.
Na import: open elke workflow, koppel de MySQL-credential en activeer hem.

> **Let op:** na activeren via API werkt de webhook soms pas na een Deactiveer → Activeer cyclus in de n8n UI.

### Stap 4 — HA packages activeren

Kopieer de `packages/` map naar je HA config-map en voeg toe aan `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Kopieer `www/logo_nw.png` naar je HA `www/` map.

### Stap 5 — Secrets instellen

Kopieer `secrets.yaml.example` naar `secrets.yaml` en vul de webhook-URLs in:

```yaml
# n8n intern IP (vanuit HA bereikbaar)
n8n_webhook_klant_opslaan:        "http://JOUW-N8N-IP:5678/webhook/klant-opslaan"
n8n_webhook_rapport_ophalen:      "http://JOUW-N8N-IP:5678/webhook/rapport-ophalen"
# ... zie secrets.yaml.example voor alle URLs
```

### Stap 6 — Dashboard aanmaken

Maak een nieuw dashboard aan in HA (Instellingen → Dashboards → Toevoegen).
Importeer de views via de YAML-editor of bouw ze na op basis van de packages.

### Stap 7 — Instellingen invullen

Open het dashboard → tab **Instellingen** → vul bedrijfsnaam, KVK, IBAN, e-mail etc. in en sla op.
Dit wordt automatisch gebruikt in factuur-PDF's en het accountantsrapport.

---

## Architectuur

```
HA Dashboard
    │
    ├─ input_button drukken
    │       │
    │       └─▶ rest_command → n8n webhook
    │                               │
    │                   ┌───────────┼───────────┐
    │                   ▼           ▼           ▼
    │                MySQL      Gotenberg     SMTP
    │               (data)      (PDF)        (email)
    │                   │
    └─◀─ HA script ◀────┘
         (vult input_text entiteiten)
```

---

## Webhook-overzicht

| Webhook pad | Workflow | Functie |
|---|---|---|
| `klant-opslaan` | klant_opslaan | Klant aanmaken/bijwerken |
| `klant-laden` | klant_laden | Klantgegevens ophalen |
| `klant-bijwerken` | klant_bijwerken | Klant bewerken |
| `klant-verwijderen` | klant_verwijderen | Klant verwijderen |
| `klanten-verversen` | klanten_dropdown_verversen | Dropdown bijwerken |
| `leverancier-opslaan` | leverancier_opslaan | Leverancier aanmaken |
| `leverancier-laden` | leverancier_laden | Leveranciergegevens ophalen |
| `leverancier-bijwerken` | leverancier_bijwerken | Leverancier bewerken |
| `leverancier-verwijderen` | leverancier_verwijderen | Leverancier verwijderen |
| `leveranciers-verversen` | leveranciers_dropdown_verversen | Dropdown bijwerken |
| `inkoop-opslaan` | inkoop_opslaan | Inkoop boeken |
| `inkoop-detail-laden` | inkoop_detail_laden | Inkoop laden |
| `inkoop-bijwerken` | inkoop_bijwerken | Inkoop bewerken |
| `inkoop-verwijderen` | inkoop_verwijderen | Inkoop verwijderen |
| `inkopen-per-leverancier` | inkopen_per_leverancier | Lijst per leverancier |
| `factuur-aanmaken` | factuur_aanmaken | Factuur aanmaken |
| `facturen-per-klant` | facturen_per_klant | Lijst per klant |
| `factuur-detail-laden` | factuur_detail_laden | Factuurgegevens ophalen |
| `factuur-bijwerken` | factuur_bijwerken | Factuur bewerken |
| `factuur-verwijderen` | factuur_verwijderen | Factuur verwijderen (soft) |
| `wachtrij-ophalen` | wachtrij_ophalen | Concept-facturen ophalen |
| `wachtrij-versturen` | wachtrij_versturen | Factuur per email versturen |
| `rapport-ophalen` | rapport_ophalen | BTW-rapport laden |
| `rapport-pdf` | rapport_pdf | Accountant-PDF emailen |
| `kostensoort-ophalen` | wv_rapport_ophalen | W&V rapport laden |
| `kostensoort-pdf` | wv_rapport_pdf | W&V PDF emailen |
| `instellingen-opslaan` | instellingen_opslaan | Bedrijfsdata opslaan |
| `instellingen-laden` | instellingen_laden | Bedrijfsdata ophalen |

---

## Bekende beperkingen / aandachtspunten

- **Factuur-PDF's** worden opgeslagen in `/data/facturen/` in de n8n container. Zorg dat deze map persistent is (Docker volume).
- **Logo** moet bereikbaar zijn via de HA `www/` map op `http://HA-IP:8123/local/logo_nw.png`.
- **n8n 0-items probleem**: flows met GROUP BY gebruiken een `UNION ALL SELECT '__geen__'` sentinel om te voorkomen dat n8n de flow stopt bij lege resultaten.
- **Factuurnummer** wordt bijgehouden in de `settings` tabel (`invoice_counter`). Stel de startwaarde in via de Instellingen-tab of direct in MySQL.
- **Verwijderde facturen** krijgen `status = 'verwijderd'` (soft-delete) — ze blijven in de DB maar tellen niet mee in rapporten.

---

## Licentie

MIT — vrij te gebruiken en aan te passen.
