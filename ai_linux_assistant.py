###############################################################
# AI LINUX COMMAND ASSISTANT
# Python + PyQt5 + Ollama
# Professional Dark Theme — FINAL PUBLISH VERSION
###############################################################

import sys
import subprocess
import json
import os
import re
import datetime
import sqlite3
import time
import webbrowser

# ─── PySide6 Imports ──────────────────────────────────────────────────────────
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QLabel, QSplitter, QFrame, QScrollArea,
    QStatusBar, QComboBox, QToolBar,
    QMessageBox, QFileDialog, QListWidget,
    QListWidgetItem, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QTabWidget, QProgressBar
)

from PySide6.QtCore import (
    Qt, QThread, Signal, QTimer, QSize       # ✅ QThread here
)

from PySide6.QtGui import (
    QFont, QColor, QTextCursor, QPalette,
    QIcon, QTextCharFormat, QSyntaxHighlighter,
    QAction                                  # ✅ QAction here
)




###############################################################
# CONFIG
###############################################################
APP_NAME         = "AI Linux Command Assistant"
VERSION          = "1.0.0"
HISTORY_FILE     = "command_history.json"
DEFAULT_MODEL    = "llama3"
FAVORITES_DB     = "favorites.db"
SETTINGS_FILE    = "settings.json"

# ── FONT SIZE SETTINGS ────────────────────────────────────
DEFAULT_FONT_SIZE = 14
MIN_FONT_SIZE     = 10
MAX_FONT_SIZE     = 26

# ── OLLAMA CONNECTION ─────────────────────────────────────
OLLAMA_URL = os.environ.get(
    "OLLAMA_URL", "http://localhost:11434"
)

# ── GUMROAD STORE LINK ────────────────────────────────────
GUMROAD_URL = "https://sarwatify.gumroad.com/l/jrpxl"


SYSTEM_PROMPT = """
You are a professional Linux system administrator and DevOps engineer.
Your role is to help users run Linux commands for system testing,
monitoring, debugging, and administration.

When responding:
1. Always provide the exact command to run
2. Wrap commands in ```bash ``` code blocks
3. Explain what the command does briefly
4. Warn about any dangerous operations
5. Suggest safer alternatives when applicable
6. Format output clearly

Be concise, accurate, and professional.
"""

###############################################################
# DARK THEME
###############################################################
DARK_THEME = """
QMainWindow {
    background-color: #1e1e2e;
}
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}
QTextEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}
QLineEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 2px solid #313244;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
}
QLineEdit:focus {
    border: 2px solid #89b4fa;
}
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton:hover  { background-color: #45475a; }
QPushButton:pressed{ background-color: #585b70; }
QPushButton#btn_send  { background-color:#89b4fa; color:#1e1e2e; }
QPushButton#btn_send:hover { background-color:#b4befe; }
QPushButton#btn_run   { background-color:#a6e3a1; color:#1e1e2e; }
QPushButton#btn_run:hover  { background-color:#94e2d5; }
QPushButton#btn_clear { background-color:#f38ba8; color:#1e1e2e; }
QPushButton#btn_clear:hover{ background-color:#eba0ac; }
QPushButton#btn_copy  { background-color:#fab387; color:#1e1e2e; }
QPushButton#btn_copy:hover { background-color:#f9e2af; }
QSplitter::handle { background-color:#313244; width:4px; }
QLabel#label_title {
    font-size:18px; font-weight:bold;
    color:#89b4fa; padding:6px;
}
QLabel#label_section {
    font-size:12px; font-weight:bold;
    color:#6c7086; padding:4px;
}
QComboBox {
    background-color:#313244; color:#cdd6f4;
    border:1px solid #45475a; border-radius:6px;
    padding:4px 8px; min-width:140px;
}
QComboBox::drop-down { border:none; }
QComboBox QAbstractItemView {
    background-color:#313244; color:#cdd6f4;
    border:1px solid #585b70;
    selection-background-color:#45475a;
}
QStatusBar {
    background-color:#181825;
    color:#6c7086; font-size:11px;
}
QListWidget {
    background-color:#181825; color:#cdd6f4;
    border:1px solid #313244; border-radius:6px;
}
QListWidget::item:hover  { background-color:#313244; color:#89b4fa; }
QListWidget::item:selected{ background-color:#45475a; color:#cdd6f4; }
QScrollBar:vertical {
    background:#181825; width:8px; border-radius:4px;
}
QScrollBar::handle:vertical {
    background:#45475a; border-radius:4px; min-height:20px;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height:0px; }
QToolBar {
    background-color:#181825;
    border-bottom:1px solid #313244;
    spacing:6px; padding:4px;
}
QTabWidget::pane {
    border:1px solid #313244; border-radius:6px;
}
QTabBar::tab {
    background:#181825; color:#6c7086;
    padding:6px 16px; border-radius:4px;
    margin-right:2px; font-size:12px; font-weight:bold;
}
QTabBar::tab:selected { background:#313244; color:#f9e2af; }
QTabBar::tab:hover    { background:#313244; color:#cdd6f4; }
"""

###############################################################
# OLLAMA — START IF NOT RUNNING
###############################################################
def start_ollama():
    """Start Ollama if not already running"""
    import requests as req
    try:
        req.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return True  # already running
    except:
        pass

    # Search common install paths
    ollama_paths = [
        os.path.join(
            os.environ.get("LOCALAPPDATA", ""),
            "Programs", "Ollama", "ollama.exe"
        ),
        r"C:\Program Files\Ollama\ollama.exe",
        os.path.join(
            os.path.dirname(sys.executable),
            "ollama", "ollama.exe"
        ),
        "ollama"  # fallback: if in PATH
    ]

    for path in ollama_paths:
        try:
            subprocess.Popen(
                [path, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW
                    if sys.platform == "win32" else 0
                )
            )
            return True
        except:
            continue
    return False

###############################################################
# SPLASH SCREEN
###############################################################
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Activate {APP_NAME}")
        self.setFixedSize(580, 700)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                color: #ffffff;
                font-family: Consolas;
            }
            QLabel  { color: #ffffff; }
            QLineEdit {
                background-color: #0d1f0d;
                color: #00ff88;
                border: 2px solid #00aa55;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00ff88;
                background-color: #0a2a0a;
            }
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }
        """)

        # ── Center on screen ──────────────────────────────────────
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

        # ── Scroll Area ───────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1a1a2e;
            }
            QScrollBar:vertical {
                background: #1a1a2e;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #444466;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #00ff88;
            }
        """)

        # ── Inner Container ───────────────────────────────────────
        container = QWidget()
        container.setStyleSheet("background-color: #1a1a2e;")

        layout = QVBoxLayout(container)
        layout.setSpacing(14)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        scroll.setWidget(container)

        # ── Attach Scroll to Window ───────────────────────────────
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)


