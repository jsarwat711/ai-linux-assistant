###############################################################
# AI Linux Command Assistant — Dockerfile (FIXED COMPLETE)
###############################################################

FROM ubuntu:22.04

# Avoid interactive prompts during install
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Los_Angeles

# ── INSTALL ALL PACKAGES ──────────────────────────────────
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxrender1 \
    libxext6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxcb-util1 \
    libxcb-cursor0 \
    libxcb-glx0 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libfontconfig1 \
    libfreetype6 \
    libqt5x11extras5 \
    xauth \
    x11-xserver-utils \
    tigervnc-standalone-server \
    tigervnc-tools \
    novnc \
    websockify \
    openbox \
    obconf \
    fonts-dejavu \
    fonts-liberation \
    fontconfig \
    supervisor \
    curl \
    wget \
    net-tools \
    xterm \
    x11-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── INSTALL PYTHON DEPENDENCIES ───────────────────────────
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# ── SET WORKING DIRECTORY ─────────────────────────────────
WORKDIR /app

# ── COPY APP FILES ────────────────────────────────────────
COPY ai_linux_assistant.py .

# ── COPY CONFIG FILES ─────────────────────────────────────
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ── SETUP VNC PASSWORD ────────────────────────────────────
RUN mkdir -p /root/.vnc && \
    echo "aiassist" | vncpasswd -f > /root/.vnc/passwd && \
    chmod 600 /root/.vnc/passwd

# ── SETUP VNC XSTARTUP ────────────────────────────────────
RUN mkdir -p /root/.vnc && \
    printf '#!/bin/bash\nunset SESSION_MANAGER\nunset DBUS_SESSION_BUS_ADDRESS\nexport XDG_RUNTIME_DIR=/tmp/runtime-root\nmkdir -p /tmp/runtime-root\nchmod 700 /tmp/runtime-root\nopenbox &\nsleep infinity\n' \
    > /root/.vnc/xstartup && \
    chmod +x /root/.vnc/xstartup

# ── SETUP OPENBOX CONFIG ──────────────────────────────────
RUN mkdir -p /root/.config/openbox && \
    printf '<?xml version="1.0" encoding="UTF-8"?>\n<openbox_config>\n  <theme><name>Bear2</name></theme>\n  <desktops><number>1</number></desktops>\n</openbox_config>\n' \
    > /root/.config/openbox/rc.xml

# ── EXPOSE PORTS ──────────────────────────────────────────
EXPOSE 5901
EXPOSE 6080

# ── ENTRYPOINT ────────────────────────────────────────────
ENTRYPOINT ["/entrypoint.sh"]
