-- =============================================================
-- Natuurwaarnemer ERP — Database Schema
-- MySQL 8.x
-- =============================================================

-- -------------------------------------------------------------
-- Klanten
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  name            VARCHAR(100) NOT NULL UNIQUE,
  type            VARCHAR(20)  DEFAULT 'klant',        -- 'klant' of 'debiteur'
  contact_person  VARCHAR(100) DEFAULT '',
  address         VARCHAR(150) DEFAULT '',
  postal_code     VARCHAR(10)  DEFAULT '',
  city            VARCHAR(100) DEFAULT '',
  country         VARCHAR(50)  DEFAULT 'Nederland',
  email           VARCHAR(100) DEFAULT '',
  phone           VARCHAR(30)  DEFAULT '',
  vat_number      VARCHAR(20)  DEFAULT '',
  kvk_number      VARCHAR(20)  DEFAULT '',
  iban            VARCHAR(34)  DEFAULT '',
  notes           VARCHAR(255) DEFAULT ''
);

-- -------------------------------------------------------------
-- Leveranciers
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS suppliers (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  name            VARCHAR(100) NOT NULL UNIQUE,
  contact_person  VARCHAR(100) DEFAULT '',
  address         VARCHAR(150) DEFAULT '',
  postal_code     VARCHAR(10)  DEFAULT '',
  city            VARCHAR(100) DEFAULT '',
  country         VARCHAR(50)  DEFAULT 'Nederland',
  email           VARCHAR(100) DEFAULT '',
  phone           VARCHAR(30)  DEFAULT '',
  vat_number      VARCHAR(20)  DEFAULT '',
  kvk_number      VARCHAR(20)  DEFAULT '',
  iban            VARCHAR(34)  DEFAULT '',
  notes           VARCHAR(255) DEFAULT ''
);

-- -------------------------------------------------------------
-- Grootboekrekeningen
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ledger_accounts (
  id    INT AUTO_INCREMENT PRIMARY KEY,
  code  VARCHAR(10)  NOT NULL UNIQUE,
  name  VARCHAR(100) NOT NULL,
  type  VARCHAR(20)  DEFAULT 'kosten'   -- 'kosten' of 'omzet'
);

-- Initiële grootboekrekeningen
INSERT IGNORE INTO ledger_accounts (code, name, type) VALUES
  -- Kosten (inkoop dropdown)
  ('4500', 'Personeelskosten',                    'kosten'),
  ('4510', 'Inhuur derden / ZZP',                 'kosten'),
  ('4600', 'Huisvestingskosten',                  'kosten'),
  ('4610', 'Energie en water',                    'kosten'),
  ('4700', 'Kantoorbenodigdheden',                'kosten'),
  ('4710', 'ICT hardware en software',            'kosten'),
  ('4720', 'Telecommunicatie',                    'kosten'),
  ('4730', 'Abonnementen en licenties',           'kosten'),
  ('4740', 'Drukwerk, porti en vrachten',         'kosten'),
  ('4750', 'Reiskosten en verblijf',              'kosten'),
  ('4800', 'Reclame en marketing',                'kosten'),
  ('4810', 'Representatiekosten',                 'kosten'),
  ('4850', 'Verzekeringen',                       'kosten'),
  ('4860', 'Juridische en adviesdiensten',        'kosten'),
  ('4870', 'Accountants- en administratiekosten', 'kosten'),
  ('4900', 'Afschrijvingen',                      'kosten'),
  ('4910', 'Bankkosten',                          'kosten'),
  ('4950', 'Overige bedrijfskosten',              'kosten'),
  ('7000', 'Inkopen',                             'kosten'),
  -- Omzet (factuur dropdown)
  ('8000', 'Omzet NL',                            'omzet'),
  ('8010', 'Omzet EU',                            'omzet');

-- -------------------------------------------------------------
-- Facturen
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS invoices (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  invoice_number VARCHAR(20)    NOT NULL UNIQUE,
  customer_id    INT            DEFAULT NULL,
  date           DATE           NOT NULL,
  due_date       DATE           DEFAULT NULL,
  subtotal       DECIMAL(10,2)  DEFAULT 0.00,
  btw_total      DECIMAL(10,2)  DEFAULT 0.00,
  total          DECIMAL(10,2)  DEFAULT 0.00,
  status         VARCHAR(20)    DEFAULT 'concept',  -- concept / verzonden / verwijderd
  pdf_path       VARCHAR(255)   DEFAULT '',
  notes          TEXT           DEFAULT NULL,
  project        VARCHAR(200)   DEFAULT '',
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);

-- -------------------------------------------------------------
-- Factuurregels
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS invoice_items (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  invoice_number VARCHAR(20)   NOT NULL,
  description    VARCHAR(255)  NOT NULL,
  quantity       DECIMAL(10,2) DEFAULT 1.00,
  unit_price     DECIMAL(10,2) DEFAULT 0.00,
  btw_rate       DECIMAL(5,2)  DEFAULT 21.00,
  btw_amount     DECIMAL(10,2) DEFAULT 0.00,
  total          DECIMAL(10,2) DEFAULT 0.00,
  FOREIGN KEY (invoice_number) REFERENCES invoices(invoice_number) ON DELETE CASCADE
);

-- -------------------------------------------------------------
-- Inkoopboekingen (expenses)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expenses (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  date              DATE           NOT NULL,
  supplier          VARCHAR(100)   DEFAULT '',
  description       VARCHAR(255)   NOT NULL,
  amount            DECIMAL(10,2)  DEFAULT 0.00,
  btw_percentage    DECIMAL(5,2)   DEFAULT 21.00,
  btw_amount        DECIMAL(10,2)  DEFAULT 0.00,
  total             DECIMAL(10,2)  DEFAULT 0.00,
  ledger_account_id INT            DEFAULT NULL,
  created_at        TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (ledger_account_id) REFERENCES ledger_accounts(id) ON DELETE SET NULL
  -- Geen invoice_number kolom
);

-- -------------------------------------------------------------
-- Grootboekboekingen
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ledger_entries (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  date        DATE           NOT NULL,
  account_id  INT            DEFAULT NULL,
  description VARCHAR(255)   DEFAULT '',
  debit       DECIMAL(10,2)  DEFAULT 0.00,
  credit      DECIMAL(10,2)  DEFAULT 0.00,
  reference   VARCHAR(50)    DEFAULT '',
  journal     VARCHAR(20)    DEFAULT '',     -- 'verkoop' of 'inkoop'
  FOREIGN KEY (account_id) REFERENCES ledger_accounts(id) ON DELETE SET NULL
);

-- -------------------------------------------------------------
-- Instellingen
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS settings (
  `key`   VARCHAR(100) NOT NULL PRIMARY KEY,
  value   TEXT         DEFAULT NULL
);

-- Initiële instellingen
INSERT IGNORE INTO settings (`key`, value) VALUES
  ('bedrijfsnaam',     'De Natuurwaarnemer'),
  ('kvk',              '4088186'),
  ('iban',             'NL46 KNAB 0776 3468 22'),
  ('adres',            ''),
  ('postcode',         ''),
  ('stad',             ''),
  ('email',            'info@natuurwaarnemer.nl'),
  ('telefoon',         ''),
  ('btw_nummer',       ''),
  ('accountant_email', ''),
  ('logo_url',         'http://192.168.2.17:8123/local/logo_nw.png'),
  ('invoice_counter',  '0');
