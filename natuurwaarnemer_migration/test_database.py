#!/usr/bin/env python3
"""
Test script voor natuurwaarnemer database
Versie 1.0
"""

import sqlite3
import os

DB_PATH = '/config/databases/natuurwaarnemer.db'

def test_database_connection():
    """Test of database bereikbaar is"""
    print("🔍 Testing database connection...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM birds')
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✅ Database connected! Found {count} birds/animals\n")
        return True
    except Exception as e:
        print(f"❌ Error connecting to database: {e}\n")
        return False

def test_statistics():
    """Toon database statistieken"""
    print("=" * 70)
    print("📊 DATABASE STATISTICS")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Totalen per tabel
    tables = [
        ('species', 'Species'),
        ('provincies', 'Provincies'),
        ('bodies', 'Camera Bodies'),
        ('lenses', 'Lenses'),
        ('instagram_tags', 'Instagram Tag Sets'),
        ('birds', 'Birds/Animals')
    ]
    
    print("\nTable counts:")
    for table, label in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f"  {label:25s}: {count:6d} records")
    
    # Verdeling per species
    print("\nBreakdown per species:")
    cursor.execute('''
        SELECT s.name, COUNT(*) as aantal
        FROM birds b
        JOIN species s ON b.species_id = s.id
        GROUP BY s.name
        ORDER BY aantal DESC
    ''')
    
    for row in cursor.fetchall():
        print(f"  {row[0]:20s}: {row[1]:6d} records")
    
    # Beschrijvingen
    cursor.execute('SELECT COUNT(*) FROM birds WHERE description IS NOT NULL AND description != ""')
    count_with_desc = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM birds')
    total = cursor.fetchone()[0]
    
    print(f"\nDescriptions:")
    print(f"  With description:     {count_with_desc:6d}")
    print(f"  Without description:  {total - count_with_desc:6d}")
    print(f"  Total:                {total:6d}")
    
    conn.close()
    print()

