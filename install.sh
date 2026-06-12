#!/bin/bash
# ============================================================
# Natuurwaarnemer ERP — Installatie Script
# Ubuntu 24.04 LTS
# Installeert: MySQL, n8n, Gotenberg, importeert alle workflows
# en genereert secrets.yaml voor Home Assistant
# ============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

REPO="https://raw.githubusercontent.com/natuurwaarnemer/Boekhouden-in-HA/master"
WORKFLOWS=(
  facturen_per_klant factuur_aanmaken factuur_bijwerken factuur_detail_laden
  factuur_pdf_download factuur_verwijderen inkoop_bijwerken inkoop_detail_laden
  inkoop_opslaan inkoop_verwijderen inkopen_per_leverancier instellingen_laden
  instellingen_opslaan klant_bijwerken klant_laden klant_opslaan klant_verwijderen
  klanten_dropdown_verversen leverancier_bijwerken leverancier_laden leverancier_opslaan
  leverancier_verwijderen leveranciers_dropdown_verversen rapport_ophalen rapport_pdf
  setup_settings_tabel wachtrij_ophalen wachtrij_versturen woocommerce_boekhouding
  wv_rapport_ophalen wv_rapport_pdf
)

header() {
  echo ""
  echo -e "${BLUE}${BOLD}══════════════════════════════════════════════${NC}"
  echo -e "${BLUE}${BOLD}  $1${NC}"
  echo -e "${BLUE}${BOLD}══════════════════════════════════════════════${NC}"
  echo ""
}

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
info() { echo -e "  ${YELLOW}→${NC} $1"; }
err()  { echo -e "  ${RED}✗ FOUT: $1${NC}"; exit 1; }

ask() {
  local var=$1 prompt=$2 default=$3
  if [ -n "$default" ]; then
    read -rp "  $prompt [$default]: " val
    eval "$var=\"${val:-$default}\""
  else
    read -rp "  $prompt: " val
    while [ -z "$val" ]; do
      echo -e "  ${RED}Verplicht veld.${NC}"
      read -rp "  $prompt: " val
    done
    eval "$var=\"$val\""
  fi
}

ask_password() {
  local var=$1 prompt=$2
  while true; do
    read -rsp "  $prompt: " p1; echo
    read -rsp "  Bevestig wachtwoord: " p2; echo
    if [ "$p1" = "$p2" ] && [ -n "$p1" ]; then
      eval "$var=\"$p1\""
      break
    fi
    echo -e "  ${RED}Wachtwoorden komen niet overeen of zijn leeg.${NC}"
  done
}

# ============================================================
# STAP 1 — INVOER
# ============================================================
clear
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║   Natuurwaarnemer ERP — Installatie Wizard   ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Beantwoord de vragen hieronder. Druk Enter voor de standaardwaarde."
echo ""

header "NETWERK"
ask N8N_IP        "IP-adres van DEZE server (n8n)"     "$(hostname -I | awk '{print $1}')"
ask HA_IP         "IP-adres van Home Assistant"         "192.168.1.x"
ask N8N_PORT      "Poort voor n8n"                      "5678"

header "BEDRIJFSGEGEVENS (voor factuur PDF)"
ask BEDRIJF_NAAM     "Bedrijfsnaam"
ask BEDRIJF_ADRES    "Adres (straat + huisnummer)"
ask BEDRIJF_POSTCODE "Postcode"
ask BEDRIJF_STAD     "Stad"
ask BEDRIJF_EMAIL    "E-mailadres"
ask BEDRIJF_TEL      "Telefoonnummer"
ask BEDRIJF_BTW      "BTW-nummer (bijv. NL123456789B01)"
ask BEDRIJF_KVK      "KVK-nummer"
ask BEDRIJF_IBAN     "IBAN"
ask BEDRIJF_BANK     "Bank (bijv. Rabobank)"

header "DATABASE"
ask    DB_NAME     "MySQL databasenaam"    "erp"
ask    DB_USER     "MySQL gebruiker"       "erp"
ask_password DB_PASS "MySQL wachtwoord voor gebruiker '$DB_USER'"
ask_password DB_ROOT_PASS "MySQL ROOT wachtwoord"

header "N8N TOEGANG"
ask          N8N_USER "n8n gebruikersnaam"   "admin"
ask_password N8N_PASS "n8n wachtwoord"

header "HOME ASSISTANT"
echo -e "  ${YELLOW}Het HA Long-Lived Access Token maak je aan in HA:${NC}"
echo -e "  Profiel → Beveiliging → Langlevende toegangstokens → Token aanmaken"
echo ""
ask HA_TOKEN "HA Long-Lived Access Token"

