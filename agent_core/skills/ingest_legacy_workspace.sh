#!/data/data/com.termux/files/usr/bin/bash
# PicoClaw Legacy Workspace Ingestion
# Discovers, catalogs, and chunks all existing PicoClaw/QuillyOS files
# Run this in Termux after termux-setup-storage

set -e

SOURCE_DIR="${1:-$HOME/storage/shared/Documents}"
MEMORY_DIR="$HOME/.picoclaw/memory"
WORKSPACE_KG="$MEMORY_DIR/workspace_knowledge_graph.json"

echo "🦅 PicoClaw Legacy Workspace Ingestion"
echo "======================================="
echo "Source: $SOURCE_DIR"
echo "Memory: $MEMORY_DIR"
echo ""

mkdir -p "$MEMORY_DIR"/{chunks,classified,index,logs,workspace_summaries}

# --- Phase 1: Discover and catalog all files ---
echo "🔍 Phase 1: Discovering files..."

python3 - "$SOURCE_DIR" "$MEMORY_DIR" <<'PYEOF'
import os, sys, json, hashlib
from pathlib import Path
from datetime import datetime

source_dir = Path(sys.argv[1])
memory_dir = Path(sys.argv[2])

# File categories based on naming patterns
CATEGORIES = {
    "briefings_and_strategy": ["brief", "strategy", "mission", "playbook", "architecture", "roadmap", "assessment", "guide"],
    "installation_and_setup": ["install", "setup", "config", "deploy", "start_", "diagnose"],
    "skills_and_code": ["skill", "agent", "bot", "router", "bridge", "optimizer", "engine", "manager", "controller", "tracker", "generator", "analyzer", "monitor", "protocol", "loop", "mesh"],
    "business_and_legal": ["deal", "arv", "calculator", "pitch", "agreement", "wholesale", "investor", "revenue"],
    "other": []
}

def categorize_file(filename):
    fname_lower = filename.lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw in fname_lower for kw in keywords):
            return cat
    return "other"

def get_file_metadata(fpath):
    stat = fpath.stat()
    return {
        "filename": fpath.name,
        "path": str(fpath),
        "size_bytes": stat.st_size,
        "size_kb": round(stat.st_size / 1024, 2),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "extension": fpath.suffix.lower(),
        "category": categorize_file(fpath.name),
        "content_hash": hashlib.sha256(fpath.read_bytes()).hexdigest()[:16] if stat.st_size < 1024*1024 else "large_file_skipped"
    }

# Discover all files
all_files = []
for fpath in sorted(source_dir.iterdir()):
    if fpath.is_file():
        meta = get_file_metadata(fpath)
        all_files.append(meta)

# Build knowledge graph
kg = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "source_directory": str(source_dir),
    "total_files": len(all_files),
    "total_size_kb": round(sum(f["size_bytes"] for f in all_files) / 1024, 2),
    "by_category": {},
    "by_extension": {},
    "files": all_files
}

for f in all_files:
    cat = f["category"]
    kg["by_category"][cat] = kg["by_category"].get(cat, 0) + 1
    ext = f["extension"] or "no_extension"
    kg["by_extension"][ext] = kg["by_extension"].get(ext, 0) + 1

# Save knowledge graph
kg_path = memory_dir / "workspace_knowledge_graph.json"
with open(kg_path, "w") as f:
    json.dump(kg, f, indent=2)

print(f"✅ Discovered {len(all_files)} files")
print(f"📊 By category: {kg['by_category']}")
print(f"📊 By extension: {kg['by_extension']}")
print(f"📦 Total size: {kg['total_size_kb']:.1f} KB")
print(f"📝 Saved: {kg_path}")
PYEOF

echo ""
echo "🔍 Phase 2: Generating one-liner summaries..."

python3 - "$SOURCE_DIR" "$MEMORY_DIR" <<'PYEOF'
import os, sys, json
from pathlib import Path
from datetime import datetime

source_dir = Path(sys.argv[1])
memory_dir = Path(sys.argv[2])

# Load knowledge graph
with open(memory_dir / "workspace_knowledge_graph.json") as f:
    kg = json.load(f)

