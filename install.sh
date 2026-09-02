#!/bin/bash
###############################################################
# AI Linux Command Assistant — Ubuntu Installer
###############################################################

set -e

# ── COLORS ────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo -e "${GREEN}"
echo "====================================================="
echo "  AI Linux Command Assistant"
echo "  Installer for Ubuntu"
echo "====================================================="
echo -e "${NC}"

# ── CHECK ROOT ────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[!] Running without sudo."
    echo -e "    Some steps may ask for your password.${NC}"
    echo ""
fi

# ── STEP 1 — CHECK DOCKER ─────────────────────────────────
echo -e "${GREEN}[1/4] Checking Docker...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}[!] Docker not found. Installing Docker...${NC}"
    echo ""

    # Install Docker
    sudo apt-get update -qq
    sudo apt-get install -y -qq \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) \
      signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -qq
    sudo apt-get install -y -qq \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-compose-plugin

    # Add user to docker group
    sudo usermod -aG docker $USER

    echo -e "${GREEN}[OK] Docker installed.${NC}"
    echo ""
    echo -e "${YELLOW}[!] IMPORTANT: Log out and log back in,"
    echo -e "    then run ./install.sh again.${NC}"
    exit 0
else
    echo -e "${GREEN}[OK] Docker found: $(docker --version)${NC}"
fi

echo ""

# ── STEP 2 — CHECK DOCKER COMPOSE ────────────────────────
echo -e "${GREEN}[2/4] Checking Docker Compose...${NC}"

if ! docker compose version &> /dev/null && \
   ! docker-compose --version &> /dev/null; then
    echo -e "${YELLOW}[!] Installing Docker Compose plugin...${NC}"
    sudo apt-get install -y -qq docker-compose-plugin
fi

# Set compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo -e "${GREEN}[OK] Docker Compose ready.${NC}"
echo ""

# ── STEP 3 — BUILD APP ────────────────────────────────────
echo -e "${GREEN}[3/4] Building AI Command Assistant...${NC}"
echo "      (First time may take 5-10 minutes)"
echo ""

$COMPOSE_CMD build

echo ""
echo -e "${GREEN}[OK] Build complete!${NC}"
echo ""

# ── STEP 4 — DOWNLOAD AI MODEL ───────────────────────────
echo -e "${GREEN}[4/4] Downloading AI model (llama3 ~4.7GB)...${NC}"
echo "      This only happens ONCE. Please wait..."
echo ""

$COMPOSE_CMD run --rm ollama_pull

echo ""
echo -e "${GREEN}[OK] AI model downloaded and ready!${NC}"
echo ""

# ── MAKE SCRIPTS EXECUTABLE ──────────────────────────────
chmod +x start.sh stop.sh 2>/dev/null || true

# ── DONE ─────────────────────────────────────────────────
echo -e "${GREEN}"
echo "====================================================="
echo "  Installation Complete!"
echo "====================================================="
echo -e "${NC}"
echo "  To START the app:  ./start.sh"
echo "  To STOP the app:   ./stop.sh"
echo "  Then open browser: http://localhost:6080"
echo "  Password:          aiassist"
echo ""
echo "====================================================="