header "E-MAIL (voor facturen versturen)"
ask MAIL_FROM   "Afzender e-mailadres"             "$BEDRIJF_EMAIL"
ask MAIL_SERVER "SMTP server"                       "smtp.gmail.com"
ask MAIL_PORT   "SMTP poort"                        "587"
ask MAIL_USER   "SMTP gebruikersnaam"               "$BEDRIJF_EMAIL"
ask_password MAIL_PASS "SMTP wachtwoord / app-wachtwoord"

# ============================================================
# STAP 2 — SAMENVATTING + BEVESTIGING
# ============================================================
clear
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║            Controleer je invoer              ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}NETWERK${NC}"
echo -e "    n8n server IP  : $N8N_IP:$N8N_PORT"
echo -e "    HA server IP   : $HA_IP"
echo ""
echo -e "  ${BOLD}BEDRIJF${NC}"
echo -e "    Naam            : $BEDRIJF_NAAM"
echo -e "    Adres           : $BEDRIJF_ADRES, $BEDRIJF_POSTCODE $BEDRIJF_STAD"
echo -e "    E-mail          : $BEDRIJF_EMAIL"
echo -e "    Telefoon        : $BEDRIJF_TEL"
echo -e "    BTW             : $BEDRIJF_BTW"
echo -e "    KVK             : $BEDRIJF_KVK"
echo -e "    IBAN            : $BEDRIJF_IBAN ($BEDRIJF_BANK)"
echo ""
echo -e "  ${BOLD}DATABASE${NC}"
echo -e "    Database        : $DB_NAME"
echo -e "    Gebruiker       : $DB_USER"
echo -e "    Wachtwoord      : ****"
echo ""
echo -e "  ${BOLD}N8N${NC}"
echo -e "    Gebruiker       : $N8N_USER"
echo -e "    Wachtwoord      : ****"
echo ""
echo -e "  ${BOLD}E-MAIL${NC}"
echo -e "    Van             : $MAIL_FROM"
echo -e "    SMTP            : $MAIL_SERVER:$MAIL_PORT"
echo -e "    Gebruiker       : $MAIL_USER"
echo ""
read -rp "  Alles correct? Installatie starten? (ja/nee): " BEVESTIG
if [ "$BEVESTIG" != "ja" ]; then
  echo "  Installatie afgebroken. Start opnieuw."
  exit 0
fi

# ============================================================
# STAP 3 — INSTALLATIE
# ============================================================

header "SYSTEEM PAKKETTEN"
info "apt update..."
sudo apt-get update -qq
info "Installeer curl, git, wget, jq, mysql-server, docker.io, nodejs, npm..."
sudo apt-get install -y -qq curl git wget jq mysql-server docker.io nodejs npm
sudo npm install -g n8n
ok "Pakketten geïnstalleerd"

# ============================================================
header "MYSQL SETUP"
info "MySQL root wachtwoord instellen..."
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$DB_ROOT_PASS'; FLUSH PRIVILEGES;"
info "Database en gebruiker aanmaken..."
sudo mysql -u root -p"$DB_ROOT_PASS" -e "
  CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
  GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost';
  FLUSH PRIVILEGES;
"
info "Schema laden..."
SCHEMA_FILE=$(mktemp)
curl -sf "$REPO/sql/schema.sql" -o "$SCHEMA_FILE" || err "Kon schema.sql niet downloaden"
mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$SCHEMA_FILE"
rm "$SCHEMA_FILE"

info "Bedrijfsgegevens instellen in database..."
mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
  INSERT INTO settings (key_name, value) VALUES
    ('company_name',    '$BEDRIJF_NAAM'),
    ('company_address', '$BEDRIJF_ADRES'),
    ('company_zip',     '$BEDRIJF_POSTCODE'),
    ('company_city',    '$BEDRIJF_STAD'),
    ('company_email',   '$BEDRIJF_EMAIL'),
    ('company_phone',   '$BEDRIJF_TEL'),
    ('company_vat',     '$BEDRIJF_BTW'),
    ('company_kvk',     '$BEDRIJF_KVK'),
    ('company_iban',    '$BEDRIJF_IBAN'),
    ('company_bank',    '$BEDRIJF_BANK'),
    ('mail_from',       '$MAIL_FROM'),
    ('mail_server',     '$MAIL_SERVER'),
    ('mail_port',       '$MAIL_PORT'),
    ('mail_user',       '$MAIL_USER'),
    ('mail_pass',       '$MAIL_PASS')
  ON DUPLICATE KEY UPDATE value = VALUES(value);