one_liners = []
for f in kg["files"]:
    fname = f["filename"]
    cat = f["category"]
    ext = f["extension"]
    size = f["size_kb"]

    # Generate one-liner based on file type
    if ext == ".py":
        desc = f"Python skill/module — {cat.replace('_', ' ')}"
    elif ext == ".sh":
        desc = f"Bash script — {cat.replace('_', ' ')}"
    elif ext == ".md":
        desc = f"Documentation/briefing — {cat.replace('_', ' ')}"
    elif ext == ".txt":
        desc = f"Text config/guide — {cat.replace('_', ' ')}"
    elif ext == ".csv":
        desc = f"Data table/spreadsheet"
    elif ext == ".pdf":
        desc = f"PDF document"
    else:
        desc = f"File — {cat.replace('_', ' ')}"

    one_liners.append(f"[{cat}] {fname} ({size:.1f} KB) — {desc}")

# Save one-liners
ol_path = memory_dir / "workspace_one_liners.txt"
with open(ol_path, "w") as f:
    f.write("# PicoClaw Legacy Workspace — One-Liner Catalog\n")
    f.write(f"# Generated: {datetime.utcnow().isoformat()}Z\n")
    f.write(f"# Total files: {len(one_liners)}\n\n")
    for line in one_liners:
        f.write(line + "\n")

print(f"✅ Generated {len(one_liners)} one-liners")
print(f"📝 Saved: {ol_path}")
PYEOF

echo ""
echo "🔍 Phase 3: Creating actionable chunk index..."

python3 - "$SOURCE_DIR" "$MEMORY_DIR" <<'PYEOF'
import os, sys, json, hashlib
from pathlib import Path
from datetime import datetime

source_dir = Path(sys.argv[1])
memory_dir = Path(sys.argv[2])

with open(memory_dir / "workspace_knowledge_graph.json") as f:
    kg = json.load(f)

# Create actionable chunks for each file
chunks = []
for f in kg["files"]:
    fname = f["filename"]
    cat = f["category"]
    ext = f["extension"]

    # Determine actionability
    if cat == "skills_and_code" and ext == ".py":
        actionability = "ingest_as_skill"
        priority = "P0" if any(k in fname.lower() for k in ["agent_core", "mesh", "orchestrator", "memory"]) else "P1"
    elif cat == "briefings_and_strategy" and ext == ".md":
        actionability = "extract_knowledge"
        priority = "P1"
    elif cat == "installation_and_setup":
        actionability = "reference_for_deployment"
        priority = "P2"
    elif cat == "business_and_legal":
        actionability = "revenue_intelligence"
        priority = "P1"
    else:
        actionability = "archive"
        priority = "P2"

    chunk = {
        "chunk_id": f"LEGACY-{hashlib.sha256(fname.encode()).hexdigest()[:8].upper()}",
        "type": "legacy_file",
        "filename": fname,
        "category": cat,
        "extension": ext,
        "size_kb": f["size_kb"],
        "path": f["path"],
        "priority": priority,
        "actionability": actionability,
        "content_hash": f["content_hash"],
        "ingested_at": datetime.utcnow().isoformat() + "Z"
    }
    chunks.append(chunk)

# Save chunks
chunks_path = memory_dir / "legacy_chunks.json"
with open(chunks_path, "w") as f:
    json.dump({
        "meta": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_chunks": len(chunks),
            "source": "legacy_workspace_ingestion"
        },
        "chunks": chunks
    }, f, indent=2)

# Summary stats
by_action = {}
by_priority = {}
for c in chunks:
    by_action[c["actionability"]] = by_action.get(c["actionability"], 0) + 1
    by_priority[c["priority"]] = by_priority.get(c["priority"], 0) + 1

print(f"✅ Created {len(chunks)} legacy chunks")
print(f"📊 By actionability: {by_action}")
print(f"📊 By priority: {by_priority}")
print(f"📝 Saved: {chunks_path}")
PYEOF

echo ""
echo "======================================="
echo "✅ Legacy workspace ingestion complete!"
echo "======================================="
echo ""
echo "📁 Files cataloged: $MEMORY_DIR/workspace_knowledge_graph.json"
echo "📋 One-liners:      $MEMORY_DIR/workspace_one_liners.txt"
echo "🧩 Legacy chunks:   $MEMORY_DIR/legacy_chunks.json"
echo ""
echo "🔧 Query commands:"
echo "  cat $MEMORY_DIR/workspace_one_liners.txt | grep 'skills_and_code'"
echo "  python3 -c "import json; d=json.load(open('$MEMORY_DIR/legacy_chunks.json')); [print(c['filename'], c['actionability']) for c in d['chunks'] if c['priority']=='P0']""
echo ""
echo "🚀 Next: Integrate legacy chunks with evolution strategy"
echo "  python3 ~/.picoclaw/memory/query.py summary"