###############################################################
# STARTUP WORKER
###############################################################
class StartupWorker(QThread):
    status_update = Signal(str)
    finished      = Signal(bool, str)

    def run(self):
        import requests as req

        # Start Ollama
        self.status_update.emit("Starting AI engine...")
        if not start_ollama():
            self.finished.emit(
                False,
                "Could not start Ollama.\n"
                "Please install from https://ollama.com"
            )
            return

        # Wait for Ollama ready
        self.status_update.emit(
            "Waiting for AI engine to be ready..."
        )
        for i in range(30):
            try:
                r = req.get(
                    f"{OLLAMA_URL}/api/tags", timeout=2
                )
                if r.status_code == 200:
                    break
            except:
                pass
            time.sleep(2)
            self.status_update.emit(
                f"Waiting for AI engine... ({(i+1)*2}s)"
            )
        else:
            self.finished.emit(
                False,
                "Ollama did not start in time.\n"
                "Please try again."
            )
            return

        # Check/pull model
        self.status_update.emit("Checking AI model...")
        try:
            r = req.get(
                f"{OLLAMA_URL}/api/tags", timeout=5
            )
            models = [
                m['name']
                for m in r.json().get('models', [])
            ]
            has_model = any(
                'llama' in m.lower() for m in models
            )
            if not has_model:
                self.status_update.emit(
                    "Downloading AI model (~4.7 GB)...\n"
                    "First time only. Please wait..."
                )
                subprocess.run(
                    ["ollama", "pull", "llama3"],
                    capture_output=True
                )
        except Exception as e:
            self.finished.emit(False, str(e))
            return

        self.status_update.emit("Ready!")
        self.finished.emit(True, "")

