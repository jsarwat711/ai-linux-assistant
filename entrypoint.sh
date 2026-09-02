#!/bin/bash
###############################################################
# Entrypoint — FIXED v4
# Fixes VNC xstartup session + display issues
###############################################################

set -e

echo "============================================"
echo "  AI Linux Command Assistant"
echo "  Starting services..."
echo "============================================"

# ── SETUP RUNTIME DIR ─────────────────────────
export XDG_RUNTIME_DIR=/tmp/runtime-root
mkdir -p /tmp/runtime-root
chmod 700 /tmp/runtime-root

# ── CLEAN OLD VNC LOCKS ───────────────────────
vncserver -kill :1 > /dev/null 2>&1 || true
rm -f /tmp/.X1-lock
rm -f /tmp/.X11-unix/X1 2>/dev/null || true
sleep 1

# ── WRITE FIXED XSTARTUP ──────────────────────
mkdir -p /root/.vnc
cat > /root/.vnc/xstartup << 'EOF'
#!/bin/bash
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
export XDG_RUNTIME_DIR=/tmp/runtime-root
mkdir -p /tmp/runtime-root
chmod 700 /tmp/runtime-root
openbox &
sleep infinity
EOF
chmod +x /root/.vnc/xstartup

# ── START VNC SERVER ──────────────────────────
echo "[1/5] Starting VNC server..."
vncserver :1 \
    -geometry ${VNC_RESOLUTION:-1600x900} \
    -depth 24 \
    -rfbport 5901 \
    -rfbauth /root/.vnc/passwd \
    -localhost no

sleep 3

# ── VERIFY DISPLAY ────────────────────────────
echo "Verifying display :1 is available..."
DISPLAY_CHECK=0
until DISPLAY=:1 xdpyinfo > /dev/null 2>&1; do
    DISPLAY_CHECK=$((DISPLAY_CHECK + 1))
    if [ $DISPLAY_CHECK -ge 10 ]; then
        echo "⚠  Display :1 not ready after 10s"
        break
    fi
    echo "   Waiting for display... ($DISPLAY_CHECK/10)"
    sleep 1
done
echo "✔  Display :1 is ready!"

# ── START OPENBOX ─────────────────────────────
echo "[2/5] Starting Openbox window manager..."
DISPLAY=:1 openbox --startup "openbox --reconfigure" &
sleep 2

# ── START noVNC ───────────────────────────────
echo "[3/5] Starting noVNC on port 6080..."
websockify \
    --web /usr/share/novnc \
    --wrap-mode=ignore \
    0.0.0.0:6080 \
    localhost:5901 &

sleep 2

# ── WAIT FOR OLLAMA ───────────────────────────
echo "[4/5] Waiting for Ollama..."

OLLAMA_HOST=${OLLAMA_HOST:-"ollama"}
OLLAMA_PORT=${OLLAMA_PORT:-"11434"}
MAX_WAIT=120
COUNT=0

until curl -sf \
    "http://${OLLAMA_HOST}:${OLLAMA_PORT}/api/tags" \
    > /dev/null 2>&1; do
    COUNT=$((COUNT + 1))
    if [ $COUNT -ge $MAX_WAIT ]; then
        echo "⚠  Ollama timeout — starting app anyway..."
        break
    fi
    echo "   Waiting for Ollama... (${COUNT}s / ${MAX_WAIT}s)"
    sleep 1
done

echo "✔  Ollama is ready!"

# ── LAUNCH APP ────────────────────────────────
echo "[5/5] Launching AI Linux Command Assistant..."
echo "============================================"
echo "  Open browser → http://localhost:6080"
echo "  VNC Password: aiassist"
echo "============================================"

DISPLAY=:1 python3 /app/ai_linux_assistant.py

# ── KEEP CONTAINER ALIVE ─────────────────────
wait
