#!/bin/bash
###############################################################
# AI Linux Command Assistant — Ubuntu Launcher
###############################################################

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear
echo -e "${GREEN}"
echo "====================================================="
echo "  AI Linux Command Assistant — Starting..."
echo "====================================================="
echo -e "${NC}"

# ── SET COMPOSE COMMAND ───────────────────────────────────
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# ── CHECK DOCKER IS RUNNING ───────────────────────────────
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}[!] Docker is not running. Starting Docker...${NC}"
    sudo systemctl start docker
    sleep 5
fi

# ── START CONTAINERS ──────────────────────────────────────
echo "[1/2] Starting containers..."
$COMPOSE_CMD up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to start."
    echo -e "        Try running ./install.sh first.${NC}"
    exit 1
fi

# ── WAIT FOR APP ─────────────────────────────────────────
echo ""
echo "[2/2] Waiting for app to be ready..."
sleep 8

# ── OPEN BROWSER ─────────────────────────────────────────
echo ""
echo -e "${GREEN}"
echo "====================================================="
echo "  App is running!"
echo "  URL:      http://localhost:6080"
echo "  Password: aiassist"
echo "====================================================="
echo -e "${NC}"

# Auto open browser
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:6080" &
elif command -v gnome-open &> /dev/null; then
    gnome-open "http://localhost:6080" &
fi

echo "  Press Ctrl+C to stop viewing logs"
echo ""
$COMPOSE_CMD logs -f
