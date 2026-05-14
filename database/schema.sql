-- =============================================================
-- Natuurwaarnemer ERP — SQLite Database Schema
-- =============================================================

-- ---------------------------------------------------------
-- Klanten
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    email       TEXT,
    address     TEXT,
    postcode    TEXT,
    city        TEXT,
    country     TEXT DEFAULT 'Nederland',
    kvk         TEXT,
    btw_number  TEXT,
    phone       TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------
-- Facturen
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS invoices (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE NOT NULL,
    customer_id    INTEGER NOT NULL,
    date           TEXT NOT NULL,
    due_date       TEXT,
    subtotal       REAL DEFAULT 0,
    btw_total      REAL DEFAULT 0,
    total          REAL DEFAULT 0,
    status         TEXT DEFAULT 'concept',
    pdf_path       TEXT,
    notes          TEXT,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- ---------------------------------------------------------
-- Factuurregels
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS invoice_items (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id        INTEGER NOT NULL,
    description       TEXT NOT NULL,
    qty               REAL DEFAULT 1,
    unit_price        REAL NOT NULL,
    btw_percentage    REAL DEFAULT 21,
    btw_amount        REAL DEFAULT 0,
    line_total        REAL DEFAULT 0,
    ledger_account_id INTEGER,
    FOREIGN KEY (invoice_id)        REFERENCES invoices(id),
    FOREIGN KEY (ledger_account_id) REFERENCES ledger_accounts(id)
);

-- ---------------------------------------------------------
-- Grootboekrekeningen
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS ledger_accounts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    code       TEXT UNIQUE NOT NULL,
    name       TEXT NOT NULL,
    type       TEXT NOT NULL,
    btw_code   TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------
-- Grootboekboekingen
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS ledger_entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT NOT NULL,
    account_id  INTEGER NOT NULL,
    description TEXT,
    debit       REAL DEFAULT 0,
    credit      REAL DEFAULT 0,
    reference   TEXT,
    journal     TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES ledger_accounts(id)
);

-- ---------------------------------------------------------
-- Kosten / uitgaven
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS expenses (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    date              TEXT NOT NULL,
    supplier          TEXT,
    description       TEXT NOT NULL,
    amount            REAL NOT NULL,
    btw_percentage    REAL DEFAULT 21,
    btw_amount        REAL DEFAULT 0,
    total             REAL NOT NULL,
    ledger_account_id INTEGER,
    receipt_path      TEXT,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ledger_account_id) REFERENCES ledger_accounts(id)
);

-- ---------------------------------------------------------
-- Producten / diensten
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT NOT NULL,
    description       TEXT,
    price             REAL NOT NULL,
    btw_percentage    REAL DEFAULT 21,
    stock             INTEGER DEFAULT 0,
    unit              TEXT DEFAULT 'stuk',
    ledger_account_id INTEGER,
    active            INTEGER DEFAULT 1,
    FOREIGN KEY (ledger_account_id) REFERENCES ledger_accounts(id)
);

-- ---------------------------------------------------------
-- Orders (bijv. WooCommerce)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE,
    customer_id  INTEGER,
    date         TEXT NOT NULL,
    subtotal     REAL DEFAULT 0,
    btw_total    REAL DEFAULT 0,
    total        REAL DEFAULT 0,
    status       TEXT DEFAULT 'nieuw',
    source       TEXT DEFAULT 'woocommerce',
    invoice_id   INTEGER,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (invoice_id)  REFERENCES invoices(id)
);

-- ---------------------------------------------------------
-- Instellingen
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS settings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key         TEXT UNIQUE NOT NULL,
    value       TEXT,
    description TEXT
);

INSERT OR IGNORE INTO settings (key, value, description) VALUES
    ('invoice_prefix',    'NW',                  'Prefix voor factuurnummers'),
    ('invoice_year',      '2026',                'Huidig boekjaar'),
    ('invoice_counter',   '0',                   'Teller voor factuurnummers (reset per jaar)'),
    ('company_name',      'Mijn Bedrijf',        'Bedrijfsnaam'),
    ('company_address',   'Straatnaam 1',        'Bedrijfsadres'),
    ('company_postcode',  '1234 AB',             'Postcode bedrijf'),
    ('company_city',      'Stad',                'Stad bedrijf'),
    ('company_email',     'info@mijnbedrijf.nl', 'E-mailadres bedrijf'),
    ('company_phone',     '',                    'Telefoonnummer bedrijf'),
    ('company_kvk',       '',                    'KvK-nummer'),
    ('company_btw',       '',                    'BTW-nummer'),
    ('company_iban',      '',                    'IBAN rekeningnummer'),
    ('btw_percentage_hoog', '21',               'Hoog BTW-tarief (%)'),
    ('btw_percentage_laag', '9',                'Laag BTW-tarief (%)'),
    ('payment_days',      '30',                  'Standaard betaaltermijn in dagen');
