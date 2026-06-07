#!/usr/bin/env python3
"""
generate_bird_map.py
Scan /config/www/birds for image files and write a JSON map file_map_v1.json
Mapping keys are normalized species names (lowercase, spaces -> underscore, remove non-alnum/_).
Each value is the filename with ?v=<mtime> cache-buster.

Usage: python3 /config/scripts/generate_bird_map.py
"""

import os
import json
from pathlib import Path
import re
import sys

BIRDS_DIR = os.environ.get("BIRDS_DIR", "/config/www/birds")
OUT_FILE = os.environ.get("OUT_FILE", os.path.join(BIRDS_DIR, "file_map_v1.json"))
VALID_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

def normalize(name: str) -> str:
    s = name.strip().lower()
    # remove commas and extra whitespace
    s = s.replace(",", " ")
    s = re.sub(r"\s+", " ", s)
    s = s.replace(" ", "_").replace("-", "_")
    # remove characters not a-z0-9_
    s = re.sub(r"[^a-z0-9_]", "", s)
    # collapse underscores
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def main():
    p = Path(BIRDS_DIR)
    if not p.exists() or not p.is_dir():
        print(f"ERROR: birds dir does not exist: {BIRDS_DIR}", file=sys.stderr)
        sys.exit(2)

    mapping = {}
    for f in sorted(p.iterdir()):
        if not f.is_file():
            continue
        if f.suffix.lower() not in VALID_EXT:
            continue
        name_noext = f.stem
        key = normalize(name_noext)
        if not key:
            continue
        try:
            mtime = int(f.stat().st_mtime)
        except Exception:
            mtime = 0
        # use filename (not full path), append cache-buster
        mapping[key] = f.name + f"?v={mtime}"

    # always ensure a placeholder entry exists if placeholder.jpg is present
    placeholder = p / "placeholder.jpg"
    if placeholder.exists():
        try:
            pm = int(placeholder.stat().st_mtime)
        except Exception:
            pm = 0
        mapping.setdefault("placeholder", f"placeholder.jpg?v={pm}")

    # write JSON file atomically
    tmp = OUT_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(mapping, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, OUT_FILE)
    print(f"Wrote {OUT_FILE} ({len(mapping)} entries)")

if __name__ == "__main__":
    main()