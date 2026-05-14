-- =============================================================
-- Natuurwaarnemer ERP — Seed: Grootboekrekeningen (RGS)
-- =============================================================
-- Referentie Grootboekschema (RGS) — standaard voor Nederlandse boekhouding
-- BTW-codes: H = hoog (21%), L = laag (9%), V = vrijgesteld, G = geen BTW

INSERT OR IGNORE INTO ledger_accounts (code, name, type, btw_code) VALUES
    -- Activa
    ('1000', 'Kas',                    'activa',        'G'),
    ('1100', 'Bank',                   'activa',        'G'),
    ('1300', 'Debiteuren',             'activa',        'G'),
    ('1600', 'Te vorderen BTW',        'activa',        'G'),

    -- Passiva
    ('4000', 'Crediteuren',            'passiva',       'G'),
    ('4500', 'Te betalen BTW',         'passiva',       'G'),

    -- Eigen vermogen
    ('3000', 'Eigen vermogen',         'eigen_vermogen','G'),

    -- Omzet
    ('8000', 'Omzet diensten',         'omzet',         'H'),
    ('8100', 'Omzet producten',        'omzet',         'H'),
    ('8900', 'Omzet vrijgesteld',      'omzet',         'V'),

    -- Kosten
    ('4400', 'Inkoopkosten',           'kosten',        'H'),
    ('4410', 'Kantoorkosten',          'kosten',        'H'),
    ('4420', 'Reiskosten',             'kosten',        'H'),
    ('4430', 'Marketing',              'kosten',        'H'),
    ('4440', 'Automatiseringskosten',  'kosten',        'H'),
    ('4450', 'Verzekeringen',          'kosten',        'V'),
    ('4460', 'Telefoon en internet',   'kosten',        'H');
