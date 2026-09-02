#!/bin/bash
###############################################################
# AI Linux Command Assistant — Ubuntu Stopper
###############################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${RED}"
echo "====================================================="
echo "  Stopping AI Linux Command Assistant..."
echo "====================================================="
echo -e "${NC}"

if docker compose version &> /dev/null; then
    docker compose down
else
    docker-compose down
fi

echo ""
echo -e "${GREEN}[OK] App stopped successfully.${NC}"
echo ""
