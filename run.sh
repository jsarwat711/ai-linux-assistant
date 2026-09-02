#!/bin/bash
###############################################################
# AI Linux Command Assistant — Ubuntu Desktop Launcher
###############################################################

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo -e "${GREEN}"
echo "====================================================="
echo "  AI Linux Command Assistant"
echo "  Starting..."
echo "====================================================="
echo -e "${NC}"

cd "$(dirname "$0")"

# ── STEP 1: CHECK DOCKER ─────────────────────────────────
echo -e "${GREEN}[1/5] Checking Docker...${NC}"

if ! command -v docker &>/dev/null; then
    echo -e "${YELLOW}  Installing Docker...${NC}"

    sudo apt-get update -qq
    sudo apt-get install -y -qq \
        ca-certificates curl gnupg lsb-release

    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        sudo gpg --dearmor \
        -o /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) \
      signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list \
      > /dev/null

    sudo apt-get update -qq
    sudo apt-get install -y -qq \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-compose-plugin

    sudo usermod -aG docker $USER
    echo -e "${YELLOW}  Docker installed!"
    echo "  Please log out and log back in,"
    echo -e "  then run ./run.sh again.${NC}"
    exit 0
fi

if ! docker info &>/dev/null; then
    sudo systemctl start docker
    sleep 3
fi

echo -e "${GREEN}  [OK] Docker ready!${NC}"
echo ""

# ── STEP 2: CHECK PYTHON ─────────────────────────────────
echo -e "${GREEN}[2/5] Checking Python...${NC}"

if ! command -v python3 &>/dev/null; then
    echo -e "${YELLOW}  Installing Python...${NC}"
    sudo apt-get install -y -qq python3 python3-pip
fi
echo -e "${GREEN}  [OK] Python ready!${NC}"
echo ""

# ── STEP 3: INSTALL PYTHON PACKAGES ─────────────────────
echo -e "${GREEN}[3/5] Installing Python packages...${NC}"

# Install PyQt5 system package first
sudo apt-get install -y -qq \
    python3-pyqt5 \
    python3-pyqt5.qtsvg \
    libxcb-cursor0 \
    libxcb-xinerama0

pip3 install -q -r requirements.txt

echo -e "${GREEN}  [OK] Packages ready!${NC}"
echo ""

# ── STEP 4: START OLLAMA ─────────────────────────────────
echo -e "${GREEN}[4/5] Starting Ollama AI engine...${NC}"

# Set compose command
if docker compose version &>/dev/null; then
    DC="docker compose"
else
    DC="docker-compose"
fi

$DC up -d

echo "  Waiting for Ollama to be ready..."
until curl -sf http://localhost:11434/api/tags \
    >/dev/null 2>&1; do
    echo "  Still waiting..."
    sleep 3
done
echo -e "${GREEN}  [OK] Ollama is ready!${NC}"
echo ""

# ── STEP 5: CHECK AND PULL MODEL ─────────────────────────
echo -e "${GREEN}[5/5] Checking AI model...${NC}"

MODEL_CHECK=$(curl -sf http://localhost:11434/api/tags | \
    grep -c "llama3" || true)

if [ "$MODEL_CHECK" -eq 0 ]; then
    echo "  Downloading AI model (~4.7 GB first time only)..."
    docker exec ollama ollama pull llama3
fi

echo -e "${GREEN}  [OK] Model ready!${NC}"
echo ""

# ── LAUNCH DESKTOP APP ───────────────────────────────────
echo -e "${GREEN}"
echo "====================================================="
echo "  Launching AI Command Assistant..."
echo "====================================================="
echo -e "${NC}"

python3 ai_linux_assistant.py

# ── CLEANUP ON EXIT ──────────────────────────────────────
echo ""
echo -e "${YELLOW}  App closed."
read -p "  Stop Ollama engine too? (y/n): " STOP
if [[ "$STOP" == "y" || "$STOP" == "Y" ]]; then
    $DC down
    echo -e "${GREEN}  Ollama stopped.${NC}"
fi
echo "  Goodbye!"