###############################################################
# LICENSE DIALOG
###############################################################
class LicenseDialog(QWidget):
    license_accepted = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Activate {APP_NAME}")
        self.setFixedSize(580, 700)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                color: #ffffff;
                font-family: Consolas;
            }
            QLabel  { color: #ffffff; }
            QLineEdit {
                background-color: #2a2a4a;
                color: #00ff88;
                border: 1px solid #444466;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }
        """)

        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width()  - self.width())  // 2,
            (screen.height() - self.height()) // 2
        )

        # ── Scroll Area Wrapper ───────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1a1a2e;
            }
            QScrollBar:vertical {
                background: #1a1a2e;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #444466;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #00ff88;
            }
        """)

        # ── Inner Container ───────────────────────────────────────
        container = QWidget()
        container.setStyleSheet("background-color: #1a1a2e;")

        layout = QVBoxLayout(container)
        layout.setSpacing(14)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        scroll.setWidget(container)

        # ── Main Layout ───────────────────────────────────────────
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # ── Header ────────────────────────────────────────────────
        title = QLabel("🔐  Activate AI Linux Command Assistant")
        title.setStyleSheet(
            "font-size:18px; font-weight:bold; color:#00ff88;"
        )
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Choose one of the options below to get started:")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color:#888888; font-size:12px;")
        layout.addWidget(subtitle)

        # ── Divider ───────────────────────────────────────────────
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color:#333355;")
        layout.addWidget(line)

        # ══════════════════════════════════════════════════════════
        # OPTION 1 — Activate License
        # ══════════════════════════════════════════════════════════
        opt1_frame = QFrame()
        opt1_frame.setMinimumWidth(500)
        opt1_frame.setStyleSheet("""
            QFrame {
                background-color: #1f2a1f;
                border: 2px solid #00ff88;
                border-radius: 10px;
                padding: 4px;
            }
        """)
        opt1_layout = QVBoxLayout(opt1_frame)
        opt1_layout.setSpacing(10)

        # ── Option Title ──────────────────────────────────────────
        opt1_title = QLabel("✅  Option 1 — Already Have a License Key?")
        opt1_title.setStyleSheet(
            "font-size:14px; font-weight:bold; color:#00ff88; border:none;"
        )
        opt1_layout.addWidget(opt1_title)

        opt1_desc = QLabel(
            "Enter your purchase email and license key below,\n"
            "then click  'Activate License'  to unlock the full version."
        )
        opt1_desc.setStyleSheet(
            "font-size:11px; color:#aaaaaa; border:none; padding-bottom:4px;"
        )
        opt1_desc.setWordWrap(True)
        opt1_layout.addWidget(opt1_desc)

        # ── Divider ───────────────────────────────────────────────
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("color:#2a4a2a; border:none; background:#2a4a2a; max-height:1px;")
        opt1_layout.addWidget(div)

        # ── Email Row ─────────────────────────────────────────────
        email_lbl = QLabel("📧  Step 1 — Enter your purchase email address:")
        email_lbl.setStyleSheet(
            "font-size:12px; font-weight:bold; color:#ffffff; border:none; margin-top:4px;"
        )
        opt1_layout.addWidget(email_lbl)

        email_hint = QLabel(
            "   ℹ️  Use the same email you used when buying on Gumroad"
        )
        email_hint.setStyleSheet(
            "font-size:11px; color:#888888; border:none; margin-bottom:2px;"
        )
        opt1_layout.addWidget(email_hint)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("   📧  e.g.  your@email.com")
        self.email_input.setMinimumHeight(38)
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: #0d1f0d;
                color: #00ff88;
                border: 2px solid #00aa55;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00ff88;
                background-color: #0a2a0a;
            }
        """)
        opt1_layout.addWidget(self.email_input)

        # ── License Key Row ───────────────────────────────────────
        key_lbl = QLabel("🔑  Step 2 — Enter your license key:")
        key_lbl.setStyleSheet(
            "font-size:12px; font-weight:bold; color:#ffffff; border:none; margin-top:6px;"
        )
        opt1_layout.addWidget(key_lbl)

        key_hint = QLabel(
            "   ℹ️  Your license key was sent to your email after purchase"
        )
        key_hint.setStyleSheet(
            "font-size:11px; color:#888888; border:none; margin-bottom:2px;"
        )
        opt1_layout.addWidget(key_hint)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("   🔑  e.g.  XXXX-XXXX-XXXX-XXXX")
        self.key_input.setMinimumHeight(38)
        self.key_input.setStyleSheet("""
            QLineEdit {
                background-color: #0d1f0d;
                color: #00ff88;
                border: 2px solid #00aa55;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00ff88;
                background-color: #0a2a0a;
            }
        """)
        opt1_layout.addWidget(self.key_input)

        # ── Status Label ──────────────────────────────────────────
        self.status_lbl = QLabel("")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setMinimumHeight(22)
        self.status_lbl.setStyleSheet(
            "color:#ff4444; font-size:12px; border:none; margin-top:2px;"
        )
        opt1_layout.addWidget(self.status_lbl)

        # ── Activate Button ───────────────────────────────────────
        self.btn_activate = QPushButton("✅  Step 3 — Click Here to Activate License")
        self.btn_activate.setMinimumHeight(42)
        self.btn_activate.setStyleSheet("""
            QPushButton {
                background-color: #00aa55;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
                margin-top: 4px;
            }
            QPushButton:hover {
                background-color: #00ff88;
                color: #000000;
            }
            QPushButton:disabled {
                background-color: #1a3a1a;
                color: #555555;
            }
        """)
        self.btn_activate.clicked.connect(self.do_activate)
        opt1_layout.addWidget(self.btn_activate)

        layout.addWidget(opt1_frame)

        # ══════════════════════════════════════════════════════════
        # OPTION 2 — Buy License
        # ══════════════════════════════════════════════════════════
        opt2_frame = QFrame()
        opt2_frame.setMinimumWidth(500)
        opt2_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2010;
                border: 1px solid #ffaa00;
                border-radius: 10px;
                padding: 4px;
            }
        """)
        opt2_layout = QVBoxLayout(opt2_frame)
        opt2_layout.setSpacing(8)

        opt2_title = QLabel("🛒  Option 2 — Don't Have a License Yet?")
        opt2_title.setStyleSheet(
            "font-size:13px; font-weight:bold; color:#ffaa00; border:none;"
        )
        opt2_layout.addWidget(opt2_title)

        opt2_desc = QLabel(
            "Purchase the full version to unlock ALL features:\n"
            "advanced AI commands, favorites, history & future updates."
        )
        opt2_desc.setStyleSheet("font-size:11px; color:#aaaaaa; border:none;")
        opt2_desc.setWordWrap(True)
        opt2_layout.addWidget(opt2_desc)

        btn_buy = QPushButton("🛒  Buy Full License — Click to Open Purchase Page")
        btn_buy.setStyleSheet("""
            QPushButton {
                background-color: #cc7700;
                color: #ffffff;
            }
            QPushButton:hover { background-color: #ffaa00; color:#000000; }
        """)
        btn_buy.clicked.connect(
            lambda: webbrowser.open("https://sarwatify.gumroad.com/l/jrpxl")
        )
        opt2_layout.addWidget(btn_buy)

        layout.addWidget(opt2_frame)

        # ══════════════════════════════════════════════════════════
        # OPTION 3 — Free Trial
        # ══════════════════════════════════════════════════════════
        opt3_frame = QFrame()
        opt3_frame.setMinimumWidth(500)
        opt3_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border: 1px solid #5566aa;
                border-radius: 10px;
                padding: 4px;
            }
        """)
        opt3_layout = QVBoxLayout(opt3_frame)
        opt3_layout.setSpacing(8)

        opt3_title = QLabel("🆓  Option 3 — Continue with Free Trial")
        opt3_title.setStyleSheet(
            "font-size:13px; font-weight:bold; color:#8899ff; border:none;"
        )
        opt3_layout.addWidget(opt3_title)

        opt3_desc = QLabel(
            "Use the app in free trial mode with limited features.\n"
            "You can activate your license at any time later."
        )
        opt3_desc.setStyleSheet("font-size:11px; color:#aaaaaa; border:none;")
        opt3_desc.setWordWrap(True)
        opt3_layout.addWidget(opt3_desc)

        btn_free = QPushButton("🆓  Continue with Free Trial (Limited Features)")
        btn_free.setStyleSheet("""
            QPushButton {
                background-color: #2a2a4a;
                color: #8899ff;
            }
            QPushButton:hover { background-color: #5566aa; color:#ffffff; }
        """)
        btn_free.clicked.connect(self.license_accepted)
        opt3_layout.addWidget(btn_free)

        layout.addWidget(opt3_frame)

        # ── Footer ────────────────────────────────────────────────
        footer = QLabel("🔒  License verified securely via Gumroad")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(
            "font-size:11px; color:#444466; margin-top:5px;"
        )
        layout.addWidget(footer)

    # ──────────────────────────────────────────────────────────────
    def do_activate(self):
        from license_manager import activate_license

        key   = self.key_input.text().strip()
        email = self.email_input.text().strip()

        if not key or not email:
            self._set_status(
                "⚠  Please enter both your email and license key.",
                "#ffaa00"
            )
            return

        self._set_status("⏳  Verifying license...", "#ffaa00")
        self.btn_activate.setEnabled(False)
        QApplication.processEvents()

        valid, message = activate_license(key, email)

        if valid:
            self._set_status("✅  " + message, "#00ff88")
            QTimer.singleShot(800, self.license_accepted)
        else:
            self._set_status("❌  " + message, "#ff4444")
            self.btn_activate.setEnabled(True)

    def _set_status(self, text, color):
        self.status_lbl.setStyleSheet(
            f"color:{color}; font-size:12px;"
        )
        self.status_lbl.setText(text)
        QApplication.processEvents()

###############################################################
# SYNTAX HIGHLIGHTER
###############################################################
class BashHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        cmd_fmt = QTextCharFormat()
        cmd_fmt.setForeground(QColor("#89b4fa"))
        cmd_fmt.setFontWeight(QFont.Bold)
        keywords = [
            "ls","cd","pwd","mkdir","rm","cp","mv",
            "cat","grep","find","chmod","chown","sudo",
            "apt","yum","systemctl","service","ps","top",
            "df","du","free","netstat","ifconfig","ip",
            "ping","curl","wget","tar","zip","unzip",
            "ssh","scp","rsync","kill","killall","echo",
            "export","source","nano","vim","tail","head",
            "awk","sed","sort","uniq","wc","xargs",
            "journalctl","dmesg","lsof","strace","htop"
        ]
        for kw in keywords:
            self.rules.append((
                re.compile(r'\b' + kw + r'\b'), cmd_fmt
            ))

        flag_fmt = QTextCharFormat()
        flag_fmt.setForeground(QColor("#a6e3a1"))
        self.rules.append((
            re.compile(r'\s-{1,2}[\w-]+'), flag_fmt
        ))

        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor("#f9e2af"))
        self.rules.append((re.compile(r'"[^"]*"'), str_fmt))
        self.rules.append((re.compile(r"'[^']*'"), str_fmt))

        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor("#6c7086"))
        comment_fmt.setFontItalic(True)
        self.rules.append((re.compile(r'#.*'), comment_fmt))

        pipe_fmt = QTextCharFormat()
        pipe_fmt.setForeground(QColor("#cba6f7"))
        pipe_fmt.setFontWeight(QFont.Bold)
        self.rules.append((
            re.compile(r'[|><&;]'), pipe_fmt
        ))

        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor("#fab387"))
        self.rules.append((re.compile(r'\b\d+\b'), num_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(
                    match.start(),
                    match.end() - match.start(),
                    fmt
                )

###############################################################
# CHAT MESSAGE HTML FORMATTER
###############################################################
def format_chat_html(role, message, timestamp):
    if role == "user":
        color = "#89b4fa"; label = "YOU";          bg = "#313244"
        align = "right"
    elif role == "assistant":
        color = "#a6e3a1"; label = "AI ASSISTANT"; bg = "#1e1e2e"
        align = "left"
    else:
        color = "#f38ba8"; label = "SYSTEM";       bg = "#1e1e2e"
        align = "left"

    message = re.sub(
        r'```(?:bash|sh)?\n?(.*?)```',
        r'<pre style="background:#181825;color:#a6e3a1;'
        r'padding:10px;border-radius:6px;'
        r'border-left:3px solid #a6e3a1;'
        r'font-family:Consolas,monospace;">\1</pre>',
        message, flags=re.DOTALL
    )
    message = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', message)
    message = re.sub(r'\*(.*?)\*',     r'<i>\1</i>', message)
    message = message.replace('\n', '<br>')

    return f"""
    <div style="text-align:{align};margin:8px 4px;">
        <span style="font-size:10px;color:{color};
                     font-weight:bold;">
            {label} &nbsp;
            <span style="color:#6c7086;">{timestamp}</span>
        </span><br>
        <span style="
            display:inline-block;
            background:{bg};
            color:#cdd6f4;
            border:1px solid #313244;
            border-left:3px solid {color};
            border-radius:8px;
            padding:10px 14px;
            max-width:90%;
            text-align:left;
            line-height:1.6;
        ">{message}</span>
    </div><br>
    """

###############################################################
# OLLAMA WORKER THREAD
###############################################################
class OllamaWorker(QThread):
    response_chunk = Signal(str)
    response_done  = Signal(str)
    error_signal   = Signal(str)

    def __init__(self, model, messages):
        super().__init__()
        self.model    = model
        self.messages = messages
        self._full    = ""

    def run(self):
        try:
            import ollama
            client = ollama.Client(host=OLLAMA_URL)
            stream = client.chat(
                model=self.model,
                messages=self.messages,
                stream=True
            )
            for chunk in stream:
                text = chunk['message']['content']
                self._full += text
                self.response_chunk.emit(text)
            self.response_done.emit(self._full)
        except Exception as e:
            self.error_signal.emit(str(e))

###############################################################
# COMMAND RUNNER THREAD
###############################################################
class CommandRunner(QThread):
    output_signal = Signal(str)
    error_signal  = Signal(str)
    done_signal   = Signal(int, float)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        start = time.time()
        try:
            process = subprocess.Popen(
                self.command, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(timeout=60)
            elapsed = time.time() - start
            if stdout: self.output_signal.emit(stdout)
            if stderr: self.error_signal.emit(stderr)
            self.done_signal.emit(process.returncode, elapsed)
        except subprocess.TimeoutExpired:
            self.error_signal.emit("Command timed out (60s)")
            self.done_signal.emit(-1, 60.0)
        except Exception as e:
            self.error_signal.emit(str(e))
            self.done_signal.emit(-1, 0.0)

###############################################################
# FAVORITES DATABASE
###############################################################
class FavoritesDB:
    def __init__(self, db_path=FAVORITES_DB):
        self.db_path = db_path
        self.conn    = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                command     TEXT NOT NULL,
                category    TEXT DEFAULT 'General',
                description TEXT DEFAULT '',
                created_at  TEXT DEFAULT (datetime('now'))
            )
        """)
        self.conn.commit()

    def add(self, name, command,
            category="General", description=""):
        self.conn.execute(
            "INSERT INTO favorites "
            "(name,command,category,description) "
            "VALUES (?,?,?,?)",
            (name, command, category, description)
        )
        self.conn.commit()

    def update(self, fav_id, name, command,
               category, description):
        self.conn.execute(
            "UPDATE favorites SET "
            "name=?,command=?,category=?,description=? "
            "WHERE id=?",
            (name, command, category, description, fav_id)
        )
        self.conn.commit()

    def delete(self, fav_id):
        self.conn.execute(
            "DELETE FROM favorites WHERE id=?", (fav_id,)
        )
        self.conn.commit()

    def get_all(self):
        cur = self.conn.execute(
            "SELECT id,name,command,category,"
            "description,created_at FROM favorites "
            "ORDER BY category,name"
        )
        return cur.fetchall()

    def search(self, keyword):
        kw = f"%{keyword}%"
        cur = self.conn.execute(
            "SELECT id,name,command,category,"
            "description,created_at FROM favorites "
            "WHERE name LIKE ? OR command LIKE ? "
            "OR description LIKE ? OR category LIKE ? "
            "ORDER BY category,name",
            (kw, kw, kw, kw)
        )
        return cur.fetchall()

    def get_categories(self):
        cur = self.conn.execute(
            "SELECT DISTINCT category FROM favorites "
            "ORDER BY category"
        )
        return [r[0] for r in cur.fetchall()]

    def export_json(self, path):
        rows = self.get_all()
        data = [
            {"id":r[0],"name":r[1],"command":r[2],
             "category":r[3],"description":r[4],
             "created_at":r[5]}
            for r in rows
        ]
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def import_json(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        for item in data:
            self.add(
                item.get("name","Imported"),
                item.get("command",""),
                item.get("category","General"),
                item.get("description","")
            )

###############################################################
# CATEGORIES
###############################################################
CATEGORIES = [
    "General","System","Network","Files",
    "Process","Disk","Testing","Security",
    "Docker","Custom"
]

###############################################################
# ADD / EDIT FAVORITE DIALOG
###############################################################
class FavoriteDialog(QDialog):
    def __init__(self, parent=None, name="", command="",
                 category="General", description=""):
        super().__init__(parent)
        self.setWindowTitle("Save Favorite Command")
        self.setMinimumWidth(480)
        self.setStyleSheet(DARK_THEME)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("⭐  Save to Favorites")
        title.setStyleSheet(
            "font-size:16px;font-weight:bold;color:#f9e2af;"
        )
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText(
            "e.g. Check Disk Usage"
        )
        form.addRow("Name *", self.name_input)

        self.cmd_input = QLineEdit(command)
        self.cmd_input.setPlaceholderText("e.g. df -h")
        form.addRow("Command *", self.cmd_input)

        self.cat_combo = QComboBox()
        self.cat_combo.addItems(CATEGORIES)
        if category in CATEGORIES:
            self.cat_combo.setCurrentText(category)
        form.addRow("Category", self.cat_combo)

        self.desc_input = QTextEdit(description)
        self.desc_input.setPlaceholderText(
            "Optional description..."
        )
        self.desc_input.setFixedHeight(80)
        form.addRow("Description", self.desc_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Save).setStyleSheet(
            "background-color:#a6e3a1;color:#1e1e2e;"
            "font-weight:bold;padding:6px 18px;"
            "border-radius:6px;"
        )
        buttons.button(QDialogButtonBox.Cancel).setStyleSheet(
            "background-color:#313244;color:#cdd6f4;"
            "padding:6px 18px;border-radius:6px;"
        )
        layout.addWidget(buttons)

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self, "Validation", "Name is required."
            )
            return
        if not self.cmd_input.text().strip():
            QMessageBox.warning(
                self, "Validation", "Command is required."
            )
            return
        self.accept()

    def get_data(self):
        return {
            "name":        self.name_input.text().strip(),
            "command":     self.cmd_input.text().strip(),
            "category":    self.cat_combo.currentText(),
            "description": self.desc_input.toPlainText().strip()
        }

