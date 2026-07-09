#!/usr/bin/env python3
"""
document_ingestor.py
PicoClaw Document Knowledge Ingestion Engine
Scans ~/storage/shared/Documents/, catalogs files, extracts knowledge,
classifies by domain, and writes to ~/.picoclaw/memory/documents/

Usage:
    python3 document_ingestor.py [--full] [--watch]
    picostart documents ingest
"""

import os
import sys
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# ─── Configuration ──────────────────────────────────────────────────────────
DOCUMENTS_ROOT = os.path.expanduser("~/storage/shared/Documents")
PICOCLAW_HOME = os.path.expanduser("~/.picoclaw")
MEMORY_DIR = os.path.join(PICOCLAW_HOME, "memory", "documents")
CATALOG_FILE = os.path.join(MEMORY_DIR, "document_catalog.json")
CHUNKS_DIR = os.path.join(MEMORY_DIR, "chunks")

# File types we care about
TEXT_EXTENSIONS = {
    '.md', '.txt', '.py', '.json', '.sh', '.js', '.html', '.css',
    '.yml', '.yaml', '.toml', '.cfg', '.ini', '.conf', '.csv'
}

BINARY_EXTENSIONS = {'.pdf', '.docx', '.jpg', '.jpeg', '.png', '.mp4', '.webm', '.zip', '.gz', '.tar'}

# Domain classifiers (regex patterns -> domain tags)
DOMAIN_PATTERNS = {
    'revenue': r'(?i)(revenue|income|profit|arbitrage|affiliate|freelance|fiverr|upwork|monetiz)',
    'mesh': r'(?i)(mesh|orchestrator|cluster|node|spoke|hub|quillyos|picoclaw)',
    'ai_agent': r'(?i)(agentic|agent|mcp|manus|claude|gpt|llm|ollama|autonomous)',
    'business': r'(?i)(deal|wholesale|contract|investor|pitch|startup|business|ops)',
    'system': r'(?i)(termux|deploy|install|setup|config|bootstrap|ssh|linux)',
    'quantum': r'(?i)(quantum|qubit|track3|rnd|research)',
    'telegram': r'(?i)(telegram|bot|router|command)',
    'n8n': r'(?i)(n8n|workflow|node-by-node|mcp setup)',
    'gws': r'(?i)(gws|google|gmail|drive|sheets|calendar|workspace)',
    'legal': r'(?i)(agreement|contract|legal|compliance|terms)',
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def ensure_dirs():
    os.makedirs(MEMORY_DIR, exist_ok=True)
    os.makedirs(CHUNKS_DIR, exist_ok=True)

def file_hash(path: str) -> str:
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
    except Exception:
        h.update(path.encode())
    return h.hexdigest()[:16]

def quick_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def classify_file(filename: str, content_preview: str) -> List[str]:
    """Classify a file into domain tags based on name and content."""
    tags = set()
    text = f"{filename} {content_preview[:2000]}"
    for domain, pattern in DOMAIN_PATTERNS.items():
        if re.search(pattern, text):
            tags.add(domain)
    if not tags:
        tags.add('general')
    return sorted(list(tags))

def extract_title(content: str, filename: str) -> str:
    """Extract a human-readable title from file content or name."""
    # Try first markdown H1
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()[:100]
    # Try first line if it looks like a title
    lines = content.strip().split('\n')[:5]
    for line in lines:
        line = line.strip()
        if line and len(line) > 10 and len(line) < 120 and not line.startswith('import') and not line.startswith('<'):
            return line
    # Fallback to filename
    return Path(filename).stem.replace('_', ' ').replace('-', ' ').title()

def extract_one_liner(content: str, max_len: int = 160) -> str:
    """Extract a one-sentence summary."""
    # Remove code blocks and markdown for summary
    text = re.sub(r'```.*?```', ' ', content, flags=re.DOTALL)
    text = re.sub(r'`[^`]+`', ' ', text)
    text = re.sub(r'[#*\-|]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for s in sentences:
        s = s.strip()
        if 20 <= len(s) <= max_len:
            return s
    return text[:max_len] + "..." if len(text) > max_len else text

def read_text_file(path: str) -> Optional[str]:
    """Read a text file with encoding fallback."""
    encodings = ['utf-8', 'latin-1', 'cp1252']
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, PermissionError):
            continue
    return None

def is_text_file(path: str) -> bool:
    ext = Path(path).suffix.lower()
    if ext in TEXT_EXTENSIONS:
        return True
    if ext in BINARY_EXTENSIONS:
        return False
    # Try reading first 4KB
    try:
        with open(path, 'rb') as f:
            chunk = f.read(4096)
            if b'\x00' in chunk:
                return False
            # If >30% non-printable, treat as binary
            non_print = sum(1 for b in chunk if b < 32 and b not in (9, 10, 13))
            return (non_print / len(chunk)) < 0.3 if chunk else True
    except Exception:
        return False

# ─── Core Ingestion ───────────────────────────────────────────────────────────

def scan_documents() -> List[Dict[str, Any]]:
    """Scan Documents folder and return file metadata list."""
    files = []
    if not os.path.isdir(DOCUMENTS_ROOT):
        print(f"[ERROR] Documents path not found: {DOCUMENTS_ROOT}")
        print("[HINT] Run: termux-setup-storage")
        return files

    for root, dirs, filenames in os.walk(DOCUMENTS_ROOT):
        # Skip hidden dirs and common junk
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'node_modules', '.git')]
        for fname in filenames:
            if fname.startswith('.'):
                continue
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, DOCUMENTS_ROOT)
            try:
                stat = os.stat(fpath)
                files.append({
                    'path': fpath,
                    'rel_path': rel_path,
                    'filename': fname,
                    'size': stat.st_size,
                    'mtime': stat.st_mtime,
                    'is_text': is_text_file(fpath),
                })
            except (OSError, PermissionError):
                continue
    return files

