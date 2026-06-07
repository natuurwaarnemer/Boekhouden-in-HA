#!/usr/bin/env python3
"""
Natuurwaarnemer Database Migratie Script
MS Access CSV Export -> SQLite Database
Versie 2.0 - Robuust met encoding auto-detect
"""

import sqlite3
import csv
import os
from datetime import datetime

# Database configuratie
DB_PATH = 'natuurwaarnemer.db'

def detect_encoding(file_path):
    """Detecteer de juiste encoding van een bestand"""
    encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    return 'latin-1'  # Fallback

def create_database():
    """Maak SQLite database en tabellen aan"""
    print("📊 Creating SQLite database...")
    
    # Verwijder oude database voor fresh start
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("   Old database removed")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabel 1: Species
    cursor.execute('''
        CREATE TABLE species (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Tabel 2: Provincies
    cursor.execute('''
        CREATE TABLE provincies (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            hashtag TEXT
        )
    ''')
    
    # Tabel 3: Camera Bodies
    cursor.execute('''
        CREATE TABLE bodies (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            hashtag TEXT
        )
    ''')
    
    # Tabel 4: Lenzen
    cursor.execute('''
        CREATE TABLE lenses (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            hashtag TEXT
        )
    ''')
    
    # Tabel 5: Instagram base tags
    cursor.execute('''
        CREATE TABLE instagram_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            species_id INTEGER,
            tags TEXT,
            FOREIGN KEY (species_id) REFERENCES species(id)
        )
    ''')
    
    # Tabel 6: Birds (hoofdtabel)
    cursor.execute('''
        CREATE TABLE birds (
            id INTEGER PRIMARY KEY,
            lfnr INTEGER,
            scientific_name TEXT NOT NULL,
            english_name TEXT,
            dutch_name_short TEXT,
            dutch_name TEXT,
            description TEXT,
            species_id INTEGER,
            province_id INTEGER,
            body_id INTEGER,
            lens_id INTEGER,
            posted_date DATE,
            instagram_scheduled_date DATE,
            FOREIGN KEY (species_id) REFERENCES species(id),
            FOREIGN KEY (province_id) REFERENCES provincies(id),
            FOREIGN KEY (body_id) REFERENCES bodies(id),
            FOREIGN KEY (lens_id) REFERENCES lenses(id)
        )
    ''')
    
    # Indexen
    cursor.execute('CREATE INDEX idx_scientific_name ON birds(scientific_name)')
    cursor.execute('CREATE INDEX idx_dutch_name ON birds(dutch_name)')
    cursor.execute('CREATE INDEX idx_posted_date ON birds(posted_date)')
    
    conn.commit()
    print("✅ Database schema created!\n")
    return conn

def clean_value(value):
    """Clean CSV waarde: verwijder quotes en whitespace"""
    if value is None:
        return None
    return value.strip('"').strip() if value else None

def import_species(conn):
    """Import species"""
    print("🦎 Importing species...")
    cursor = conn.cursor()
    
    species_list = [
        (1, 'Vogels'),
        (2, 'Zoogdieren'),
        (3, 'Vissen'),
        (4, 'Reptielen'),
        (5, 'Amfibieën'),
        (6, 'Insecten')
    ]
    
    cursor.executemany('INSERT INTO species (id, name) VALUES (?, ?)', species_list)
    conn.commit()
    print(f"✅ Imported {len(species_list)} species\n")

def import_bodies(conn):
    """Import camera bodies"""
    print("📷 Importing bodies...")
    
    file_path = 'Body.csv'
    if not os.path.exists(file_path):
        print(f"⚠️  {file_path} not found, skipping\n")
        return
    
    encoding = detect_encoding(file_path)
    cursor = conn.cursor()
    count = 0
    
    with open(file_path, 'r', encoding=encoding) as f:
        delimiter = ';' if ';' in f.readline() else ','
        f.seek(0)
        reader = csv.DictReader(f, delimiter=delimiter, quotechar='"')
        
        for row in reader:
            cursor.execute(
                'INSERT OR IGNORE INTO bodies (id, name, hashtag) VALUES (?, ?, ?)',
                (
                    clean_value(row.get('Id')),
                    clean_value(row.get('Body')),
                    clean_value(row.get('BodyHashtag'))
                )
            )
            count += 1
    
    conn.commit()
    print(f"✅ Imported {count} bodies (encoding: {encoding})\n")

def import_lenses(conn):
    """Import lenzen"""
    print("🔍 Importing lenses...")
    
    file_path = 'Lensen.csv'
    if not os.path.exists(file_path):
        print(f"⚠️  {file_path} not found, skipping\n")
        return
    
    encoding = detect_encoding(file_path)
    cursor = conn.cursor()
    count = 0
    
    with open(file_path, 'r', encoding=encoding) as f:
        delimiter = ';' if ';' in f.readline() else ','
        f.seek(0)
        reader = csv.DictReader(f, delimiter=delimiter, quotechar='"')
        
        for row in reader:
            cursor.execute(
                'INSERT OR IGNORE INTO lenses (id, name, hashtag) VALUES (?, ?, ?)',
                (
                    clean_value(row.get('Id')),
                    clean_value(row.get('Lenstype')),
                    clean_value(row.get('LensHashtag'))
                )
            )
            count += 1
    
    conn.commit()
    print(f"✅ Imported {count} lenses (encoding: {encoding})\n")

def import_provincies(conn):
    """Import provincies"""
    print("🗺️  Importing provincies...")
    
    file_path = 'Provincies.csv'
    if not os.path.exists(file_path):
        print(f"⚠️  {file_path} not found, skipping\n")
        return
    
    encoding = detect_encoding(file_path)
    cursor = conn.cursor()
    count = 0
    
    with open(file_path, 'r', encoding=encoding) as f:
        delimiter = ';' if ';' in f.readline() else ','
        f.seek(0)
        reader = csv.DictReader(f, delimiter=delimiter, quotechar='"')
        
        for row in reader:
            cursor.execute(
                'INSERT OR IGNORE INTO provincies (id, name, hashtag) VALUES (?, ?, ?)',
                (
                    clean_value(row.get('Id')),
                    clean_value(row.get('Provincies')),
                    clean_value(row.get('Hastag'))  # Typo in origineel
                )
            )
            count += 1
    
    conn.commit()
    print(f"✅ Imported {count} provincies (encoding: {encoding})\n")

def import_instagram_tags(conn):
    """Import Instagram hashtags"""
    print("#️⃣  Importing Instagram tags...")
    
    file_path = 'Instatags.csv'
    if not os.path.exists(file_path):
        print(f"⚠️  {file_path} not found, skipping\n")
        return
    
    encoding = detect_encoding(file_path)
    cursor = conn.cursor()
    count = 0
    
    with open(file_path, 'r', encoding=encoding) as f:
        delimiter = ';' if ';' in f.readline() else ','
        f.seek(0)
        reader = csv.DictReader(f, delimiter=delimiter, quotechar='"')
        
        for row in reader:
            species_name = clean_value(row.get('Species'))
            tags = clean_value(row.get('InstaHastags'))
            
            # Lookup species_id
            cursor.execute('SELECT id FROM species WHERE name = ?', (species_name,))
            result = cursor.fetchone()
            
            if result:
                cursor.execute(
                    'INSERT INTO instagram_tags (species_id, tags) VALUES (?, ?)',
                    (result[0], tags)
                )
                count += 1
    
    conn.commit()
    print(f"✅ Imported {count} Instagram tag sets (encoding: {encoding})\n")

def import_birds(conn):
    """Import alle vogels en andere dieren"""
    print("🐦 Importing birds...")
    
    file_path = 'Vogelnamen.csv'
    if not os.path.exists(file_path):
        print(f"❌ {file_path} not found!\n")
        return
    
    encoding = detect_encoding(file_path)
    print(f"   Detected encoding: {encoding}")
    
    cursor = conn.cursor()
    count = 0
    
    with open(file_path, 'r', encoding=encoding) as f:
        delimiter = ';' if ';' in f.readline() else ','
        f.seek(0)
        reader = csv.DictReader(f, delimiter=delimiter, quotechar='"')
        
        for row in reader:
            # Lookup foreign keys
            species_name = clean_value(row.get('Species'))
            province_name = clean_value(row.get('Provincies'))
            body_name = clean_value(row.get('Body'))
            lens_name = clean_value(row.get('Lensen'))
            
            species_id = None
            if species_name:
                cursor.execute('SELECT id FROM species WHERE name = ?', (species_name,))
                r = cursor.fetchone()
                species_id = r[0] if r else None
            
            province_id = None
            if province_name:
                cursor.execute('SELECT id FROM provincies WHERE name = ?', (province_name,))
                r = cursor.fetchone()
                province_id = r[0] if r else None
            
            body_id = None
            if body_name:
                cursor.execute('SELECT id FROM bodies WHERE name = ?', (body_name,))
                r = cursor.fetchone()
                body_id = r[0] if r else None
            
            lens_id = None
            if lens_name:
                cursor.execute('SELECT id FROM lenses WHERE name = ?', (lens_name,))
                r = cursor.fetchone()
                lens_id = r[0] if r else None
            
            # Insert bird
            cursor.execute('''
                INSERT OR IGNORE INTO birds (
                    id, lfnr, scientific_name, english_name, 
                    dutch_name_short, dutch_name, description,
                    species_id, province_id, body_id, lens_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                clean_value(row.get('Id')),
                clean_value(row.get('LFNR')),
                clean_value(row.get('NAMEHOWA')),
                clean_value(row.get('NAMEENGL')),
                clean_value(row.get('NAMEHOLL')),
                clean_value(row.get('HollandseNaam')),
                clean_value(row.get('Description')),
                species_id,
                province_id,
                body_id,
                lens_id
            ))
            
            count += 1
            
            # Progress indicator
            if count % 1000 == 0:
                print(f"   ... {count} records processed")
    
    conn.commit()
    print(f"✅ Imported {count} birds/animals\n")

