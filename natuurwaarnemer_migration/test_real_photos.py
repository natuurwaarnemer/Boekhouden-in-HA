#!/usr/bin/env python3
"""
Test met echte foto's uit /incoming/
"""

import os
import sqlite3
import re
from collections import defaultdict

DB_PATH = '/config/databases/natuurwaarnemer.db'
INCOMING_PATH = '/config/instagram/incoming/'

def parse_filename(filename):
    """Parse: genus_species_YYYYMMDD_NN.jpg"""
    name_without_ext = filename.replace('.jpg', '').replace('.JPG', '').lower()
    parts = name_without_ext.split('_')
    
    if len(parts) < 3:
        return {'valid': False}
    
    number_part = parts[-1]
    date_part = parts[-2]
    
    if len(date_part) == 8 and date_part.isdigit() and number_part.isdigit():
        scientific_parts = parts[:-2]
        scientific_name_clean = ''.join(scientific_parts).lower()
        
        return {
            'scientific_name': scientific_name_clean,
            'year': int(date_part[0:4]),
            'month': int(date_part[4:6]),
            'day': int(date_part[6:8]),
            'number': int(number_part),
            'date': date_part,
            'valid': True
        }
    
    return {'valid': False}

def lookup_bird(scientific_name):
    """Zoek vogel in database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT b.id, b.scientific_name, b.dutch_name, b.english_name
        FROM birds b
        WHERE LOWER(REPLACE(b.scientific_name, ' ', '')) = LOWER(?)
        LIMIT 1
    ''', (scientific_name,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'found': True,
            'id': result[0],
            'scientific_name': result[1],
            'dutch_name': result[2],
            'english_name': result[3]
        }
    return {'found': False}

def group_photos(photo_files):
    """Groepeer foto's voor carousels"""
    groups = defaultdict(list)
    
    for filename in sorted(photo_files):
        parsed = parse_filename(filename)
        
        if not parsed['valid']:
            continue
        
        group_key = f"{parsed['scientific_name']}_{parsed['date']}"
        groups[group_key].append({'filename': filename, 'number': parsed['number'], 'parsed': parsed})
    
    result = []
    for group_key, photos in groups.items():
        sorted_photos = sorted(photos, key=lambda x: x['number'])
        result.append({
            'group_key': group_key,
            'scientific_name': sorted_photos[0]['parsed']['scientific_name'],
            'date': sorted_photos[0]['parsed']['date'],
            'photos': [p['filename'] for p in sorted_photos],
            'photo_count': len(sorted_photos)
        })
    
    result.sort(key=lambda x: x['date'])
    return result

# Main test
print("=" * 70)
print("🧪 TEST: ECHTE FOTO'S UIT /incoming/")
print("=" * 70)

photos = sorted([f for f in os.listdir(INCOMING_PATH) if f.lower().endswith('.jpg')])
print(f"\n📸 Found {len(photos)} photos\n")

# Test parsing
print("PARSING TEST:")
print("-" * 70)
for photo in photos:
    parsed = parse_filename(photo)
    if parsed['valid']:
        print(f"✅ {photo}")
        print(f"   → {parsed['scientific_name']} | {parsed['date']} | #{parsed['number']}")
    else:
        print(f"❌ {photo} (INVALID FORMAT)")

# Test grouping
print(f"\n{'=' * 70}")
print("CAROUSEL GROUPING:")
print("-" * 70)

groups = group_photos(photos)
print(f"\nTotal posts: {len(groups)}\n")

for idx, group in enumerate(groups, 1):
    bird = lookup_bird(group['scientific_name'])
    
    if group['photo_count'] > 1:
        post_type = "📸 CAROUSEL"
    else:
        post_type = "📷 SINGLE"
    
    print(f"Post {idx}: {post_type}")
    print(f"  Date: {group['date'][:4]}-{group['date'][4:6]}-{group['date'][6:8]}")
    if bird['found']:
        print(f"  Bird: {bird['dutch_name']} ({bird['scientific_name']})")
    else:
        print(f"  Bird: ❌ NOT FOUND IN DATABASE ({group['scientific_name']})")
    print(f"  Photos: {group['photo_count']}")
    for photo in group['photos']:
        print(f"    - {photo}")
    print()

print("=" * 70)
print("✅ TEST COMPLETED")
print("=" * 70)