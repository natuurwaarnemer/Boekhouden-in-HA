#!/usr/bin/env python3
"""
Instagram Photo Processor
- Resize foto's naar Instagram formaat
- Voeg watermark toe
- Genereer caption met hashtags
"""

import os
import sqlite3
from PIL import Image, ImageDraw, ImageFont
from collections import defaultdict
import json

# Configuratie
DB_PATH = '/config/databases/natuurwaarnemer.db'
INCOMING_PATH = '/config/instagram/incoming/'
TEMP_PATH = '/config/instagram/temp/'
WATERMARK_PATH = '/config/instagram/watermark/watermark.png'

# Instagram optimale formaten
INSTAGRAM_MAX_WIDTH = 1080
INSTAGRAM_MAX_HEIGHT = 1350
JPEG_QUALITY = 95

# Watermark instellingen
WATERMARK_OPACITY = 1.0              # Volledig dekkend
WATERMARK_POSITION = 'bottom-right'  # Positie
WATERMARK_MARGIN = 20                # Pixels vanaf rand
WATERMARK_MAX_WIDTH_PERCENT = 0.25   # 25% van foto breedte

def parse_filename(filename):
    """Parse bestandsnaam: genus_species_YYYYMMDD_NN.jpg"""
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
    """Zoek vogel in database met alle metadata"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            b.id,
            b.scientific_name,
            b.dutch_name,
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
            'english_name': result[3],
            'description': result[4],
            'species': result[5],
            'province': result[6],
            'province_hashtags': result[7],
            'body': result[8],
            'body_hashtags': result[9],
            'lens': result[10],
            'lens_hashtags': result[11],
            'base_tags': result[12]
        }
    
    return {'found': False}

def resize_for_instagram(image):
    """
    Resize foto naar Instagram optimaal formaat
    - Max 1080px breed
    - Behoud aspect ratio
    """
    width, height = image.size
    
    # Bereken nieuwe dimensies
    if width > height:
        # Landscape: max 1080px breed
        if width > INSTAGRAM_MAX_WIDTH:
            new_width = INSTAGRAM_MAX_WIDTH
            new_height = int((INSTAGRAM_MAX_WIDTH / width) * height)
        else:
            new_width = width
            new_height = height
    else:
        # Portrait: max 1080px breed, max 1350px hoog
        if width > INSTAGRAM_MAX_WIDTH:
            new_width = INSTAGRAM_MAX_WIDTH
            new_height = int((INSTAGRAM_MAX_WIDTH / width) * height)
        else:
            new_width = width
            new_height = height
        
        # Check max height
        if new_height > INSTAGRAM_MAX_HEIGHT:
            new_height = INSTAGRAM_MAX_HEIGHT
            new_width = int((INSTAGRAM_MAX_HEIGHT / height) * width)
    
    # Resize met high-quality resampling
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return resized

def add_watermark(image, watermark_path, position='bottom-right', margin=20, opacity=1.0):
    """
    Voeg watermark toe aan foto
    
    position: 'bottom-right', 'bottom-left', 'top-right', 'top-left'
    margin: pixels vanaf rand
    opacity: 0.0 - 1.0
    """
    if not os.path.exists(watermark_path):
        print(f"⚠️  Watermark not found: {watermark_path}")
        return image
    
    # Laad watermark
    watermark = Image.open(watermark_path).convert('RGBA')
    
    # Schaal watermark (max % van foto breedte)
    max_wm_width = int(image.width * WATERMARK_MAX_WIDTH_PERCENT)
    if watermark.width > max_wm_width:
        wm_ratio = max_wm_width / watermark.width
        new_wm_width = max_wm_width
        new_wm_height = int(watermark.height * wm_ratio)
        watermark = watermark.resize((new_wm_width, new_wm_height), Image.Resampling.LANCZOS)
    
    # Pas opacity toe
    if opacity < 1.0:
        alpha = watermark.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        watermark.putalpha(alpha)
    
    # Bereken positie
    if position == 'bottom-right':
        x = image.width - watermark.width - margin
        y = image.height - watermark.height - margin
    elif position == 'bottom-left':
        x = margin
        y = image.height - watermark.height - margin
    elif position == 'top-right':
        x = image.width - watermark.width - margin
        y = margin
    elif position == 'top-left':
        x = margin
        y = margin
    else:
        x = image.width - watermark.width - margin
        y = image.height - watermark.height - margin
    
    # Converteer image naar RGBA voor transparantie
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Plak watermark
    image.paste(watermark, (x, y), watermark)
    
    # Converteer terug naar RGB voor JPEG
    if image.mode == 'RGBA':
        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
        rgb_image.paste(image, mask=image.split()[3])
        return rgb_image
    
    return image

def generate_caption(bird_data):
    """
    Genereer Instagram caption met beschrijving + hashtags
    """
    # Beschrijving
    if bird_data.get('description'):
        caption_text = bird_data['description'].strip()
    else:
        caption_text = f"Een prachtige {bird_data['dutch_name']}!"
    
    # Genereer hashtags
    hashtags = []
    
    # Wetenschappelijke naam
    if bird_data.get('scientific_name'):
        hashtags.append(f"#{bird_data['scientific_name'].lower().replace(' ', '')}")
    
    # Engelse naam
    if bird_data.get('english_name'):
        hashtags.append(f"#{bird_data['english_name'].lower().replace(' ', '').replace('-', '')}")
    
    # Nederlandse naam
    if bird_data.get('dutch_name'):
        hashtags.append(f"#{bird_data['dutch_name'].lower().replace(' ', '')}")
    
    # Provincie hashtags
    if bird_data.get('province_hashtags'):
        hashtags.extend(bird_data['province_hashtags'].split())
    
    # Camera hashtags
    if bird_data.get('body_hashtags'):
        hashtags.extend(bird_data['body_hashtags'].split())
    
    # Lens hashtags
    if bird_data.get('lens_hashtags'):
        hashtags.extend(bird_data['lens_hashtags'].split())
    
    # Base species hashtags
    if bird_data.get('base_tags'):
        hashtags.extend(bird_data['base_tags'].split())
    
    # Limiteer tot 30 hashtags (Instagram max)
    hashtag_string = " ".join(hashtags[:30])
    
    # Combineer
    full_caption = f"{caption_text}\n\n{hashtag_string}"
    
    return {
        'caption': full_caption,
        'hashtag_count': min(len(hashtags), 30),
        'char_count': len(full_caption)
    }

def process_photo(filename):
    """
    Process een enkele foto:
    1. Parse filename
    2. Lookup bird
    3. Resize
    4. Add watermark
    5. Generate caption
    6. Save to temp
    """
    # Parse filename
    parsed = parse_filename(filename)
    if not parsed['valid']:
        return None
    
    # Lookup bird
    bird = lookup_bird(parsed['scientific_name'])
    if not bird['found']:
        return None
    
    # Load image
    input_path = os.path.join(INCOMING_PATH, filename)
    image = Image.open(input_path)
    
    original_size = image.size
    
    # Resize
    image = resize_for_instagram(image)
    new_size = image.size
    
    # Add watermark
    if os.path.exists(WATERMARK_PATH):
        image = add_watermark(
            image, 
            WATERMARK_PATH,
            position=WATERMARK_POSITION,
            margin=WATERMARK_MARGIN,
            opacity=WATERMARK_OPACITY
        )
    
    # Generate caption
    caption_data = generate_caption(bird)
    
    # Save processed image
    output_filename = f"processed_{filename}"
    output_path = os.path.join(TEMP_PATH, output_filename)
    image.save(output_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)
    
    return {
        'filename': filename,
        'processed_filename': output_filename,
        'processed_path': output_path,
        'bird': bird,
        'caption': caption_data['caption'],
        'hashtag_count': caption_data['hashtag_count'],
        'original_size': original_size,
        'new_size': new_size
    }

# Test met 1 foto
if __name__ == '__main__':
    print("=" * 70)
    print("🧪 PHOTO PROCESSOR TEST")
    print("=" * 70)
    
    # Haal eerste foto
    photos = sorted([f for f in os.listdir(INCOMING_PATH) if f.lower().endswith('.jpg')])
    
    if not photos:
        print("❌ No photos found in /incoming/")
    else:
        print(f"\nFound {len(photos)} photos. Processing first one...\n")
        
        result = process_photo(photos[0])
        
        if result:
            print(f"\n{'='*70}")
            print("✅ PROCESSING COMPLETE")
            print(f"{'='*70}")
            print(f"Original: {result['original_size'][0]}x{result['original_size'][1]}px")
            print(f"Resized:  {result['new_size'][0]}x{result['new_size'][1]}px")
            print(f"Saved:    {result['processed_path']}")
            print(f"\nCaption preview (first 300 chars):")
            print(f"{'-'*70}")
            print(result['caption'][:300])
            if len(result['caption']) > 300:
                print("...")
            print(f"{'-'*70}")