" 2>/dev/null || info "Settings tabel nog niet aanwezig — wordt gevuld door n8n workflow"
ok "MySQL klaar"

# ============================================================
header "N8N SETUP"
info "n8n configuratiemap aanmaken..."
mkdir -p ~/.n8n

info "Pruning configuratie schrijven..."
cat > ~/.n8n/pruning.env << EOF
EXECUTIONS_DATA_PRUNE=true
EXECUTIONS_DATA_MAX_AGE=168
EXECUTIONS_DATA_MAX_COUNT=1000
EXECUTIONS_DATA_SAVE_ON_SUCCESS=none
EXECUTIONS_DATA_SAVE_ON_ERROR=all
EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS=false
EOF

N8N_ENCRYPT_KEY=$(openssl rand -base64 32 | tr -d '=+/' | head -c 32)
cat > ~/.n8n/config << EOF
{
  "encryptionKey": "$N8N_ENCRYPT_KEY"
}
EOF

info "Systemd service aanmaken..."
sudo tee /etc/systemd/system/n8n.service > /dev/null << EOF
[Unit]
Description=n8n
After=network.target mysql.service

[Service]
Type=simple
User=$USER
ExecStart=$(which n8n) start
Restart=on-failure
RestartSec=5
Environment=N8N_PORT=$N8N_PORT
Environment=N8N_PROTOCOL=http
Environment=N8N_HOST=0.0.0.0
Environment=N8N_SECURE_COOKIE=false
Environment=N8N_BASIC_AUTH_ACTIVE=true
Environment=N8N_BASIC_AUTH_USER=$N8N_USER
Environment=N8N_BASIC_AUTH_PASSWORD=$N8N_PASS
Environment=N8N_ALLOW_EXEC=true
Environment=GENERIC_TIMEZONE=Europe/Amsterdam
Environment=TZ=Europe/Amsterdam
EnvironmentFile=/home/$USER/.n8n/pruning.env

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable n8n
sudo systemctl start n8n
info "Wachten tot n8n opgestart is (30 seconden)..."
sleep 30
ok "n8n gestart"

# ============================================================
header "GOTENBERG (PDF service)"
info "Gotenberg container starten..."
sudo docker run -d \
  --name gotenberg \
  --restart unless-stopped \
  -p 3000:3000 \
  gotenberg/gotenberg:8
ok "Gotenberg draait op poort 3000"

# ============================================================
header "N8N WORKFLOWS IMPORTEREN"
info "Workflows downloaden en aanpassen (IP + token)..."
WORKFLOW_DIR=$(mktemp -d)

for WF in "${WORKFLOWS[@]}"; do
  WF_FILE="$WORKFLOW_DIR/${WF}.json"
  curl -sf "$REPO/n8n/${WF}.json" -o "$WF_FILE" || { info "Overgeslagen: ${WF}.json"; continue; }

  # Vervang hardcoded HA IP en token
  sed -i \
    -e "s|192\.168\.2\.17:8123|$HA_IP:8123|g" \
    -e "s|Bearer eyJ[A-Za-z0-9._-]*|Bearer $HA_TOKEN|g" \
    -e "s|192\.168\.2\.35:5678|$N8N_IP:$N8N_PORT|g" \
    "$WF_FILE"
done

