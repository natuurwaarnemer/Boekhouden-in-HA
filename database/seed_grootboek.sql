-- =============================================================
-- Natuurwaarnemer ERP — Seed: Grootboekrekeningen (volledig RGS)
-- =============================================================
-- Referentie Grootboekschema (RGS) — series 0xxx t/m 9xxx
-- BTW-codes: H = hoog (21%), L = laag (9%), V = vrijgesteld, G = geen BTW

INSERT OR IGNORE INTO ledger_accounts (code, name, type, btw_code) VALUES
    -- 0xxx — Vaste activa
    ('0100', 'Inventaris en inrichting',          'activa',         'H'),
    ('0110', 'Afschrijving inventaris',           'activa',         'G'),
    ('0200', 'Hardware en computers',             'activa',         'H'),
    ('0210', 'Afschrijving hardware',             'activa',         'G'),
    ('0300', 'Vervoermiddelen',                   'activa',         'H'),
    ('0310', 'Afschrijving vervoermiddelen',      'activa',         'G'),
    ('0400', 'Immateriële vaste activa',          'activa',         'G'),
    ('0410', 'Afschrijving immateriële activa',   'activa',         'G'),
    ('0500', 'Gebouwen en terreinen',             'activa',         'G'),
    ('0510', 'Afschrijving gebouwen',             'activa',         'G'),

    -- 1xxx — Vlottende activa
    ('1000', 'Kas',                               'activa',         'G'),
    ('1010', 'Kleine kas',                        'activa',         'G'),
    ('1100', 'Bank',                              'activa',         'G'),
    ('1110', 'Spaarrekening',                     'activa',         'G'),
    ('1200', 'Kruisposten',                       'activa',         'G'),
    ('1300', 'Debiteuren',                        'activa',         'G'),
    ('1310', 'Vooruitontvangen bedragen',         'activa',         'G'),
    ('1400', 'Te vorderen omzetbelasting',        'activa',         'G'),
    ('1410', 'Te vorderen BTW hoog',              'activa',         'G'),
    ('1420', 'Te vorderen BTW laag',              'activa',         'G'),
    ('1500', 'Overige vorderingen',               'activa',         'G'),
    ('1510', 'Vooruitbetaalde kosten',            'activa',         'G'),
    ('1600', 'Te vorderen BTW',                   'activa',         'G'),

    -- 2xxx — Voorraden
    ('2000', 'Voorraad handelsgoederen',          'activa',         'H'),
    ('2100', 'Voorraad grondstoffen',             'activa',         'H'),
    ('2200', 'Onderhanden werk',                  'activa',         'G'),
    ('2300', 'Voorraad gereed product',           'activa',         'H'),

    -- 3xxx — Eigen vermogen
    ('3000', 'Eigen vermogen',                    'eigen_vermogen', 'G'),
    ('3100', 'Kapitaal',                          'eigen_vermogen', 'G'),
    ('3200', 'Privéonttrekkingen',                'eigen_vermogen', 'G'),
    ('3300', 'Privéstortingen',                   'eigen_vermogen', 'G'),
    ('3400', 'Winstreserve',                      'eigen_vermogen', 'G'),
    ('3500', 'Onverdeeld resultaat',              'eigen_vermogen', 'G'),

    -- 4xxx — Schulden en inkoopkosten
    ('4000', 'Crediteuren',                       'passiva',        'G'),
    ('4100', 'Te betalen omzetbelasting',         'passiva',        'G'),
    ('4110', 'Te betalen BTW hoog',               'passiva',        'G'),
    ('4120', 'Te betalen BTW laag',               'passiva',        'G'),
    ('4200', 'Te betalen loonheffing',            'passiva',        'G'),
    ('4300', 'Te betalen sociale lasten',         'passiva',        'G'),
    ('4400', 'Inkoopkosten',                      'kosten',         'H'),
    ('4410', 'Kantoorkosten',                     'kosten',         'H'),
    ('4420', 'Reiskosten',                        'kosten',         'H'),
    ('4430', 'Marketing en reclame',              'kosten',         'H'),
    ('4440', 'Automatiseringskosten',             'kosten',         'H'),
    ('4450', 'Verzekeringen',                     'kosten',         'V'),
    ('4460', 'Telefoon en internet',              'kosten',         'H'),
    ('4470', 'Huur en leasing',                   'kosten',         'V'),
    ('4480', 'Energie en nutsvoorzieningen',      'kosten',         'V'),
    ('4490', 'Overige inkoopkosten',              'kosten',         'H'),
    ('4500', 'Te betalen BTW',                    'passiva',        'G'),
    ('4600', 'Vooruitontvangen omzet',            'passiva',        'G'),
    ('4700', 'Kortlopende leningen',              'passiva',        'G'),
    ('4800', 'Rekening-courant aandeelhouder',    'passiva',        'G'),
    ('4900', 'Overige kortlopende schulden',      'passiva',        'G'),

    -- 5xxx — Personeelskosten
    ('5000', 'Brutolonen en salarissen',          'kosten',         'G'),
    ('5100', 'Sociale lasten werkgever',          'kosten',         'G'),
    ('5200', 'Pensioenlasten',                    'kosten',         'G'),
    ('5300', 'Vakantiegeld',                      'kosten',         'G'),
    ('5400', 'Overige personeelskosten',          'kosten',         'H'),
    ('5500', 'Inhuur derden en ZZP',              'kosten',         'H'),
    ('5600', 'Uitzendkrachten',                   'kosten',         'H'),
    ('5700', 'Opleidingskosten personeel',        'kosten',         'H'),
    ('5800', 'Reiskostenvergoeding personeel',    'kosten',         'V'),
    ('5900', 'Overige personeelsvergoedingen',    'kosten',         'G'),

    -- 6xxx — Financiële kosten en afschrijvingen
    ('6000', 'Rentekosten',                       'kosten',         'G'),
    ('6100', 'Bankkosten',                        'kosten',         'V'),
    ('6200', 'Afschrijvingen inventaris',         'kosten',         'G'),
    ('6210', 'Afschrijvingen hardware',           'kosten',         'G'),
    ('6220', 'Afschrijvingen vervoermiddelen',    'kosten',         'G'),
    ('6230', 'Afschrijvingen gebouwen',           'kosten',         'G'),
    ('6240', 'Afschrijvingen immaterieel',        'kosten',         'G'),
    ('6300', 'Koersverliezen',                    'kosten',         'G'),
    ('6400', 'Financiële lasten overig',          'kosten',         'G'),
    ('6500', 'Buitengewone lasten',               'kosten',         'G'),

    -- 7xxx — Overige bedrijfskosten
    ('7000', 'Overige bedrijfskosten',            'kosten',         'H'),
    ('7100', 'Representatiekosten',               'kosten',         'H'),
    ('7200', 'Opleidingskosten',                  'kosten',         'H'),
    ('7300', 'Abonnementen en lidmaatschappen',   'kosten',         'H'),
    ('7400', 'Drukwerk en kantoorbenodigdheden',  'kosten',         'H'),
    ('7500', 'Porti en verzendkosten',            'kosten',         'H'),
    ('7600', 'Accountants- en advieskosten',      'kosten',         'H'),
    ('7700', 'Juridische kosten',                 'kosten',         'H'),
    ('7800', 'Onderhoudskosten',                  'kosten',         'H'),
    ('7900', 'Diverse bedrijfskosten',            'kosten',         'H'),

    -- 8xxx — Omzet
    ('8000', 'Omzet diensten hoog tarief',        'omzet',          'H'),
    ('8100', 'Omzet producten hoog tarief',       'omzet',          'H'),
    ('8200', 'Omzet diensten laag tarief',        'omzet',          'L'),
    ('8300', 'Omzet producten laag tarief',       'omzet',          'L'),
    ('8400', 'Omzet EU-leveringen',               'omzet',          'G'),
    ('8500', 'Omzet export buiten EU',            'omzet',          'G'),
    ('8600', 'Omzet overig',                      'omzet',          'H'),
    ('8700', 'Doorberekende kosten',              'omzet',          'H'),
    ('8800', 'Subsidies en bijdragen',            'omzet',          'G'),
    ('8900', 'Omzet vrijgesteld',                 'omzet',          'V'),

    -- 9xxx — Resultatenrekeningen
    ('9000', 'Brutowinst',                        'resultaat',      'G'),
    ('9100', 'Bedrijfsresultaat',                 'resultaat',      'G'),
    ('9200', 'Resultaat voor belasting',          'resultaat',      'G'),
    ('9300', 'Vennootschapsbelasting',            'resultaat',      'G'),
    ('9400', 'Resultaat na belasting',            'resultaat',      'G'),
    ('9900', 'Eindresultaat boekjaar',            'resultaat',      'G');