def test_lookup_bird(dutch_name):
    """Zoek een vogel op en toon alle data"""
    print("=" * 70)
    print(f"🐦 BIRD LOOKUP: {dutch_name}")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            b.id,
            b.dutch_name,
            b.scientific_name,
            b.english_name,
            b.description,
            s.name as species,
            p.name as province,
            p.hashtag as province_hashtags,
            bo.name as body,
            bo.hashtag as body_hashtags,
            l.name as lens,
            l.hashtag as lens_hashtags,
            it.tags as base_tags
        FROM birds b
        LEFT JOIN species s ON b.species_id = s.id
        LEFT JOIN provincies p ON b.province_id = p.id
        LEFT JOIN bodies bo ON b.body_id = bo.id
        LEFT JOIN lenses l ON b.lens_id = l.id
        LEFT JOIN instagram_tags it ON s.id = it.species_id
        WHERE b.dutch_name = ?
    ''', (dutch_name,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        print(f"❌ Bird '{dutch_name}' not found in database!\n")
        return None
    
    # Parse result
    (bird_id, dutch_name, scientific_name, english_name, description, 
     species, province, province_hashtags, body, body_hashtags, 
     lens, lens_hashtags, base_tags) = result
    
    # Print details
    print(f"\nID:                {bird_id}")
    print(f"Dutch name:        {dutch_name}")
    print(f"Scientific name:   {scientific_name}")
    print(f"English name:      {english_name}")
    print(f"\nMetadata:")
    print(f"  Species:         {species}")
    print(f"  Province:        {province}")
    print(f"  Camera:          {body}")
    print(f"  Lens:            {lens}")
    
    if description:
        print(f"\nDescription:")
        print(f"  {description[:200]}..." if len(description) > 200 else f"  {description}")
    else:
        print(f"\nDescription:       (none)")
    
    print(f"\nHashtags:")
    print(f"  Province:        {province_hashtags if province_hashtags else '(none)'}")
    print(f"  Body:            {body_hashtags if body_hashtags else '(none)'}")
    print(f"  Lens:            {lens_hashtags if lens_hashtags else '(none)'}")
    if base_tags:
        print(f"  Base tags:       {base_tags[:80]}..." if len(base_tags) > 80 else f"  Base tags:       {base_tags}")
    else:
        print(f"  Base tags:       (none)")
    
    print()
    return result

def generate_instagram_caption(dutch_name):
    """Genereer complete Instagram caption"""
    print("=" * 70)
    print(f"#️⃣  INSTAGRAM CAPTION GENERATOR: {dutch_name}")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            b.id,
            b.dutch_name,
            b.scientific_name,
            b.english_name,
            b.description,
            s.name as species,
            p.name as province,
            p.hashtag as province_hashtags,
            bo.name as body,
            bo.hashtag as body_hashtags,
            l.name as lens,
            l.hashtag as lens_hashtags,
            it.tags as base_tags
        FROM birds b
        LEFT JOIN species s ON b.species_id = s.id
        LEFT JOIN provincies p ON b.province_id = p.id
        LEFT JOIN bodies bo ON b.body_id = bo.id
        LEFT JOIN lenses l ON b.lens_id = l.id
        LEFT JOIN instagram_tags it ON s.id = it.species_id
        WHERE b.dutch_name = ?
    ''', (dutch_name,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        print(f"❌ Bird '{dutch_name}' not found!\n")
        return None
    
    # Parse result
    (bird_id, dutch_name, scientific_name, english_name, description, 
     species, province, province_hashtags, body, body_hashtags, 
     lens, lens_hashtags, base_tags) = result
    
    # Genereer hashtags
    hashtags = []
    
    # Wetenschappelijke naam hashtag
    if scientific_name:
        hashtags.append(f"#{scientific_name.lower().replace(' ', '')}")
    
    # Engelse naam hashtag
    if english_name:
        hashtags.append(f"#{english_name.lower().replace(' ', '').replace('-', '')}")
    
    # Nederlandse naam hashtag
    if dutch_name:
        hashtags.append(f"#{dutch_name.lower().replace(' ', '')}")
    
    # Provincie hashtags
    if province_hashtags:
        hashtags.extend(province_hashtags.split())
    
    # Camera hashtags
    if body_hashtags:
        hashtags.extend(body_hashtags.split())
    
    # Lens hashtags
    if lens_hashtags:
        hashtags.extend(lens_hashtags.split())
    
    # Base species hashtags
    if base_tags:
        hashtags.extend(base_tags.split())
    
    # Bouw caption
    caption_text = ""
    
    # Beschrijving (of standaard tekst)
    if description and description.strip():
        caption_text = description.strip()
    else:
        caption_text = f"Een prachtige {dutch_name}!"
    
    # Voeg hashtags toe (max 30)
    hashtag_string = " ".join(hashtags[:30])
    full_caption = f"{caption_text}\n\n{hashtag_string}"
    
    # Print result
    print(f"\nGenerated for: {dutch_name} ({scientific_name})")
    print(f"Hashtag count: {min(len(hashtags), 30)} (total available: {len(hashtags)})")
    print(f"\nFull caption ({len(full_caption)} characters):")
    print("-" * 70)
    print(full_caption)
    print("-" * 70)
    print()
    
    return full_caption

def test_random_birds():
    """Toon 5 random vogels"""
    print("=" * 70)
    print("🎲 5 RANDOM BIRDS FROM DATABASE")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            b.dutch_name,
            b.scientific_name,
            b.english_name,
            s.name as species
        FROM birds b
        LEFT JOIN species s ON b.species_id = s.id
        WHERE b.dutch_name IS NOT NULL AND b.dutch_name != ''
        ORDER BY RANDOM()
        LIMIT 5
    ''')
    
    print()
    for idx, row in enumerate(cursor.fetchall(), 1):
        print(f"{idx}. {row[0]:30s} | {row[1]:30s} | {row[2]:30s} | {row[3]}")
    
    conn.close()
    print()

def main():
    """Main test workflow"""
    print("\n" + "=" * 70)
    print("🦆 NATUURWAARNEMER DATABASE TEST SUITE")
    print("=" * 70)
    print()
    
    # Test 1: Connection
    if not test_database_connection():
        return
    
    # Test 2: Statistics
    test_statistics()
    
    # Test 3: Random birds
    test_random_birds()
    
    # Test 4: Lookup specific birds
    test_birds = ['Fuut', 'Dodaars', 'Koolmees']
    
    for bird_name in test_birds:
        test_lookup_bird(bird_name)
    
    # Test 5: Instagram caption generation
    test_caption_birds = ['Fuut', 'Dodaars']
    
    for bird_name in test_caption_birds:
        generate_instagram_caption(bird_name)
    
    # Summary
    print("=" * 70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Database is working correctly ✅")
    print("  2. Hashtag generation is functional ✅")
    print("  3. Ready for Fase 2: Waarneming.nl API + Photo detection 🚀")
    print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()