def ingest_file(file_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Ingest a single file into knowledge chunks."""
    fpath = file_info['path']
    fname = file_info['filename']
    ext = Path(fname).suffix.lower()

    record = {
        'id': file_hash(fpath),
        'filename': fname,
        'rel_path': file_info['rel_path'],
        'absolute_path': fpath,
        'size': file_info['size'],
        'mtime': file_info['mtime'],
        'mtime_iso': datetime.fromtimestamp(file_info['mtime'], tz=timezone.utc).isoformat(),
        'extension': ext,
        'is_text': file_info['is_text'],
        'ingested_at': datetime.now(timezone.utc).isoformat(),
    }

    if file_info['is_text']:
        content = read_text_file(fpath)
        if content is None:
            record['status'] = 'read_error'
            return record

        record['content_hash'] = quick_hash(content)
        record['content_length'] = len(content)
        record['title'] = extract_title(content, fname)
        record['one_liner'] = extract_one_liner(content)
        record['tags'] = classify_file(fname, content)

        # Chunk large files
        if len(content) > 8000:
            record['chunks'] = chunk_content(content, record['id'])
        else:
            record['chunks'] = [{
                'chunk_id': f"{record['id']}_0",
                'start': 0,
                'end': len(content),
                'text': content,
                'hash': record['content_hash']
            }]

        # Extract actionable items (TODOs, commands, code blocks)
        record['actionables'] = extract_actionables(content)
        record['code_blocks'] = extract_code_blocks(content)
        record['status'] = 'ingested'
    else:
        record['status'] = 'binary_skipped'
        record['tags'] = ['binary']

    return record

def chunk_content(content: str, file_id: str, chunk_size: int = 4000, overlap: int = 200) -> List[Dict]:
    """Split content into overlapping chunks."""
    chunks = []
    start = 0
    idx = 0
    while start < len(content):
        end = min(start + chunk_size, len(content))
        # Try to break at newline
        if end < len(content):
            nl = content.rfind('\n', start, end)
            if nl != -1 and nl > start + chunk_size // 2:
                end = nl + 1
        chunk_text = content[start:end]
        chunks.append({
            'chunk_id': f"{file_id}_{idx}",
            'start': start,
            'end': end,
            'text': chunk_text,
            'hash': quick_hash(chunk_text)
        })
        start = end - overlap
        idx += 1
    return chunks

def extract_actionables(content: str) -> List[Dict]:
    """Extract TODOs, action items, and commands from content."""
    actionables = []
    # Markdown TODOs
    for m in re.finditer(r'(?i)^[\s]*[-*]\s*\[([ xX])\]\s*(.+)$', content, re.MULTILINE):
        actionables.append({
            'type': 'todo',
            'checked': m.group(1).lower() == 'x',
            'text': m.group(2).strip(),
        })
    # Bash commands (lines starting with $ or bash)
    for m in re.finditer(r'(?im)^(?:\$|bash|python3|pip|npm|node)\s+(.+)$', content):
        cmd = m.group(1).strip()
        if len(cmd) > 5:
            actionables.append({
                'type': 'command',
                'text': cmd,
            })
    return actionables

def extract_code_blocks(content: str) -> List[Dict]:
    """Extract fenced code blocks with language detection."""
    blocks = []
    for m in re.finditer(r'```(?:(\w+))?\n(.*?)```', content, re.DOTALL):
        lang = m.group(1) or 'text'
        code = m.group(2).strip()
        if len(code) > 20:
            blocks.append({
                'language': lang,
                'length': len(code),
                'hash': quick_hash(code),
                'preview': code[:200] + '...' if len(code) > 200 else code
            })
    return blocks

# ─── Catalog Management ───────────────────────────────────────────────────────

def load_catalog() -> Dict[str, Any]:
    if os.path.exists(CATALOG_FILE):
        try:
            with open(CATALOG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {'version': '1.0', 'files': {}, 'last_scan': None, 'stats': {}}

def save_catalog(catalog: Dict[str, Any]):
    with open(CATALOG_FILE, 'w') as f:
        json.dump(catalog, f, indent=2)

def write_chunk_file(file_id: str, chunks: List[Dict]):
    chunk_path = os.path.join(CHUNKS_DIR, f"{file_id}.json")
    with open(chunk_path, 'w') as f:
        json.dump({'file_id': file_id, 'chunks': chunks}, f, indent=2)

# ─── Main ─────────────────────────────────────────────────────────────────────

def run_ingestion(full_rescan: bool = False, watch_mode: bool = False):
    ensure_dirs()
    catalog = load_catalog()
    print(f"[INGESTOR] Scanning: {DOCUMENTS_ROOT}")
    files = scan_documents()
    print(f"[INGESTOR] Found {len(files)} files")

    new_count = 0
    updated_count = 0
    skipped_count = 0

    for finfo in files:
        fid = file_hash(finfo['path'])
        existing = catalog['files'].get(fid)

        if not full_rescan and existing:
            # Check if modified
            if existing.get('mtime') == finfo['mtime'] and existing.get('size') == finfo['size']:
                skipped_count += 1
                continue

        record = ingest_file(finfo)
        if record is None:
            continue

        catalog['files'][fid] = record
        if record.get('chunks'):
            write_chunk_file(fid, record['chunks'])

        if existing:
            updated_count += 1
            print(f"  [UPDATED] {record['rel_path']} ({record.get('status')})")
        else:
            new_count += 1
            print(f"  [NEW] {record['rel_path']} tags={record.get('tags', [])}")

    catalog['last_scan'] = datetime.now(timezone.utc).isoformat()
    catalog['stats'] = {
        'total_files': len(catalog['files']),
        'text_files': sum(1 for f in catalog['files'].values() if f.get('is_text')),
        'binary_files': sum(1 for f in catalog['files'].values() if not f.get('is_text')),
        'domains': {}
    }
    # Count domain tags
    for f in catalog['files'].values():
        for tag in f.get('tags', []):
            catalog['stats']['domains'][tag] = catalog['stats']['domains'].get(tag, 0) + 1

    save_catalog(catalog)
    print(f"\n[INGESTOR] Done: {new_count} new, {updated_count} updated, {skipped_count} unchanged")
    print(f"[INGESTOR] Catalog: {CATALOG_FILE}")
    print(f"[INGESTOR] Domains: {catalog['stats']['domains']}")

    if watch_mode:
        print("[INGESTOR] Watch mode active (polling every 60s, Ctrl+C to stop)")
        import time
        try:
            while True:
                time.sleep(60)
                run_ingestion(full_rescan=False, watch_mode=False)
        except KeyboardInterrupt:
            print("\n[INGESTOR] Watch stopped.")

if __name__ == '__main__':
    full = '--full' in sys.argv
    watch = '--watch' in sys.argv
    run_ingestion(full_rescan=full, watch_mode=watch)
