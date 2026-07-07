#!/usr/bin/env python3
"""
Document Ingestor v2.1 — Termux-Optimized
Paces ingestion to avoid crashing mobile devices.
Batches, size limits, incremental saves, memory-conscious chunking.
"""

import os
import sys
import json
import hashlib
import time
import re
from datetime import datetime
from pathlib import Path

# ─── CONFIG ─── Tune these for your device ───
BATCH_SIZE = 8           # Files per batch (lower = less memory)
BATCH_PAUSE = 2.0          # Seconds between batches (lets CPU cool)
MAX_FILE_SIZE_MB = 5       # Skip files larger than this
CHUNK_SIZE = 800           # Characters per chunk (smaller = less memory)
CHUNK_OVERLAP = 100        # Overlap between chunks
MAX_CHUNKS_PER_FILE = 50   # Cap chunks per file
HASH_PREFIX_LEN = 8        # Shorter hashes = less compute

# ─── PATHS ───
HOME = os.path.expanduser("~")
WORKSPACE = os.path.join(HOME, ".picoclaw", "workspace")
MEMORY = os.path.join(HOME, ".picoclaw", "memory", "documents")
CHUNKS_DIR = os.path.join(MEMORY, "chunks")
CATALOG_PATH = os.path.join(MEMORY, "document_catalog.json")
DOCS_PATH = os.path.join(WORKSPACE, "Documents")

# Supported extensions
EXTS = {".txt", ".md", ".py", ".json", ".csv", ".log", ".sh", ".yaml", ".yml", ".html", ".xml", ".rst"}


def ensure_dirs():
    os.makedirs(MEMORY, exist_ok=True)
    os.makedirs(CHUNKS_DIR, exist_ok=True)


def quick_hash(text):
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:HASH_PREFIX_LEN]


def classify_file(path, content):
    name = os.path.basename(path).lower()
    if "revenue" in name or "revenue" in content[:2000].lower():
        return "revenue"
    if "skill" in name or "skill" in content[:2000].lower():
        return "skill"
    if "config" in name or "config" in content[:2000].lower():
        return "config"
    if ".py" in name:
        return "python"
    if ".md" in name:
        return "markdown"
    if ".json" in name:
        return "json"
    return "document"


def read_file_safe(path):
    try:
        size = os.path.getsize(path)
        if size > MAX_FILE_SIZE_MB * 1024 * 1024:
            return None, f"skipped (> {MAX_FILE_SIZE_MB}MB)"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(), None
    except Exception as e:
        return None, str(e)


def chunk_content(text, doc_id):
    chunks = []
    start = 0
    count = 0
    while start < len(text) and count < MAX_CHUNKS_PER_FILE:
        end = start + CHUNK_SIZE
        chunk_text = text[start:end]
        if not chunk_text.strip():
            start = end
            continue
        chunk_id = f"{doc_id}_c{count}"
        chunks.append({
            "id": chunk_id,
            "text": chunk_text,
            "hash": quick_hash(chunk_text),
            "start": start,
            "end": end
        })
        start = end - CHUNK_OVERLAP
        count += 1
    return chunks


def save_chunk_file(doc_id, chunks):
    path = os.path.join(CHUNKS_DIR, f"{doc_id}_chunks.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)


def load_catalog():
    if os.path.exists(CATALOG_PATH):
        try:
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"version": "2.1", "created": datetime.now().isoformat(), "documents": []}


def save_catalog(catalog):
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)


def scan_files():
    files = []
    if not os.path.exists(DOCS_PATH):
        print(f"[INGESTOR] Documents path not found: {DOCS_PATH}")
        return files
    for root, _, fnames in os.walk(DOCS_PATH):
        for fname in fnames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in EXTS:
                fpath = os.path.join(root, fname)
                files.append(fpath)
    return files


def ingest_file(fpath, existing_ids):
    rel = os.path.relpath(fpath, DOCS_PATH)
    doc_id = quick_hash(rel) + "_" + quick_hash(str(os.path.getmtime(fpath)))
    if doc_id in existing_ids:
        return None, "already_ingested"

    content, err = read_file_safe(fpath)
    if content is None:
        return None, err

    doc_type = classify_file(fpath, content)
    chunks = chunk_content(content, doc_id)
    save_chunk_file(doc_id, chunks)

    return {
        "id": doc_id,
        "path": rel,
        "type": doc_type,
        "size": len(content),
        "chunks": len(chunks),
        "mtime": os.path.getmtime(fpath),
        "ingested_at": datetime.now().isoformat()
    }, None


def run_ingestion():
    ensure_dirs()
    catalog = load_catalog()
    existing_ids = {d["id"] for d in catalog.get("documents", [])}

    files = scan_files()
    print(f"[INGESTOR] Found {len(files)} candidate files")
    print(f"[INGESTOR] Already ingested: {len(existing_ids)}")
    print(f"[INGESTOR] Batch size: {BATCH_SIZE}, pause: {BATCH_PAUSE}s, max size: {MAX_FILE_SIZE_MB}MB")
    print(f"[INGESTOR] Starting... (Ctrl+C to pause, re-run to resume)")
    print("-" * 50)

    new_count = 0
    skip_count = 0
    err_count = 0
    batch = []

    for i, fpath in enumerate(files, 1):
        doc, err = ingest_file(fpath, existing_ids)
        if doc:
            catalog["documents"].append(doc)
            existing_ids.add(doc["id"])
            new_count += 1
            batch.append(f"  ✓ {os.path.basename(fpath)} ({doc['type']}, {doc['chunks']} chunks)")
        elif err == "already_ingested":
            skip_count += 1
        else:
            err_count += 1
            batch.append(f"  ✗ {os.path.basename(fpath)}: {err}")

        # Save every file (incremental)
        if i % 3 == 0:
            save_catalog(catalog)

        # Print batch progress
        if i % BATCH_SIZE == 0 or i == len(files):
            for line in batch:
                print(line)
            batch = []
            print(f"[INGESTOR] Progress: {i}/{len(files)} | new:{new_count} skip:{skip_count} err:{err_count}")
            if i < len(files):
                print(f"[INGESTOR] Pausing {BATCH_PAUSE}s for CPU...")
                time.sleep(BATCH_PAUSE)
            save_catalog(catalog)

    print("-" * 50)
    print(f"[INGESTOR] Done. Total: {len(files)} | New: {new_count} | Skipped: {skip_count} | Errors: {err_count}")
    print(f"[INGESTOR] Catalog: {CATALOG_PATH}")
    print(f"[INGESTOR] Chunks: {CHUNKS_DIR}")


if __name__ == "__main__":
    try:
        run_ingestion()
    except KeyboardInterrupt:
        print("\n[INGESTOR] Interrupted. Progress saved. Re-run to resume.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[INGESTOR] Fatal error: {e}")
        sys.exit(1)
