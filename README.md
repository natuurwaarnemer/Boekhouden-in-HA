# Boekhouden in Home Assistant

Volledig ERP boekhoudsysteem gebouwd in **Home Assistant + n8n + MySQL**.
Facturen maken, inkopen boeken, BTW-rapport, winst & verlies — alles vanuit je HA dashboard.

---

## Wat zit erin

| Map/Bestand | Inhoud |
|---|---|
| `packages/` | HA YAML-packages (input helpers, automations, scripts) |
| `n8n/` | 30 n8n workflow exports (JSON) |
| `sql/schema.sql` | Database schema + initiële data |
| `server/` | Systemd service file + n8n pruning config |
| `secrets.yaml.example` | Template voor je eigen secrets |
| `install.sh` | Automatisch installatiescript |

### Dashboard-tabs
- **Klanten** — CRUD, automatisch klantnummer
- **Leveranciers** — CRUD, automatisch leveranciersnummer
- **Inkopen** — Boeken op grootboekrekening, factuurnummer leverancier
- **Verkopen** — Factuurregels invoeren
- **Facturen** — Overzicht, bewerken, verwijderen (soft-delete)
- **Wachtrij** — Concept → PDF → verzenden per email
- **Rapporten** — BTW-rapport + accountant-PDF per kwartaal/maand
- **Winst & Verlies** — W&V per grootboekrekening
- **Instellingen** — Bedrijfsgegevens die op de PDF verschijnen

---

## Snelle installatie

### Vereisten
- Ubuntu 22.04 of 24.04 LTS — fysieke machine, VM, VPS of Proxmox container
- Home Assistant OS al geïnstalleerd en bereikbaar op het netwerk
- Een HA Long-Lived Access Token (zie stap 1 hieronder)

---

### Stap 1 — HA token aanmaken
In Home Assistant:
**Profiel → Beveiliging → Langlevende toegangstokens → Token aanmaken**

Kopieer het token — je hebt het nodig in het installatiescript.

---

### Stap 2 — Installatiescript uitvoeren op de server

SSH naar je server en voer uit:

```bash
curl -fsSL https://raw.githubusercontent.com/natuurwaarnemer/Boekhouden-in-HA/master/install.sh | bash
```

Het script vraagt om:
- IP-adressen (server + HA)
- Bedrijfsgegevens (naam, adres, BTW, KVK, IBAN)
- Database wachtwoorden
- n8n gebruikersnaam + wachtwoord
- HA token
- SMTP gegevens voor facturen versturen

Toont daarna een volledige samenvatting en vraagt bevestiging voor het start.

**Het script installeert automatisch:**
- MySQL 8 + database + schema
- n8n als systemd service (met execution pruning)
- Gotenberg (PDF service) als Docker container
- Alle 30 n8n workflows (met jouw IPs en token ingevuld)
- Genereert `secrets_erp.yaml` voor HA

---

### Stap 3 — MySQL credential koppelen in n8n

Open n8n via `http://SERVER-IP:5678`

Ga naar **Credentials → New → MySQL** en vul in:
- Naam: `MySQL — erp`
- Host: `localhost`
- Database: (jouw databasenaam)
- User: (jouw db gebruiker)
- Password: (jouw db wachtwoord)

Ga daarna per workflow naar de MySQL nodes en koppel deze credential.

> **Tip:** begin met `klanten_dropdown_verversen` en `leveranciers_dropdown_verversen` — die zijn het makkelijkst te testen.

---

### Stap 4 — HA packages activeren

Kopieer de `packages/` map naar je HA config map (`/config/packages/`).

Zorg dat in `configuration.yaml` staat:
```yaml
homeassistant:
  packages: !include_dir_named packages
```

---

### Stap 5 — Secrets toevoegen aan HA

Het installatiescript heeft een bestand `secrets_erp.yaml` aangemaakt.
Kopieer de inhoud naar je HA `secrets.yaml`.

---

### Stap 6 — Logo plaatsen

Zet je bedrijfslogo als `www/logo.png` in de HA config map.
Het wordt automatisch gebruikt in factuur-PDF's.

---

### Stap 7 — HA herstarten

```
Instellingen → Systeem → Opnieuw opstarten
```

---

### Stap 8 — Dashboard importeren

Maak een nieuw dashboard aan en importeer `dashboard/dashboard_boekhoudsysteem.json`
via de RAW YAML editor van het dashboard.

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

## Handmatige installatie

Zie de gedetailleerde stappen in de [wiki](../../wiki) of lees `install.sh` als referentie.

---

## Webhook-overzicht

| Webhook pad | Workflow | Functie |
|---|---|---|
| `klant-opslaan` | klant_opslaan | Klant aanmaken |
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
| `inkoop-detail` | inkoop_detail_laden | Inkoop laden |
| `inkoop-bijwerken` | inkoop_bijwerken | Inkoop bewerken |
| `inkoop-verwijderen` | inkoop_verwijderen | Inkoop verwijderen |
| `inkopen-per-leverancier` | inkopen_per_leverancier | Lijst per leverancier |
| `factuur-aanmaken` | factuur_aanmaken | Factuur aanmaken |
| `facturen-per-klant` | facturen_per_klant | Lijst per klant |
| `factuur-detail` | factuur_detail_laden | Factuurgegevens ophalen |
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

## Bekende aandachtspunten

- **MySQL credential** moet na import handmatig gekoppeld worden in n8n (eenmalig)
- **Logo** plaatsen als `www/logo.png` in HA config map
- **Factuurnummer teller** instelt via Instellingen-tab of direct in MySQL (`settings` tabel, key `invoice_counter`)
- **Verwijderde facturen** krijgen `status = 'verwijderd'` (soft-delete)
- **n8n execution data** wordt automatisch opgeschoond (max 7 dagen / 1000 runs)

---

## Licentie

MIT — vrij te gebruiken en aan te passen.
