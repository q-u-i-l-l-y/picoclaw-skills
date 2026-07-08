#!/data/data/com.termux/files/usr/bin/bash
# PicoClaw Skills Library — Mesh Node Onboarding Script
# Run: bash install.sh

set -e

echo "=========================================="
echo "  PicoClaw Skills Library — Mesh Onboarding"
echo "=========================================="
echo ""
echo "  This script will:"
echo "    1. Detect your device's capabilities"
echo "    2. Generate a unique node identity"
echo "    3. Register you as a spoke in the mesh"
echo "    4. Activate Tier 1 revenue skills"
echo "    5. Align all actions with the North Star vision"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Config
SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"
PICOCLAW_HOME="${HOME}/.picoclaw"
NODE_ID_FILE="${PICOCLAW_HOME}/node_identity.json"
MESH_CONFIG="${PICOCLAW_HOME}/mesh_config.json"

# Step 1: Check Python
echo "[1/6] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "${RED}✗ Python3 not found. Please install Python3 first.${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Step 2: Create picoclaw home
echo "[2/6] Setting up PicoClaw home directory..."
mkdir -p "${PICOCLAW_HOME}"
mkdir -p "${PICOCLAW_HOME}/skills"
mkdir -p "${PICOCLAW_HOME}/memory"
mkdir -p "${PICOCLAW_HOME}/logs"
echo "${GREEN}✓ Directories created${NC}"

# Step 3: Detect capabilities
echo "[3/6] Detecting device capabilities..."
python3 -c "
import json
import os
import subprocess
import sys

caps = {
    'python_version': sys.version.split()[0],
    'platform': sys.platform,
    'has_git': False,
    'has_curl': False,
    'has_ssh': False,
    'has_termux_api': False,
    'has_camera': False,
    'has_sensors': False,
    'has_tts': False,
    'storage_available': False,
    'internet': False,
    'node_type': ['spoke-compute']
}

# Check tools
tools = {
    'has_git': ['git', '--version'],
    'has_curl': ['curl', '--version'],
    'has_ssh': ['ssh', '-V'],
    'has_termux_api': ['termux-api-start', '--help'],
}

for key, cmd in tools.items():
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=5)
        if result.returncode == 0 or 'version' in str(result.stderr).lower():
            caps[key] = True
    except:
        pass

# Check Termux-specific
try:
    subprocess.run(['termux-camera-photo', '--help'], capture_output=True, timeout=3)
    caps['has_camera'] = True
except:
    pass

try:
    subprocess.run(['termux-sensor', '--help'], capture_output=True, timeout=3)
    caps['has_sensors'] = True
except:
    pass

try:
    subprocess.run(['termux-tts-speak', '--help'], capture_output=True, timeout=3)
    caps['has_tts'] = True
except:
    pass

# Check storage
if os.path.exists('/sdcard') or os.path.exists(os.path.expanduser('~/storage')):
    caps['storage_available'] = True

# Check internet
try:
    import urllib.request
    urllib.request.urlopen('https://github.com', timeout=10)
    caps['internet'] = True
except:
    pass

# Determine node type
if caps['has_termux_api']:
    caps['node_type'].append('spoke-data')
if caps['has_camera'] or caps['has_sensors']:
    caps['node_type'].append('spoke-health')
if caps['internet']:
    caps['node_type'].append('spoke-revenue')

# Save capabilities
caps_file = os.path.expanduser('~/.picoclaw/device_capabilities.json')
with open(caps_file, 'w') as f:
    json.dump(caps, f, indent=2)

print('Capabilities detected:')
for k, v in caps.items():
    if isinstance(v, bool):
        status = '✓' if v else '✗'
        print(f'  [{status}] {k}')
    elif k == 'node_type':
        print(f'  [→] Node types: {', '.join(v)}')
"

echo "${GREEN}✓ Capabilities saved${NC}"

# Step 4: Generate node identity
echo "[4/6] Generating node identity..."
python3 -c "
import json
import os
import hashlib
import time

node_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
identity = {
    'node_id': node_id,
    'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
    'version': '3.0.0-mesh',
    'repo': 'picoclaw-skills',
    'role': 'spoke',
    'status': 'active'
}

id_file = os.path.expanduser('~/.picoclaw/node_identity.json')
with open(id_file, 'w') as f:
    json.dump(identity, f, indent=2)

print(f'Node ID: {node_id}')
print('Identity saved.')
"

echo "${GREEN}✓ Node identity generated${NC}"

# Step 5: Create mesh config
echo "[5/6] Configuring mesh network..."
python3 -c "
import json
import os

mesh_config = {
    'version': '3.0.0-mesh',
    'topology': 'hub_spoke_mesh',
    'hub_nodes': [
        {'id': 'hub-main', 'repo': 'q-u-i-l-l-y/picoclaw-dev', 'region': 'global'}
    ],
    'discovery': {
        'method': 'git_dht',
        'registry_repo': 'q-u-i-l-l-y/picoclaw-skills',
        'check_interval': 300
    },
    'federation': {
        'enabled': True,
        'learning_rounds': True,
        'privacy_mode': 'local_first',
        'contribution_weight': 1.0
    },
    'revenue_share': {
        'node_percentage': 70,
        'hub_percentage': 20,
        'rd_fund_percentage': 10
    }
}

config_file = os.path.expanduser('~/.picoclaw/mesh_config.json')
with open(config_file, 'w') as f:
    json.dump(mesh_config, f, indent=2)

print('Mesh configured.')
"

echo "${GREEN}✓ Mesh configuration saved${NC}"

# Step 6: Activate skills
echo "[6/6] Activating skills..."
if [ -d "${SKILLS_DIR}/skills" ]; then
    SKILL_COUNT=$(find "${SKILLS_DIR}/skills" -name "manifest.json" | wc -l)
    echo "Found ${SKILL_COUNT} skill manifests"

    # Link skills to picoclaw home
    ln -sf "${SKILLS_DIR}/skills" "${PICOCLAW_HOME}/skills/repo" 2>/dev/null || true
    echo "${GREEN}✓ Skills linked${NC}"
else
    echo "${YELLOW}⚠ No skills directory found. Skills will be auto-pulled on first run.${NC}"
fi

echo ""
echo "=========================================="
echo "  Onboarding Complete!"
echo "=========================================="
echo ""
echo "Your node is now part of the PicoClaw mesh."
echo ""
echo "Next steps:"
echo "  1. Run: python3 -m picoclaw status"
echo "  2. Run: python3 -m picoclaw skills"
echo "  3. Start revenue engine: python3 -m picoclaw revenue"
echo ""
echo "North Star: From Affiliate Income → Medical Device R&D → Metamaterial Health Mesh"
echo ""