###############################################################
# MAIN WINDOW
###############################################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setMinimumSize(1200, 750)

        if os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))

        # state
        self.chat_history     = []
        self.command_history  = []
        self.last_ai_command  = ""
        self.current_model    = DEFAULT_MODEL
        self.ai_worker        = None
        self.cmd_worker       = None
        self.is_thinking      = False
        self._streaming_text  = ""

        self.current_font_size = self.load_font_size()
        self.load_history()
        self.setup_toolbar()
        self.setup_ui()
        self.setup_statusbar()
        self.init_favorites_db()

        QTimer.singleShot(300, self.show_welcome)

    # ── KEYBOARD SHORTCUTS ────────────────────────────────
    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() in (Qt.Key_Equal, Qt.Key_Plus):
                self.increase_font()
            elif event.key() == Qt.Key_Minus:
                self.decrease_font()
            elif event.key() == Qt.Key_0:
                self.reset_font()
        super().keyPressEvent(event)

    # ── FAVORITES DB ──────────────────────────────────────
    def init_favorites_db(self):
        self.fav_db = FavoritesDB()
        self.refresh_favorites()

    def refresh_favorites(self, rows=None):
        self.fav_list.clear()
        if rows is None:
            rows = self.fav_db.get_all()
        for row in rows:
            fav_id, name, command, category, desc, created = row
            item = QListWidgetItem(
                f"[{category}]  {name}  —  {command}"
            )
            item.setToolTip(
                f"Command:  {command}\n"
                f"Category: {category}\n"
                f"Desc:     {desc}\n"
                f"Saved:    {created}"
            )
            item.setData(Qt.UserRole, {
                "id":          fav_id,
                "name":        name,
                "command":     command,
                "category":    category,
                "description": desc
            })
            self.fav_list.addItem(item)

    def search_favorites(self, keyword):
        rows = (self.fav_db.search(keyword)
                if keyword.strip()
                else self.fav_db.get_all())
        self.refresh_favorites(rows)

    def filter_favorites_by_category(self, category):
        if category == "All Categories":
            self.refresh_favorites()
            return
        rows = [r for r in self.fav_db.get_all()
                if r[3] == category]
        self.refresh_favorites(rows)

    def add_favorite_dialog(self, command=""):
        dlg = FavoriteDialog(self, command=command)
        if dlg.exec_() == QDialog.Accepted:
            d = dlg.get_data()
            self.fav_db.add(
                d["name"], d["command"],
                d["category"], d["description"]
            )
            self.refresh_favorites()
            self.update_status(f"Saved: {d['name']}")

    def edit_favorite(self):
        item = self.fav_list.currentItem()
        if not item:
            QMessageBox.information(
                self, "Edit",
                "Please select a favorite to edit."
            )
            return
        d   = item.data(Qt.UserRole)
        dlg = FavoriteDialog(
            self, name=d["name"], command=d["command"],
            category=d["category"],
            description=d["description"]
        )
        if dlg.exec_() == QDialog.Accepted:
            u = dlg.get_data()
            self.fav_db.update(
                d["id"], u["name"], u["command"],
                u["category"], u["description"]
            )
            self.refresh_favorites()
            self.update_status(f"Updated: {u['name']}")

    def delete_favorite(self):
        item = self.fav_list.currentItem()
        if not item:
            return
        d = item.data(Qt.UserRole)
        if QMessageBox.question(
            self, "Delete", f"Delete '{d['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            self.fav_db.delete(d["id"])
            self.refresh_favorites()
            self.update_status(f"Deleted: {d['name']}")

    def run_favorite(self, item):
        if not item:
            return
        d = item.data(Qt.UserRole)
        if d:
            self.cmd_input.setText(d["command"])
            self.execute_command(d["command"])

    def save_history_to_favorites(self):
        item = self.history_list.currentItem()
        if not item:
            QMessageBox.information(
                self, "Save",
                "Please select a history item first."
            )
            return
        dlg = FavoriteDialog(self, command=item.text())
        if dlg.exec_() == QDialog.Accepted:
            d = dlg.get_data()
            self.fav_db.add(
                d["name"], d["command"],
                d["category"], d["description"]
            )
            self.refresh_favorites()
            self.update_status(f"Saved: {d['name']}")

    def export_favorites(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Favorites",
            "favorites_export.json",
            "JSON Files (*.json)"
        )
        if path:
            self.fav_db.export_json(path)
            self.update_status(f"Exported: {path}")

    def import_favorites(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Favorites", "",
            "JSON Files (*.json)"
        )
        if path:
            try:
                self.fav_db.import_json(path)
                self.refresh_favorites()
                self.update_status(f"Imported: {path}")
            except Exception as e:
                QMessageBox.warning(
                    self, "Import Error", str(e)
                )

    def save_last_to_favorites(self):
        if self.last_ai_command:
            self.add_favorite_dialog(
                command=self.last_ai_command
            )

    # ── FONT CONTROLS ─────────────────────────────────────
    def increase_font(self):
        if self.current_font_size < MAX_FONT_SIZE:
            self.current_font_size += 1
            self.apply_font_size()

    def decrease_font(self):
        if self.current_font_size > MIN_FONT_SIZE:
            self.current_font_size -= 1
            self.apply_font_size()

    def reset_font(self):
        self.current_font_size = DEFAULT_FONT_SIZE
        self.apply_font_size()

    def apply_font_size(self):
        fs   = self.current_font_size
        font = QFont("Consolas", fs)
        self.font_size_label.setText(f"  {fs}  ")
        self.chat_display.setFont(font)
        self.terminal_output.setFont(font)
        self.chat_input.setFont(font)
        self.cmd_input.setFont(font)
        self.history_list.setFont(font)

        updated = re.sub(
            r'(QWidget\s*\{[^}]*font-size:\s*)\d+(px)',
            lambda m: f'{m.group(1)}{fs}{m.group(2)}',
            DARK_THEME
        )
        QApplication.instance().setStyleSheet(updated)
        self.save_font_size()
        self.update_status(f"Font size: {fs}px")

    def save_font_size(self):
        try:
            s = {}
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE) as f:
                    s = json.load(f)
            s["font_size"] = self.current_font_size
            with open(SETTINGS_FILE, "w") as f:
                json.dump(s, f, indent=2)
        except:
            pass

    def load_font_size(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE) as f:
                    s = json.load(f)
                    return int(
                        s.get("font_size", DEFAULT_FONT_SIZE)
                    )
        except:
            pass
        return DEFAULT_FONT_SIZE

    # ── TOOLBAR ───────────────────────────────────────────
    def setup_toolbar(self):
        tb = QToolBar()
        tb.setMovable(False)
        tb.setIconSize(QSize(18, 18))
        self.addToolBar(tb)

        lbl = QLabel(f"  {APP_NAME}  ")
        lbl.setObjectName("label_title")
        tb.addWidget(lbl)
        tb.addSeparator()

        lbl2 = QLabel("  Model: ")
        lbl2.setStyleSheet("color:#6c7086;font-size:12px;")
        tb.addWidget(lbl2)

        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "llama3","llama3.2","mistral",
            "codellama","gemma2","phi3"
        ])
        self.model_combo.setCurrentText(DEFAULT_MODEL)
        self.model_combo.currentTextChanged.connect(
            self.change_model
        )
        tb.addWidget(self.model_combo)
        tb.addSeparator()

        lbl_font = QLabel("  Font: ")
        lbl_font.setStyleSheet("color:#6c7086;font-size:12px;")
        tb.addWidget(lbl_font)

        _btn_style = """
            QPushButton {
                background-color:#313244; color:#cdd6f4;
                border-radius:6px; font-size:12px;
                font-weight:bold; padding:4px 6px;
            }
            QPushButton:hover { background-color:#45475a; }
        """
        self.btn_font_down = QPushButton("A−")
        self.btn_font_down.setFixedWidth(42)
        self.btn_font_down.setStyleSheet(_btn_style)
        self.btn_font_down.clicked.connect(self.decrease_font)
        tb.addWidget(self.btn_font_down)

        self.font_size_label = QLabel(
            f"  {self.current_font_size}  "
        )
        self.font_size_label.setStyleSheet(
            "color:#f9e2af;font-size:13px;"
            "font-weight:bold;min-width:30px;"
        )
        self.font_size_label.setAlignment(Qt.AlignCenter)
        tb.addWidget(self.font_size_label)

        self.btn_font_up = QPushButton("A+")
        self.btn_font_up.setFixedWidth(42)
        self.btn_font_up.setStyleSheet(_btn_style)
        self.btn_font_up.clicked.connect(self.increase_font)
        tb.addWidget(self.btn_font_up)

        self.btn_font_reset = QPushButton("↺")
        self.btn_font_reset.setFixedWidth(32)
        self.btn_font_reset.setStyleSheet(_btn_style)
        self.btn_font_reset.clicked.connect(self.reset_font)
        tb.addWidget(self.btn_font_reset)

        tb.addSeparator()

        act_clear = QAction("🗑 Clear Chat", self)
        act_clear.triggered.connect(self.clear_chat)
        tb.addAction(act_clear)

        act_save = QAction("💾 Save Chat", self)
        act_save.triggered.connect(self.save_chat)
        tb.addAction(act_save)

        act_about = QAction("ℹ About", self)
        act_about.triggered.connect(self.show_about)
        tb.addAction(act_about)

    # ── MAIN UI ───────────────────────────────────────────
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        splitter = QSplitter(Qt.Horizontal)

        # ── LEFT — CHAT ───────────────────────────────────
        left_panel  = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 4, 0)
        left_layout.setSpacing(6)

        lbl_chat = QLabel("💬  AI ASSISTANT CHAT")
        lbl_chat.setObjectName("label_section")
        left_layout.addWidget(lbl_chat)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        left_layout.addWidget(self.chat_display)

        self.thinking_label = QLabel("")
        self.thinking_label.setStyleSheet(
            "color:#f9e2af;font-size:12px;padding:2px;"
        )
        left_layout.addWidget(self.thinking_label)

        input_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText(
            "Ask about any Linux command..."
        )
        self.chat_input.returnPressed.connect(
            self.send_message
        )
        input_row.addWidget(self.chat_input)

        self.btn_send = QPushButton("⮕ Send")
        self.btn_send.setObjectName("btn_send")
        self.btn_send.clicked.connect(self.send_message)
        self.btn_send.setFixedWidth(90)
        input_row.addWidget(self.btn_send)
        left_layout.addLayout(input_row)

        action_row = QHBoxLayout()

        self.btn_run_last = QPushButton("▶ Run Last Command")
        self.btn_run_last.setObjectName("btn_run")
        self.btn_run_last.clicked.connect(self.run_last_command)
        action_row.addWidget(self.btn_run_last)

        self.btn_copy_last = QPushButton("⎘ Copy Command")
        self.btn_copy_last.setObjectName("btn_copy")
        self.btn_copy_last.clicked.connect(
            self.copy_last_command
        )
        action_row.addWidget(self.btn_copy_last)

        self.btn_clear_chat = QPushButton("✕ Clear Chat")
        self.btn_clear_chat.setObjectName("btn_clear")
        self.btn_clear_chat.clicked.connect(self.clear_chat)
        action_row.addWidget(self.btn_clear_chat)

        left_layout.addLayout(action_row)

        # ── RIGHT — TERMINAL + TABS ───────────────────────
        right_panel  = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 0, 0, 0)
        right_layout.setSpacing(6)

        right_splitter = QSplitter(Qt.Vertical)

        # Terminal widget
        terminal_widget = QWidget()
        terminal_layout = QVBoxLayout(terminal_widget)
        terminal_layout.setContentsMargins(0, 0, 0, 0)
        terminal_layout.setSpacing(4)

        lbl_term = QLabel("💻  TERMINAL OUTPUT")
        lbl_term.setObjectName("label_section")
        terminal_layout.addWidget(lbl_term)

        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet(
            "background-color:#0d0d0d;"
            "color:#00ff99;"
            "font-family:Consolas,monospace;"
            "font-size:13px;"
            "border:1px solid #313244;"
            "border-radius:8px;padding:8px;"
        )
        terminal_layout.addWidget(self.terminal_output)
        self.highlighter = BashHighlighter(
            self.terminal_output.document()
        )

        run_row = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText(
            "Enter Linux command to run directly..."
        )
        self.cmd_input.returnPressed.connect(
            self.run_direct_command
        )
        run_row.addWidget(self.cmd_input)

        self.btn_run_direct = QPushButton("▶ Run")
        self.btn_run_direct.setObjectName("btn_run")
        self.btn_run_direct.clicked.connect(
            self.run_direct_command
        )
        self.btn_run_direct.setFixedWidth(80)
        run_row.addWidget(self.btn_run_direct)

        self.btn_clear_term = QPushButton("✕ Clear")
        self.btn_clear_term.setObjectName("btn_clear")
        self.btn_clear_term.clicked.connect(
            self.clear_terminal
        )
        self.btn_clear_term.setFixedWidth(80)
        run_row.addWidget(self.btn_clear_term)
        terminal_layout.addLayout(run_row)

        # Bottom tabs
        bottom_tabs = QTabWidget()

        # Favorites tab
        fav_widget = QWidget()
        fav_layout = QVBoxLayout(fav_widget)
        fav_layout.setContentsMargins(6, 6, 6, 6)
        fav_layout.setSpacing(4)

        fav_search_row = QHBoxLayout()
        self.fav_search = QLineEdit()
        self.fav_search.setPlaceholderText(
            "🔍 Search favorites..."
        )
        self.fav_search.textChanged.connect(
            self.search_favorites
        )
        fav_search_row.addWidget(self.fav_search)

        self.fav_cat_filter = QComboBox()
        self.fav_cat_filter.addItem("All Categories")
        self.fav_cat_filter.addItems(CATEGORIES)
        self.fav_cat_filter.currentTextChanged.connect(
            self.filter_favorites_by_category
        )
        self.fav_cat_filter.setFixedWidth(130)
        fav_search_row.addWidget(self.fav_cat_filter)
        fav_layout.addLayout(fav_search_row)

        self.fav_list = QListWidget()
        self.fav_list.setAlternatingRowColors(True)
        self.fav_list.setStyleSheet("""
            QListWidget {
                background:#181825; color:#cdd6f4;
                border:1px solid #313244;
                border-radius:6px;
                alternate-background-color:#1e1e2e;
            }
            QListWidget::item { padding:6px 8px; }
            QListWidget::item:hover {
                background:#313244; color:#f9e2af;
            }
            QListWidget::item:selected {
                background:#45475a; color:#cdd6f4;
            }
        """)
        self.fav_list.itemDoubleClicked.connect(
            self.run_favorite
        )
        fav_layout.addWidget(self.fav_list)

        fav_btn_row = QHBoxLayout()
        for label, obj, slot in [
            ("⭐ Add",    "btn_run",   self.add_favorite_dialog),
            ("▶ Run",    "btn_run",   lambda: self.run_favorite(self.fav_list.currentItem())),
            ("✏ Edit",   "btn_copy",  self.edit_favorite),
            ("🗑 Delete", "btn_clear", self.delete_favorite),
        ]:
            b = QPushButton(label)
            b.setObjectName(obj)
            b.clicked.connect(slot)
            fav_btn_row.addWidget(b)
        fav_layout.addLayout(fav_btn_row)

        fav_io_row = QHBoxLayout()
        for label, slot in [
            ("⬆ Export JSON", self.export_favorites),
            ("⬇ Import JSON", self.import_favorites),
        ]:
            b = QPushButton(label)
            b.setStyleSheet(
                "background:#313244;color:#cdd6f4;"
                "border-radius:6px;padding:4px 10px;"
            )
            b.clicked.connect(slot)
            fav_io_row.addWidget(b)
        fav_layout.addLayout(fav_io_row)

        # History tab
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(6, 6, 6, 6)
        history_layout.setSpacing(4)

        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(
            self.load_history_item
        )
        history_layout.addWidget(self.history_list)

        hist_btn_row = QHBoxLayout()
        btn_use = QPushButton("▶ Use")
        btn_use.setObjectName("btn_run")
        btn_use.clicked.connect(
            lambda: self.load_history_item(
                self.history_list.currentItem()
            )
        )
        hist_btn_row.addWidget(btn_use)

        btn_save_h = QPushButton("⭐ Save to Favorites")
        btn_save_h.setObjectName("btn_copy")
        btn_save_h.clicked.connect(
            self.save_history_to_favorites
        )
        hist_btn_row.addWidget(btn_save_h)

        self.btn_clear_history = QPushButton("✕ Clear")
        self.btn_clear_history.setObjectName("btn_clear")
        self.btn_clear_history.clicked.connect(
            self.clear_history
        )
        hist_btn_row.addWidget(self.btn_clear_history)
        history_layout.addLayout(hist_btn_row)

        bottom_tabs.addTab(fav_widget,     "⭐  Favorites")
        bottom_tabs.addTab(history_widget, "📋  History")

        right_splitter.addWidget(terminal_widget)
        right_splitter.addWidget(bottom_tabs)
        right_splitter.setSizes([450, 280])
        right_layout.addWidget(right_splitter)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 600])
        main_layout.addWidget(splitter)

    # ── STATUS BAR ────────────────────────────────────────
    def setup_statusbar(self):
        self.status_bar   = QStatusBar()
        self.status_label = QLabel(
            f"  Ready  |  Model: {self.current_model}"
        )
        self.status_bar.addWidget(self.status_label)
        self.setStatusBar(self.status_bar)

    # ── WELCOME ───────────────────────────────────────────
    def show_welcome(self):
        self.apply_font_size()
        self.append_chat_message("assistant", (
            "**Welcome to AI Linux Command Assistant!**\n\n"
            "I can help you with:\n"
            "- 🔍 Finding the right Linux commands\n"
            "- 📊 System monitoring and diagnostics\n"
            "- 🧪 Running tests and benchmarks\n"
            "- 🛠 Debugging and troubleshooting\n"
            "- 📁 File and permission management\n"
            "- 🌐 Network diagnostics\n\n"
            "Try asking:\n"
            "*\"How do I check disk usage?\"*\n"
            "*\"Monitor CPU usage in real time\"*"
        ))

    # ── SEND MESSAGE ──────────────────────────────────────
    def send_message(self):
        user_text = self.chat_input.text().strip()
        if not user_text or self.is_thinking:
            return

        self.chat_input.clear()
        self.append_chat_message("user", user_text)
        self.chat_history.append({
            "role": "user", "content": user_text
        })

        self.is_thinking = True
        self.btn_send.setEnabled(False)
        self.btn_send.setText("...")
        self.thinking_label.setText("⟳  AI is thinking...")
        self.update_status("AI is generating response...")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + self.chat_history[-12:]

        self.ai_worker = OllamaWorker(
            self.current_model, messages
        )
        self.ai_worker.response_chunk.connect(
            self.on_ai_chunk
        )
        self.ai_worker.response_done.connect(
            self.on_ai_done
        )
        self.ai_worker.error_signal.connect(
            self.on_ai_error
        )
        self.ai_worker.start()
        self._streaming_text = ""

    def on_ai_chunk(self, chunk):
        self._streaming_text += chunk

    def on_ai_done(self, full_response):
        self.is_thinking = False
        self.btn_send.setEnabled(True)
        self.btn_send.setText("⮕ Send")
        self.thinking_label.setText("")

        self.append_chat_message("assistant", full_response)
        self.chat_history.append({
            "role": "assistant", "content": full_response
        })

        commands = self.extract_commands(full_response)
        if commands:
            self.last_ai_command = commands[0]
            self.cmd_input.setText(commands[0])
            short = (commands[0][:50] + "..."
                     if len(commands[0]) > 50
                     else commands[0])
            self.update_status(
                f"Ready  |  Command ready: {short}"
            )
        else:
            self.update_status("Ready  |  Response received")

        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)

    def on_ai_error(self, error):
        self.is_thinking = False
        self.btn_send.setEnabled(True)
        self.btn_send.setText("⮕ Send")
        self.thinking_label.setText("")
        self.append_chat_message(
            "system",
            f"⚠️ Ollama Error: {error}\n\n"
            "Make sure Ollama is running:\n"
            "```bash\nollama serve\n```"
        )
        self.update_status(f"Error: {error}")

    # ── EXTRACT COMMANDS ──────────────────────────────────
    def extract_commands(self, text):
        blocks = re.findall(
            r'```(?:bash|sh)?\n?(.*?)```',
            text, re.DOTALL
        )
        commands = []
        for block in blocks:
            lines = [
                l.strip()
                for l in block.strip().splitlines()
                if l.strip() and not l.strip().startswith('#')
            ]
            commands.extend(lines)
        return commands

    # ── RUN COMMANDS ──────────────────────────────────────
    def run_last_command(self):
        if not self.last_ai_command:
            self.append_terminal(
                "⚠ No command to run yet.\n", error=True
            )
            return
        self.execute_command(self.last_ai_command)

    def copy_last_command(self):
        if not self.last_ai_command:
            return
        QApplication.clipboard().setText(self.last_ai_command)
        self.update_status(f"Copied: {self.last_ai_command}")

    def run_direct_command(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
        self.execute_command(cmd)
        self.cmd_input.clear()

    def execute_command(self, command):
        dangerous = [
            "rm -rf /", "mkfs",
            "> /dev/sda", "dd if="
        ]
        for d in dangerous:
            if d in command:
                self.append_terminal(
                    f"⛔ BLOCKED: '{command}' "
                    f"is potentially destructive.\n",
                    error=True
                )
                return

        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.append_terminal(
            f"\n[{ts}] $ {command}\n", header=True
        )
        self.update_status(f"Running: {command}")
        self.btn_run_direct.setEnabled(False)
        self.btn_run_last.setEnabled(False)

        self.cmd_worker = CommandRunner(command)
        self.cmd_worker.output_signal.connect(
            lambda t: self.append_terminal(t)
        )
        self.cmd_worker.error_signal.connect(
            lambda t: self.append_terminal(t, error=True)
        )
        self.cmd_worker.done_signal.connect(
            self.on_command_done
        )
        self.cmd_worker.start()

        if command not in self.command_history:
            self.command_history.insert(0, command)
            self.history_list.insertItem(0, command)
        self.save_history()

    def on_command_done(self, returncode, elapsed):
        self.btn_run_direct.setEnabled(True)
        self.btn_run_last.setEnabled(True)
        icon = "✔" if returncode == 0 else "✖"
        self.append_terminal(
            f"\n{icon} Exit: {returncode}"
            f"  |  Time: {elapsed:.2f}s\n",
            error=(returncode != 0)
        )
        self.update_status(
            f"Done  |  Exit: {returncode}"
            f"  |  Time: {elapsed:.2f}s"
        )
        cursor = self.terminal_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.terminal_output.setTextCursor(cursor)

    # ── TERMINAL APPEND ───────────────────────────────────
    def append_terminal(self, text,
                        error=False, header=False):
        cursor = self.terminal_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        fmt = QTextCharFormat()
        if header:
            fmt.setForeground(QColor("#89b4fa"))
            fmt.setFontWeight(QFont.Bold)
        elif error:
            fmt.setForeground(QColor("#f38ba8"))
        else:
            fmt.setForeground(QColor("#a6e3a1"))
        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        self.terminal_output.setTextCursor(cursor)

    # ── CHAT APPEND ───────────────────────────────────────
    def append_chat_message(self, role, message):
        ts  = datetime.datetime.now().strftime("%H:%M:%S")
        html = format_chat_html(role, message, ts)
        self.chat_display.append(html)
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)

    # ── CLEAR ─────────────────────────────────────────────
    def clear_chat(self):
        self.chat_display.clear()
        self.chat_history = []
        self.show_welcome()

    def clear_terminal(self):
        self.terminal_output.clear()

    def clear_history(self):
        self.command_history = []
        self.history_list.clear()
        self.save_history()

    def load_history_item(self, item):
        if item:
            self.cmd_input.setText(item.text())

    def change_model(self, model):
        self.current_model = model
        self.update_status(f"Model changed to: {model}")

    def update_status(self, msg):
        self.status_label.setText(
            f"  {msg}  |  Model: {self.current_model}"
        )

    # ── HISTORY SAVE/LOAD ─────────────────────────────────
    def save_history(self):
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(
                    self.command_history[:100], f, indent=2
                )
        except:
            pass

    def load_history(self):
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE) as f:
                    self.command_history = json.load(f)
        except:
            self.command_history = []

    def refresh_history_list(self):
        self.history_list.clear()
        for cmd in self.command_history:
            self.history_list.addItem(cmd)

    # ── SAVE CHAT ─────────────────────────────────────────
    def save_chat(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Chat", "chat_log.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if path:
            try:
                with open(path, "w") as f:
                    for msg in self.chat_history:
                        f.write(
                            f"[{msg['role'].upper()}]\n"
                            f"{msg['content']}\n\n"
                        )
                self.update_status(f"Saved: {path}")
            except Exception as e:
                self.update_status(f"Save error: {e}")

    # ── ABOUT ─────────────────────────────────────────────
    def show_about(self):
        QMessageBox.information(
            self, "About",
            f"<h2>{APP_NAME}</h2>"
            f"<p>Version: {VERSION}</p>"
            "<p>AI-powered Linux command assistant<br>"
            "using Ollama LLM for local inference.</p>"
            "<p>Built with Python + PyQt5 + Ollama</p>"
        )

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_history_list()

###############################################################
# ENTRY POINT
###############################################################
def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    if os.path.exists("icon.ico"):
        app.setWindowIcon(QIcon("icon.ico"))

    app.setStyleSheet(DARK_THEME)

    # ── STEP 1: CHECK LICENSE ─────────────────────────────
    from license_manager import check_license
    licensed, _ = check_license()

    if not licensed:
        lic_dialog = LicenseDialog()
        lic_dialog.show()
        accepted = [False]
        lic_dialog.license_accepted.connect(
            lambda: accepted.__setitem__(0, True)
        )
        while not accepted[0]:
            QApplication.processEvents()
            time.sleep(0.05)
        lic_dialog.close()

    # ── STEP 2: SHOW SPLASH + START OLLAMA ───────────────
    splash = SplashScreen()
    splash.show()
    QApplication.processEvents()

    startup_done  = [False]
    startup_ok    = [True]
    startup_error = [""]

    def on_status(text):
        splash.set_status(text)

    def on_finished(success, error):
        startup_done[0]  = True
        startup_ok[0]    = success
        startup_error[0] = error

    worker = StartupWorker()
    worker.status_update.connect(on_status)
    worker.finished.connect(on_finished)
    worker.start()

    while not startup_done[0]:
        QApplication.processEvents()
        time.sleep(0.05)

    splash.close()

    # ── STEP 3: CHECK STARTUP RESULT ─────────────────────
    if not startup_ok[0]:
        QMessageBox.critical(
            None, "Startup Error",
            f"Failed to start:\n\n{startup_error[0]}"
        )
        sys.exit(1)

    # ── STEP 4: LAUNCH MAIN WINDOW ───────────────────────
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
