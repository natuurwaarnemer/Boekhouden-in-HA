#!/usr/bin/env python3
"""
Verwerk ALLE foto's in /incoming/ en groepeer ze voor Instagram posts
"""

import os
import json
from collections import defaultdict
from photo_processor import parse_filename, lookup_bird, process_photo

INCOMING_PATH = '/config/instagram/incoming/'
OUTPUT_JSON = '/config/instagram/temp/instagram_queue.json'

def group_photos(photo_files):
    """Groepeer foto's voor carousels (zelfde vogel + datum)"""
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

# Main
print("=" * 70)
print("📸 BATCH PHOTO PROCESSOR - OPACITY 1.0")
print("=" * 70)

photos = sorted([f for f in os.listdir(INCOMING_PATH) if f.lower().endswith('.jpg')])
print(f"\nFound {len(photos)} photos in /incoming/\n")

# Groepeer foto's
groups = group_photos(photos)
print(f"Grouped into {len(groups)} Instagram posts\n")

instagram_queue = []
total_processed = 0
total_failed = 0

for idx, group in enumerate(groups, 1):
    post_type = "📸 CAROUSEL" if group['photo_count'] > 1 else "📷 SINGLE"
    print(f"Post {idx}/{len(groups)}: {post_type} ({group['photo_count']} photo(s))")
    
    processed_photos = []
    bird_data = None
    
    for photo in group['photos']:
        print(f"  Processing: {photo}...", end=" ")
        
        result = process_photo(photo)
        
        if result:
            processed_photos.append({
                'original': photo,
                'processed': result['processed_filename'],
                'processed_path': result['processed_path']
            })
            
            # Bewaar bird data (voor caption, zelfde voor alle foto's in group)
            if not bird_data:
                bird_data = result['bird']
                caption = result['caption']
            
            total_processed += 1
            print("✅")
        else:
            total_failed += 1
            print("❌")
    
    # Voeg toe aan queue
    if processed_photos and bird_data:
        instagram_queue.append({
            'post_number': idx,
            'post_type': 'carousel' if group['photo_count'] > 1 else 'single',
            'date': group['date'],
            'bird_id': bird_data['id'],
            'bird_dutch_name': bird_data['dutch_name'],
            'bird_scientific_name': bird_data['scientific_name'],
            'bird_english_name': bird_data.get('english_name', ''),
            'photo_count': len(processed_photos),
            'photos': processed_photos,
            'caption': caption,
            'status': 'ready'
        })
    
    print()

# Sla queue op als JSON
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(instagram_queue, f, indent=2, ensure_ascii=False)

print(f"{'='*70}")
print("✅ BATCH PROCESSING COMPLETE")
print(f"{'='*70}")
print(f"\n📊 Statistics:")
print(f"  Total photos processed: {total_processed}")
print(f"  Total photos failed:    {total_failed}")
print(f"  Total posts ready:      {len(instagram_queue)}")
print(f"\n💾 Queue saved to: {OUTPUT_JSON}")

# Toon samenvatting
print(f"\n{'='*70}")
print("📋 POSTING QUEUE SUMMARY")
print(f"{'='*70}\n")

for post in instagram_queue:
    icon = "📸" if post['post_type'] == 'carousel' else "📷"
    print(f"{icon} Post {post['post_number']}: {post['bird_dutch_name']}")
    print(f"   Type: {post['post_type'].upper()}")
    print(f"   Photos: {post['photo_count']}")
    print(f"   Date: {post['date'][:4]}-{post['date'][4:6]}-{post['date'][6:8]}")
    print()

print(f"{'='*70}")
print("🚀 Ready for Instagram posting!")
print(f"{'='*70}")