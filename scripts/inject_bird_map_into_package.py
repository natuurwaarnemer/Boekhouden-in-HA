#!/usr/bin/env python3
"""
Inject updated bird file_map into /config/packages/birdnetphoto.yaml.

Priority for replacement:
1) Replace content between {% set file_map_block = '''  ...  ''' %} (preferred)
2) Else replace first ### BEGIN_BIRDNET_FILE_MAP ... ### END_BIRDNET_FILE_MAP block
3) Else replace inline {% set file_map = { ... } %} by creating the triple-quoted block

Behaviour:
- Builds mapping from /config/www/birds (adds ?v=<mtime>).
- Makes a timestamped backup of the package file before editing.
- Keeps only a single source block (deduplicates multiple occurrences).
"""
import json
import re
import shutil
from pathlib import Path
from datetime import datetime

CONFIG = Path('/config')
BIRDS_DIR = CONFIG / 'www' / 'birds'
PACKAGE = CONFIG / 'packages' / 'birdnetphoto.yaml'
BACKUP = PACKAGE.with_name(f"{PACKAGE.name}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")

BEGIN = '### BEGIN_BIRDNET_FILE_MAP'
END = '### END_BIRDNET_FILE_MAP'

def build_map():
    m = {}
    if not BIRDS_DIR.exists():
        return m
    for p in sorted(BIRDS_DIR.iterdir()):
        if not p.is_file():
            continue
        name = p.name
        try:
            mtime = int(p.stat().st_mtime)
        except Exception:
            mtime = int(datetime.now().timestamp())
        if '?' in name:
            base, _ = name.split('?', 1)
            newname = f"{base}?v={mtime}"
        else:
            newname = f"{name}?v={mtime}"
        key = Path(name.split('?',1)[0]).stem.lower().replace(' ', '_').replace('-', '_')
        m[key] = newname
    return m

def replace_file_map_block(text, jsonstr):
    """
    Preferred: replace content between:
      {% set file_map_block = '''
      ...content...
      ''' %}
    """
    pattern = re.compile(
        r"(\{\%\s*set\s+file_map_block\s*=\s*'''[\r\n]*)"  # opening
        r"(.*?)"                                           # content (group 2)
        r"([\r\n]*'''[\s]*\%\})",                           # closing
        flags=re.DOTALL
    )
    if pattern.search(text):
        text = pattern.sub(r"\1" + jsonstr + r"\3", text, count=1)
        return text, True
    return text, False

def replace_begin_end_block(text, jsonstr):
    block_re = re.compile(rf"({re.escape(BEGIN)}\s*)(\{{.*?\}})(\s*{re.escape(END)})", flags=re.DOTALL)
    if block_re.search(text):
        text = block_re.sub(rf"\1{jsonstr}\3", text, count=1)
        return text, True
    return text, False

def replace_inline_file_map(text, jsonstr):
    """
    Replace inline {% set file_map = { ... } %} with the triple quoted block + parsing lines.
    """
    inline_re = re.compile(r"{%\s*set\s+file_map\s*=\s*\{.*?\}\s*%}", flags=re.DOTALL)
    if inline_re.search(text):
        replacement = (
            "{% set file_map_block = '''\n"
            f"{BEGIN}\n{jsonstr}\n{END}\n"
            "''' %}\n"
            "{% set file_map = file_map_block | regex_replace('(?s).*### BEGIN_BIRDNET_FILE_MAP\\\\n(.*)\\\\n### END_BIRDNET_FILE_MAP.*','\\\\1') | from_json %}"
        )
        text = inline_re.sub(replacement, text, count=1)
        return text, True
    return text, False

def deduplicate_file_map_block(text):
    """
    Keep only the first {% set file_map_block = ''' ... ''' %} occurrence (if any).
    If not present, keep only the first BEGIN/END block (if present).
    """
    # Deduplicate triple-quoted file_map_block occurrences
    triple_pattern = re.compile(r"(\{\%\s*set\s+file_map_block\s*=\s*'''[\r\n]*).*?([\r\n]*'''[\s]*\%\})", flags=re.DOTALL)
    matches = list(triple_pattern.finditer(text))
    if len(matches) > 1:
        first = matches[0]
        before = text[:first.start()]
        first_block = text[first.start():first.end()]
        after = text[first.end():]
        # remove other occurrences in the after text
        after_clean = triple_pattern.sub("", after)
        text = before + first_block + after_clean
        return text

    # If no triple block, dedupe BEGIN/END blocks
    be_pattern = re.compile(rf"{re.escape(BEGIN)}.*?{re.escape(END)}", flags=re.DOTALL)
    be_matches = list(be_pattern.finditer(text))
    if len(be_matches) > 1:
        first = be_matches[0]
        before = text[:first.start()]
        first_block = text[first.start():first.end()]
        after = text[first.end():]
        after_clean = be_pattern.sub("", after)
        text = before + first_block + after_clean
    return text

def main():
    mapping = build_map()
    if not mapping:
        print(f"No images found in {BIRDS_DIR}; aborting.")
        return
    jsonstr = json.dumps(mapping, ensure_ascii=False, separators=(',', ':'))

    if not PACKAGE.exists():
        raise FileNotFoundError(f"Package not found: {PACKAGE}")
    shutil.copy2(PACKAGE, BACKUP)
    text = PACKAGE.read_text(encoding='utf-8')

    # 1) Preferred: replace inside the {% set file_map_block = ''' ... ''' %} block
    text, replaced = replace_file_map_block(text, jsonstr)
    if replaced:
        text = deduplicate_file_map_block(text)
        PACKAGE.write_text(text, encoding='utf-8')
        print(f"Replaced file_map inside triple-quoted file_map_block in {PACKAGE} (backup: {BACKUP})")
        return

    # 2) Fallback: replace BEGIN/END block
    text, replaced = replace_begin_end_block(text, jsonstr)
    if replaced:
        text = deduplicate_file_map_block(text)
        PACKAGE.write_text(text, encoding='utf-8')
        print(f"Replaced BEGIN/END block in {PACKAGE} (backup: {BACKUP})")
        return

    # 3) Fallback: replace inline file_map dict by creating the triple-quoted block
    text, replaced = replace_inline_file_map(text, jsonstr)
    if replaced:
        text = deduplicate_file_map_block(text)
        PACKAGE.write_text(text, encoding='utf-8')
        print(f"Replaced inline file_map and created triple-quoted block in {PACKAGE} (backup: {BACKUP})")
        return

    # 4) If nothing matched, append a triple-quoted block at the end
    insert = "\n{% set file_map_block = '''\n" + BEGIN + "\n" + jsonstr + "\n" + END + "\n''' %}\n{% set file_map = file_map_block | regex_replace('(?s).*### BEGIN_BIRDNET_FILE_MAP\\\\n(.*)\\\\n### END_BIRDNET_FILE_MAP.*','\\\\1') | from_json %}\n"
    text = text + insert
    PACKAGE.write_text(text, encoding='utf-8')
    print(f"No existing block found — appended triple-quoted file_map_block to {PACKAGE} (backup: {BACKUP})")

if __name__ == "__main__":
    main()