# Installatie — Natuurwaarnemer ERP

Gedetailleerde installatie-instructies voor alle componenten van **Natuurwaarnemer ERP**.

---

## Inhoudsopgave

1. [Vereisten](#vereisten)
2. [Docker Compose opstelling](#docker-compose)
3. [SQLite database aanmaken](#sqlite-database)
4. [Home Assistant configuratie](#home-assistant)
5. [n8n workflows importeren](#n8n-workflows)
6. [SMTP configureren](#smtp)
7. [secrets.yaml voorbeeld](#secretsyaml)
8. [Testen](#testen)

---

## Vereisten

Zorg dat de volgende software geïnstalleerd is:

- **Docker** en **Docker Compose** (voor n8n en Gotenberg)
- **Home Assistant** (OS, Container of Supervised)
- **SQLite 3** (meestal al aanwezig op Linux/macOS)

---

## Docker Compose

Gebruik het onderstaande `docker-compose.yml` bestand om n8n en Gotenberg tegelijk op te starten:

```yaml
version: '3.8'

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=wijzig_dit_wachtwoord
      - N8N_HOST=n8n
      - WEBHOOK_URL=http://n8n:5678/
      - GENERIC_TIMEZONE=Europe/Amsterdam
    volumes:
      - n8n_data:/home/node/.n8n
      - /data:/data

  gotenberg:
    image: gotenberg/gotenberg:8
    container_name: gotenberg
    restart: unless-stopped
    ports:
      - "3000:3000"
    command:
      - "gotenberg"
      - "--chromium-disable-javascript=false"
      - "--chromium-allow-list=.*"

volumes:
  n8n_data:
```

Sla op als `docker-compose.yml` en start met:

```bash
docker compose up -d
```

Controleer of beide containers draaien:

```bash
docker compose ps
```

---

## SQLite Database

### Database aanmaken

Maak de datamap aan en initialiseer de database:

```bash
mkdir -p /data/facturen
sqlite3 /data/gippetto.db < database/schema.sql
```

### Grootboek seed importeren

```bash
sqlite3 /data/gippetto.db < database/seed_grootboek.sql
```

### Verificatie

```bash
sqlite3 /data/gippetto.db ".tables"
# Verwacht: customers expenses invoice_items invoices ledger_accounts
#           ledger_entries orders products settings

sqlite3 /data/gippetto.db "SELECT code, name FROM ledger_accounts ORDER BY code;"
```

### Bedrijfsinstellingen aanpassen

```bash
sqlite3 /data/gippetto.db "UPDATE settings SET value = 'Jouw Bedrijf BV' WHERE key = 'company_name';"
sqlite3 /data/gippetto.db "UPDATE settings SET value = 'NL12ABCD0123456789' WHERE key = 'company_iban';"
sqlite3 /data/gippetto.db "UPDATE settings SET value = '12345678' WHERE key = 'company_kvk';"
sqlite3 /data/gippetto.db "UPDATE settings SET value = 'NL123456789B01' WHERE key = 'company_btw';"
```

---

## Home Assistant

### Input helpers toevoegen

Kopieer de input helpers uit `home-assistant/input_helpers.yaml` naar je HA configuratie.

**Optie A — Directe import:**
```bash
# In /config/configuration.yaml toevoegen:
input_select: !include input_select.yaml
input_text: !include input_text.yaml
input_number: !include input_number.yaml
input_button: !include input_button.yaml
```

**Optie B — Alles in configuration.yaml:**
Plak de inhoud van `home-assistant/input_helpers.yaml` direct in `/config/configuration.yaml`.

### rest_command toevoegen

Voeg de volgende sectie toe aan `/config/configuration.yaml`:

```yaml
rest_command:
  n8n_factuur_webhook:
    url: !secret n8n_webhook_factuur
    method: POST
    content_type: application/json
    payload: >
      {
        "klant":        "{{ states('input_select.factuur_klant') }}",
        "project":      "{{ states('input_text.factuur_project') }}",
        "omschrijving1":"{{ states('input_text.factuur_regel1_omschrijving') }}",
        "aantal1":      {{ states('input_number.factuur_regel1_aantal') }},
        "prijs1":       {{ states('input_number.factuur_regel1_prijs') }},
        "btw1":         "{{ states('input_select.factuur_regel1_btw') }}",
        "omschrijving2":"{{ states('input_text.factuur_regel2_omschrijving') }}",
        "aantal2":      {{ states('input_number.factuur_regel2_aantal') }},
        "prijs2":       {{ states('input_number.factuur_regel2_prijs') }},
        "btw2":         "{{ states('input_select.factuur_regel2_btw') }}",
        "omschrijving3":"{{ states('input_text.factuur_regel3_omschrijving') }}",
        "aantal3":      {{ states('input_number.factuur_regel3_aantal') }},
        "prijs3":       {{ states('input_number.factuur_regel3_prijs') }},
        "btw3":         "{{ states('input_select.factuur_regel3_btw') }}",
        "notities":     "{{ states('input_text.factuur_notities') }}"
      }

  n8n_kosten_webhook:
    url: !secret n8n_webhook_kosten
    method: POST
    content_type: application/json
    payload: >
      {
        "leverancier":  "{{ states('input_text.kosten_leverancier') }}",
        "omschrijving": "{{ states('input_text.kosten_omschrijving') }}",
        "bedrag":       {{ states('input_number.kosten_bedrag') }},
        "btw":          "{{ states('input_select.kosten_btw') }}",
        "datum":        "{{ states('input_text.kosten_datum') }}",
        "grootboek":    "{{ states('input_select.kosten_grootboek') }}"
      }
```

### Automations toevoegen

Voeg de automations uit `home-assistant/automations.yaml` toe via:
- **HA UI:** Instellingen → Automations & Scènes → Automation aanmaken → YAML bewerken
- **Of:** Plak in `/config/automations.yaml`

### Dashboard importeren

1. Ga naar **Instellingen → Dashboards**
2. Klik op **Dashboard toevoegen**
3. Kies **Leeg dashboard**
4. Open het nieuwe dashboard → rechts bovenin de drie stippen → **YAML bewerken**
5. Plak de inhoud van `home-assistant/dashboard.yaml`

### HA herstarten

```bash
# Via HA CLI:
ha core restart

# Of via de UI: Instellingen → Systeem → Opnieuw opstarten
```

---

## n8n Workflows

### Importeren

1. Open n8n op `http://localhost:5678`
2. Log in met de ingestelde gebruikersnaam en wachtwoord
3. Ga naar **Workflows** in het linkermenu
4. Klik op de knop **Importeren** (↑ pijl icoon)
5. Importeer achtereenvolgens:
   - `n8n/workflow_factuur.json`
   - `n8n/workflow_kosten.json`
   - `n8n/workflow_grootboek.json`

### SQLite credential instellen

In elke geïmporteerde workflow:
1. Klik op een **SQLite** node
2. Klik op **Credential voor SQLite**
3. Maak nieuwe credential aan:
   - **Database pad:** `/data/gippetto.db`
4. Sla op en koppel aan alle SQLite nodes

### Workflows activeren

Klik voor elke workflow op de schakelaar rechtsboven om de workflow **actief** te maken.

---

## SMTP

### Credential aanmaken in n8n

1. Ga naar **Credentials** in het n8n linkermenu
2. Klik op **Nieuw**
3. Zoek op **SMTP**
4. Vul in:
   - **Host:** bijv. `smtp.gmail.com` of `mail.jouwprovider.nl`
   - **Poort:** `587` (TLS) of `465` (SSL)
   - **Gebruiker:** jouw e-mailadres
   - **Wachtwoord:** jouw e-mailwachtwoord of app-wachtwoord
5. Test de verbinding en sla op

### Send Email node koppelen

Open `workflow_factuur` in n8n, klik op de **Send Email** node en selecteer de aangemaakte SMTP credential.

---

## secrets.yaml

Voeg de volgende regels toe aan `/config/secrets.yaml` in Home Assistant:

```yaml
# Natuurwaarnemer ERP — n8n webhooks
n8n_webhook_factuur: "http://n8n:5678/webhook/factuur-aanmaken"
n8n_webhook_kosten:  "http://n8n:5678/webhook/kosten-opslaan"
```

> **Let op:** Vervang `n8n` door het IP-adres of de hostnaam van je n8n-instantie als deze niet via Docker op hetzelfde netwerk draait, bijv. `http://192.168.1.100:5678/webhook/factuur-aanmaken`.

---

## Testen

### Test factuurflow

Stuur een test-POST naar de n8n webhook:

```bash
curl -X POST http://localhost:5678/webhook/factuur-aanmaken \
  -H "Content-Type: application/json" \
  -d '{
    "klant": "Test Klant",
    "project": "Testproject",
    "omschrijving1": "Advies en consultancy",
    "aantal1": 2,
    "prijs1": 150.00,
    "btw1": "21",
    "notities": "Testnota"
  }'
```

Verwacht antwoord:
```json
{
  "succes": true,
  "bericht": "Factuur NW-2026-0001 aangemaakt",
  "factuurnummer": "NW-2026-0001"
}
```

### Test kostenflow

```bash
curl -X POST http://localhost:5678/webhook/kosten-opslaan \
  -H "Content-Type: application/json" \
  -d '{
    "leverancier": "Kantoorwinkel BV",
    "omschrijving": "Printerpapier A4",
    "bedrag": 45.00,
    "btw": "21",
    "datum": "2026-05-14",
    "grootboek": "4410 Kantoorkosten"
  }'
```

### Test rapportageflow

```bash
curl "http://localhost:5678/webhook/grootboek-rapport?periode=2026-05"
```

### Database controleren

```bash
sqlite3 /data/gippetto.db "SELECT invoice_number, total, status FROM invoices ORDER BY created_at DESC LIMIT 5;"
sqlite3 /data/gippetto.db "SELECT date, description, debit, credit FROM ledger_entries ORDER BY created_at DESC LIMIT 10;"
```