def verify_database(conn):
    """Verificatie en statistieken"""
    print("=" * 60)
    print("📊 DATABASE STATISTICS")
    print("=" * 60)
    
    cursor = conn.cursor()
    
    tables = [
        ('species', 'Species'),
        ('provincies', 'Provincies'),
        ('bodies', 'Camera Bodies'),
        ('lenses', 'Lenses'),
        ('instagram_tags', 'Instagram Tag Sets'),
        ('birds', 'Birds/Animals')
    ]
    
    for table, label in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f"{label:25s}: {count:6d} records")
    
    # Sample bird
    print("\n" + "=" * 60)
    print("🐦 SAMPLE RECORD: Fuut")
    print("=" * 60)
    
    cursor.execute('''
        SELECT 
            b.dutch_name,
            b.scientific_name,
            b.english_name,
            substr(b.description, 1, 100) as description,
            s.name as species,
            p.name as province,
            p.hashtag as province_hashtag,
            bo.name as body,
            bo.hashtag as body_hashtag,
            l.name as lens,
            l.hashtag as lens_hashtag,
            substr(it.tags, 1, 80) as base_tags
        FROM birds b
        LEFT JOIN species s ON b.species_id = s.id
        LEFT JOIN provincies p ON b.province_id = p.id
        LEFT JOIN bodies bo ON b.body_id = bo.id
        LEFT JOIN lenses l ON b.lens_id = l.id
        LEFT JOIN instagram_tags it ON s.id = it.species_id
        WHERE b.dutch_name = 'Fuut'
        LIMIT 1
    ''')
    
    result = cursor.fetchone()
    if result:
        print(f"Dutch name:     {result[0]}")
        print(f"Scientific:     {result[1]}")
        print(f"English:        {result[2]}")
        print(f"Description:    {result[3]}..." if result[3] else "No description")
        print(f"\nMetadata:")
        print(f"  Species:      {result[4]}")
        print(f"  Province:     {result[5]}")
        print(f"  Camera:       {result[7]}")
        print(f"  Lens:         {result[9]}")
        print(f"\nHashtags:")
        print(f"  Province:     {result[6]}")
        print(f"  Body:         {result[8]}")
        print(f"  Lens:         {result[10]}")
        print(f"  Base tags:    {result[11]}..." if result[11] else "")
    else:
        print("⚠️  Sample bird 'Fuut' not found")

def main():
    """Main workflow"""
    print("\n" + "=" * 60)
    print("🦆 NATUURWAARNEMER DATABASE MIGRATIE v2.0")
    print("=" * 60)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Create database
        conn = create_database()
        
        # Import data (volgorde is belangrijk ivm foreign keys)
        import_species(conn)
        import_bodies(conn)
        import_lenses(conn)
        import_provincies(conn)
        import_instagram_tags(conn)
        import_birds(conn)
        
        # Verify
        verify_database(conn)
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Database:  {os.path.abspath(DB_PATH)}")
        print(f"Size:      {os.path.getsize(DB_PATH) / 1024 / 1024:.2f} MB")
        print(f"Finished:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()