info "Workflows importeren via n8n CLI..."
for WF_FILE in "$WORKFLOW_DIR"/*.json; do
  WF_NAME=$(basename "$WF_FILE" .json)
  n8n import:workflow --input="$WF_FILE" 2>/dev/null && ok "Geïmporteerd: $WF_NAME" || info "Overgeslagen: $WF_NAME"
done

rm -rf "$WORKFLOW_DIR"
info "n8n herstarten zodat workflows actief zijn..."
sudo systemctl restart n8n
sleep 15
ok "Workflows geïmporteerd"

# ============================================================
header "HOME ASSISTANT SECRETS.YAML"
SECRETS_FILE="$(pwd)/secrets_erp.yaml"
cat > "$SECRETS_FILE" << EOF
# Gegenereerd door install.sh op $(date +%d-%m-%Y)
# Kopieer de inhoud naar je HA secrets.yaml

n8n_webhook_klant:                    "http://$N8N_IP:$N8N_PORT/webhook/klant-opslaan"
n8n_webhook_ververs_klanten:          "http://$N8N_IP:$N8N_PORT/webhook/ververs-klanten"
n8n_webhook_ververs_leveranciers:     "http://$N8N_IP:$N8N_PORT/webhook/ververs-leveranciers"
n8n_webhook_leverancier:              "http://$N8N_IP:$N8N_PORT/webhook/leverancier-opslaan"
n8n_webhook_leverancier_laden:        "http://$N8N_IP:$N8N_PORT/webhook/leverancier-laden"
n8n_webhook_leverancier_bijwerken:    "http://$N8N_IP:$N8N_PORT/webhook/leverancier-bijwerken"
n8n_webhook_leverancier_verwijderen:  "http://$N8N_IP:$N8N_PORT/webhook/leverancier-verwijderen"
n8n_webhook_klant_laden:              "http://$N8N_IP:$N8N_PORT/webhook/klant-laden"
n8n_webhook_klant_bijwerken:          "http://$N8N_IP:$N8N_PORT/webhook/klant-bijwerken"
n8n_webhook_klant_verwijderen:        "http://$N8N_IP:$N8N_PORT/webhook/klant-verwijderen"
n8n_webhook_factuur:                  "http://$N8N_IP:$N8N_PORT/webhook/factuur-aanmaken"
n8n_webhook_inkoop:                   "http://$N8N_IP:$N8N_PORT/webhook/inkoop-opslaan"
n8n_webhook_wachtrij_ophalen:         "http://$N8N_IP:$N8N_PORT/webhook/wachtrij-ophalen"
n8n_webhook_wachtrij_versturen:       "http://$N8N_IP:$N8N_PORT/webhook/wachtrij-versturen"
n8n_webhook_facturen_per_klant:       "http://$N8N_IP:$N8N_PORT/webhook/facturen-per-klant"
n8n_webhook_factuur_detail:           "http://$N8N_IP:$N8N_PORT/webhook/factuur-detail"
n8n_webhook_factuur_bijwerken:        "http://$N8N_IP:$N8N_PORT/webhook/factuur-bijwerken"
n8n_webhook_factuur_verwijderen:      "http://$N8N_IP:$N8N_PORT/webhook/factuur-verwijderen"
n8n_webhook_inkopen_per_lev:          "http://$N8N_IP:$N8N_PORT/webhook/inkopen-per-leverancier"
n8n_webhook_inkoop_detail:            "http://$N8N_IP:$N8N_PORT/webhook/inkoop-detail"
n8n_webhook_inkoop_bijwerken:         "http://$N8N_IP:$N8N_PORT/webhook/inkoop-bijwerken"
n8n_webhook_inkoop_verwijderen:       "http://$N8N_IP:$N8N_PORT/webhook/inkoop-verwijderen"
n8n_ha_token:                         "$HA_TOKEN"
EOF
ok "secrets_erp.yaml aangemaakt: $SECRETS_FILE"

# ============================================================
header "INSTALLATIE VOLTOOID"
echo -e "  ${GREEN}${BOLD}Alles is geïnstalleerd!${NC}"
echo ""
echo -e "  ${BOLD}Samenvatting van wat er gedaan is:${NC}"
echo -e "    ✓ MySQL database '$DB_NAME' aangemaakt"
echo -e "    ✓ Database schema geladen"
echo -e "    ✓ n8n geïnstalleerd en actief op poort $N8N_PORT"
echo -e "    ✓ Gotenberg actief op poort 3000"
echo -e "    ✓ ${#WORKFLOWS[@]} n8n workflows geïmporteerd"
echo -e "    ✓ secrets_erp.yaml gegenereerd"
echo ""
echo -e "  ${BOLD}${YELLOW}Nog handmatig te doen:${NC}"
echo ""
echo -e "  1. Open n8n: ${BLUE}http://$N8N_IP:$N8N_PORT${NC}"
echo -e "     → Ga naar Credentials → New → MySQL"
echo -e "     → Naam: 'MySQL — erp'"
echo -e "     → Host: localhost, DB: $DB_NAME"
echo -e "     → User: $DB_USER, Wachtwoord: (jouw DB wachtwoord)"
echo -e "     → Koppel deze credential aan alle workflow MySQL nodes"
echo ""
echo -e "  2. Kopieer ${BLUE}$SECRETS_FILE${NC} naar je HA secrets.yaml"
echo ""
echo -e "  3. Kopieer de ERP packages naar HA:"
echo -e "     ${BLUE}https://github.com/natuurwaarnemer/Boekhouden-in-HA/tree/master/packages${NC}"
echo ""
echo -e "  4. HA herstarten"
echo ""
echo -e "  ${BOLD}Inloggegevens:${NC}"
echo -e "    n8n     : http://$N8N_IP:$N8N_PORT  →  $N8N_USER / (jouw wachtwoord)"
echo -e "    MySQL   : $DB_NAME / $DB_USER"
echo ""
