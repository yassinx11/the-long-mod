#!/usr/bin/env python3
"""
TLD Workshop Rework - Python Port
Original Java app by werwolf2303 / KolbenLP
Python port using PySide6

Game: The Long Drive
"""

import sys
import os
import json
import threading
import shutil
import time
import tempfile
import zipfile
from pathlib import Path
from io import BytesIO

import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QScrollArea,
    QFrame, QStackedWidget, QProgressBar, QSpinBox, QCheckBox,
    QMessageBox, QTextEdit, QSplitter, QFileDialog, QSpacerItem,
    QSizePolicy, QGridLayout
)
from PySide6.QtCore import (
    Qt, Signal, QObject, QThread, QTimer, QSize, QRunnable,
    QThreadPool, Slot, QPropertyAnimation, QEasingCurve, QRect
)
from PySide6.QtGui import (
    QPixmap, QPainter, QColor, QFont, QFontDatabase,
    QLinearGradient, QPen, QBrush, QIcon, QPalette,
    QCursor, QImage
)

# ─── Constants ───────────────────────────────────────────────────────────────

REPOSITORY_URL      = "https://kolbenlp.gitlab.io/WorkshopTLDMods"
MODLIST_JSON        = f"{REPOSITORY_URL}/modlist_3.json"
MODPACK_JSON        = "https://gitlab.com/KolbenLP/WorkshopTLDMods/-/raw/WorkshopDatabase8.6/Modpacks/modlist_3.json"
TLD_PATCHER_URL     = "https://gitlab.com/KolbenLP/WorkshopTLDMods/-/raw/WorkshopDatabase8.6/Workshop/TLDPatcher.zip"
TLD_LOADER_URL      = "https://gitlab.com/KolbenLP/WorkshopTLDMods/-/raw/WorkshopDatabase8.6/Workshop/TLDLoader.dll"
CONFIG_FILE         = "config.tldwr"
MODS_STORE_FILE     = "mods.tldwr"
APP_VERSION         = "1.0.0-py"

# ─── Dark gaming aesthetic palette ──────────────────────────────────────────

STYLE = """
QMainWindow, QWidget {
    background-color: #0d0f14;
    color: #c8ccd4;
}

/* ── Sidebar nav ── */
#sidebar {
    background: #111318;
    border-right: 1px solid #1e2230;
    min-width: 56px;
    max-width: 56px;
}

/* ── Nav buttons ── */
#navBtn {
    background: transparent;
    border: none;
    border-radius: 8px;
    color: #4a5068;
    font-size: 20px;
    padding: 10px 8px;
    min-height: 44px;
    min-width: 44px;
}
#navBtn:hover {
    background: #1a1e2a;
    color: #7c8bba;
}
#navBtn[active="true"] {
    background: #1d2135;
    color: #5b7cf6;
    border-left: 2px solid #5b7cf6;
}

/* ── Top bar ── */
#topBar {
    background: #111318;
    border-bottom: 1px solid #1e2230;
    padding: 0 16px;
    min-height: 52px;
    max-height: 52px;
}
#pageTitle {
    font-size: 15px;
    font-weight: 700;
    color: #e2e6f3;
    letter-spacing: 0.03em;
}

/* ── Search ── */
#searchBox {
    background: #191d28;
    border: 1px solid #252a3a;
    border-radius: 8px;
    color: #c8ccd4;
    font-size: 13px;
    padding: 6px 12px;
    min-width: 220px;
}
#searchBox:focus {
    border-color: #3a4870;
    background: #1d2133;
}

/* ── Category combo ── */
QComboBox {
    background: #191d28;
    border: 1px solid #252a3a;
    border-radius: 8px;
    color: #c8ccd4;
    font-size: 12px;
    padding: 5px 10px;
    min-width: 130px;
}
QComboBox:hover { border-color: #3a4870; }
QComboBox::drop-down { border: none; width: 18px; }
QComboBox QAbstractItemView {
    background: #191d28;
    border: 1px solid #252a3a;
    color: #c8ccd4;
    selection-background-color: #1d2d54;
}

/* ── Mod card ── */
#modCard {
    background: #131720;
    border: 1px solid #1a1f2e;
    border-radius: 10px;
    margin: 4px;
}
#modCard:hover {
    border-color: #2d3553;
    background: #161b27;
}
#modCard[selected="true"] {
    border-color: #5b7cf6;
    background: #141a2e;
}
#modCardName {
    font-size: 13px;
    font-weight: 600;
    color: #d8ddf0;
}
#modCardMeta {
    font-size: 11px;
    color: #4e5675;
}
#modCardAuthor {
    font-size: 11px;
    color: #5b7cf6;
}
#categoryTag {
    background: #1a2040;
    border-radius: 4px;
    color: #5b7cf6;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 7px;
}
#installedBadge {
    background: #0e2a1a;
    border-radius: 4px;
    color: #3dd68c;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 7px;
}
#updateBadge {
    background: #2a1a00;
    border-radius: 4px;
    color: #f0a030;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 7px;
}

/* ── Detail panel ── */
#detailPanel {
    background: #111318;
    border-left: 1px solid #1e2230;
    min-width: 300px;
    max-width: 360px;
}
#detailTitle {
    font-size: 17px;
    font-weight: 700;
    color: #e2e6f3;
}
#detailAuthor { font-size: 12px; color: #5b7cf6; }
#detailDate   { font-size: 11px; color: #3a4060; }
#detailDesc {
    background: #0d0f14;
    border: 1px solid #1a1f2e;
    border-radius: 8px;
    color: #8a90a8;
    font-size: 12px;
    padding: 10px;
}

/* ── Buttons ── */
#primaryBtn {
    background: #3a54d4;
    border: none;
    border-radius: 8px;
    color: #ffffff;
    font-size: 13px;
    font-weight: 600;
    padding: 9px 22px;
}
#primaryBtn:hover   { background: #4a66e8; }
#primaryBtn:pressed { background: #2e44b8; }
#primaryBtn:disabled { background: #1a2048; color: #3a4060; }

#secondaryBtn {
    background: #191d28;
    border: 1px solid #252a3a;
    border-radius: 8px;
    color: #8a90b8;
    font-size: 13px;
    padding: 9px 22px;
}
#secondaryBtn:hover   { border-color: #3a4870; color: #c0c8e8; }
#secondaryBtn:pressed { background: #141720; }

#dangerBtn {
    background: #3a1515;
    border: 1px solid #5a2020;
    border-radius: 8px;
    color: #e05050;
    font-size: 13px;
    padding: 9px 22px;
}
#dangerBtn:hover { background: #4a1c1c; border-color: #703030; }

/* ── Progress bar ── */
QProgressBar {
    background: #191d28;
    border: 1px solid #1e2230;
    border-radius: 5px;
    text-align: center;
    color: #6070a0;
    font-size: 11px;
    height: 10px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3a54d4, stop:1 #5b7cf6);
    border-radius: 5px;
}

/* ── Scroll area ── */
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical {
    background: #0d0f14;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #252a3a;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #3a4060; }
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; }

/* ── Settings ── */
#sectionLabel {
    font-size: 11px;
    font-weight: 700;
    color: #3a4060;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
#settingRow {
    background: #131720;
    border: 1px solid #1a1f2e;
    border-radius: 8px;
    padding: 2px;
}
QCheckBox {
    color: #8a90b8;
    font-size: 13px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #252a3a;
    border-radius: 4px;
    background: #191d28;
}
QCheckBox::indicator:checked {
    background: #3a54d4;
    border-color: #3a54d4;
}
QSpinBox {
    background: #191d28;
    border: 1px solid #252a3a;
    border-radius: 6px;
    color: #c8ccd4;
    font-size: 13px;
    padding: 4px 8px;
}
QLabel#infoLabel { font-size: 12px; color: #5a6080; }

/* ── Pagination ── */
#pageLabel { font-size: 12px; color: #4e5675; }
#pageBtn {
    background: #191d28;
    border: 1px solid #1a1f2e;
    border-radius: 6px;
    color: #5b7cf6;
    font-size: 14px;
    padding: 4px 12px;
    min-width: 30px;
}
#pageBtn:hover   { background: #1d2133; border-color: #2d3553; }
#pageBtn:disabled { color: #252a3a; border-color: #141720; }

/* ── Empty state ── */
#emptyMsg {
    color: #2a2f42;
    font-size: 14px;
    font-weight: 600;
}
"""

# ─── Config ──────────────────────────────────────────────────────────────────

class Config:
    DEFAULTS = {
        "checkformodupdates": True,
        "numberofmodsperpage": 12,
        "tld_path": "",
        "steam_path": "",
    }

    def __init__(self, path: str = CONFIG_FILE):
        self._path = path
        self._data: dict = {}
        self._load()

    def _load(self):
        self._data = dict(self.DEFAULTS)
        if os.path.exists(self._path):
            try:
                with open(self._path) as f:
                    self._data.update(json.load(f))
            except Exception:
                pass

    def save(self):
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key, fallback=None):
        return self._data.get(key, fallback)

    def set(self, key, value):
        self._data[key] = value

# ─── Mod model ───────────────────────────────────────────────────────────────

class Mod:
    __slots__ = ("name", "version", "description", "date",
                 "link", "picture_link", "file_name",
                 "category", "changelog", "author")

    def __init__(self, d: dict):
        self.name         = d.get("Name", "")
        self.version      = d.get("Version", "")
        self.description  = d.get("Description", "")
        self.date         = d.get("Date", "")
        self.link         = d.get("Link", "")
        self.picture_link = d.get("PictureLink", "")
        self.file_name    = d.get("FileName", "")
        self.category     = d.get("Category", "Uncategorized")
        self.changelog    = d.get("Changelog", "")
        self.author       = d.get("Author", "Unknown")

# ─── Workshop API ─────────────────────────────────────────────────────────────

class WorkshopAPI:
    def __init__(self, config: Config):
        self.config = config
        self._mods_cache: list[Mod] = []
        self._installed: dict[str, str] = {}  # filename -> version
        self._load_installed()

    def _load_installed(self):
        if os.path.exists(MODS_STORE_FILE):
            try:
                with open(MODS_STORE_FILE) as f:
                    self._installed = json.load(f)
            except Exception:
                self._installed = {}

    def _resolve_tld_path(self) -> str:
        tld_path = self.config.get("tld_path", "")
        if tld_path:
            return os.path.abspath(os.path.expanduser(tld_path))

        home = os.path.expanduser("~")
        candidates = [
            os.path.join(home, ".steam", "steam", "steamapps", "common", "The Long Drive"),
            os.path.join(home, ".local", "share", "Steam", "steamapps", "common", "The Long Drive"),
        ]
        for candidate in candidates:
            if os.path.isdir(candidate):
                return candidate

        return os.path.abspath(".")

    def _mods_dir(self) -> str:
        return os.path.join(self._resolve_tld_path(), "Mods")

    def _normalize_installed_entry(self, mod: Mod) -> dict:
        raw = self._installed.get(mod.file_name, {})
        if isinstance(raw, str):
            return {"version": raw, "install_path": "", "archive": mod.file_name}
        if isinstance(raw, dict):
            return {
                "version": raw.get("version", ""),
                "install_path": raw.get("install_path", ""),
                "archive": raw.get("archive", mod.file_name),
            }
        return {"version": "", "install_path": "", "archive": mod.file_name}

    def ensure_loader(self) -> None:
        tld_root = self._resolve_tld_path()
        mods_dir = os.path.join(tld_root, "Mods")
        melon_dir = os.path.join(tld_root, "MelonLoader")
        os.makedirs(mods_dir, exist_ok=True)
        os.makedirs(melon_dir, exist_ok=True)

        loader_path = os.path.join(tld_root, "TLDLoader.dll")
        if os.path.exists(loader_path):
            return

        response = requests.get(TLD_LOADER_URL, timeout=30)
        response.raise_for_status()
        with open(loader_path, "wb") as f:
            f.write(response.content)

    def _extract_archive(self, archive_path: str, mod: Mod) -> str:
        mods_dir = self._mods_dir()
        tld_root = self._resolve_tld_path()
        os.makedirs(mods_dir, exist_ok=True)

        with zipfile.ZipFile(archive_path, "r") as zf:
            members = [name for name in zf.namelist() if name and not name.endswith("/")]
            if not members:
                raise ValueError(f"Archive for '{mod.name}' is empty.")

            top_levels = {name.split("/", 1)[0] for name in members if "/" in name}
            has_root_files = any("/" not in name for name in members)

            if any(name.startswith("Mods/") or name.startswith("MelonLoader/") for name in members):
                zf.extractall(tld_root)
                return os.path.join(mods_dir, mod.name)

            if len(top_levels) == 1 and not has_root_files:
                top = next(iter(top_levels))
                if top.lower() in {"mods", "melonloader"}:
                    zf.extractall(tld_root)
                    return os.path.join(mods_dir, mod.name)
                zf.extractall(mods_dir)
                return os.path.join(mods_dir, top)

            target = os.path.join(mods_dir, mod.name)
            if os.path.isdir(target):
                shutil.rmtree(target)
            os.makedirs(target, exist_ok=True)
            zf.extractall(target)
            return target

    def _save_installed(self):
        with open(MODS_STORE_FILE, "w") as f:
            json.dump(self._installed, f, indent=2)

    def fetch_mods(self) -> list[Mod]:
        resp = requests.get(MODLIST_JSON, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        # JSON structure: {"modlist": [...]} — root object with "modlist" array
        if isinstance(data, dict):
            raw_list = data.get("modlist", data.get("mods", data.get("Mods", [])))
        elif isinstance(data, list):
            raw_list = data
        else:
            raw_list = []
        self._mods_cache = [Mod(d) for d in raw_list if isinstance(d, dict)]
        return self._mods_cache

    def get_cached_mods(self) -> list[Mod]:
        return self._mods_cache

    def get_categories(self) -> list[str]:
        cats = sorted({m.category for m in self._mods_cache})
        return ["All"] + cats

    def is_installed(self, mod: Mod) -> bool:
        return mod.file_name in self._installed

    def installed_version(self, mod: Mod) -> str:
        return self._normalize_installed_entry(mod).get("version", "")

    def has_update(self, mod: Mod) -> bool:
        iv = self.installed_version(mod)
        return iv != "" and iv != mod.version

    def get_installed_mods(self) -> list[Mod]:
        return [m for m in self._mods_cache if self.is_installed(m)]

    def get_mods_with_updates(self) -> list[Mod]:
        return [m for m in self._mods_cache if self.has_update(m)]

    def download(self, mod: Mod, progress_cb=None) -> None:
        self.ensure_loader()

        with tempfile.NamedTemporaryFile(prefix="tlm_", suffix=".zip", delete=False) as tmp:
            dest = tmp.name

        with requests.get(mod.link, stream=True, timeout=30) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            done = 0
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    done += len(chunk)
                    if progress_cb and total:
                        progress_cb(int(done * 100 / total))

        install_path = self._extract_archive(dest, mod)
        os.remove(dest)

        self._installed[mod.file_name] = {
            "version": mod.version,
            "install_path": install_path,
            "archive": mod.file_name,
        }
        self._save_installed()

    def uninstall(self, mod: Mod) -> None:
        entry = self._normalize_installed_entry(mod)
        install_path = entry.get("install_path", "")
        if install_path and os.path.exists(install_path):
            if os.path.isdir(install_path):
                shutil.rmtree(install_path)
            else:
                os.remove(install_path)

        legacy_archive = os.path.join(self._mods_dir(), mod.file_name)
        if os.path.exists(legacy_archive):
            os.remove(legacy_archive)

        self._installed.pop(mod.file_name, None)
        self._save_installed()

# ─── Worker signals ───────────────────────────────────────────────────────────

class WorkerSignals(QObject):
    finished  = Signal(object)
    error     = Signal(str)
    progress  = Signal(int)

class FetchWorker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))

# ─── Mod Card ─────────────────────────────────────────────────────────────────

class ModCard(QFrame):
    clicked = Signal(object)   # emits Mod

    def __init__(self, mod: Mod, api: WorkshopAPI, parent=None):
        super().__init__(parent)
        self.mod = mod
        self.api = api
        self.setObjectName("modCard")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._build()

    def _build(self):
        self.setFixedHeight(82)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(3)

        # Top row: name + badge
        top = QHBoxLayout()
        top.setSpacing(6)
        name = QLabel(self.mod.name)
        name.setObjectName("modCardName")
        name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # elide long names
        fm = name.fontMetrics()
        elided = fm.elidedText(self.mod.name, Qt.ElideRight, 200)
        name.setText(elided)
        top.addWidget(name, 1)

        if self.api.has_update(self.mod):
            b = QLabel("UPDATE")
            b.setObjectName("updateBadge")
            top.addWidget(b)
        elif self.api.is_installed(self.mod):
            b = QLabel("✓")
            b.setObjectName("installedBadge")
            top.addWidget(b)

        layout.addLayout(top)

        # Author
        author = QLabel(f"by {self.mod.author}")
        author.setObjectName("modCardAuthor")
        layout.addWidget(author)

        # Bottom row: category + version + date
        bot = QHBoxLayout()
        bot.setSpacing(6)
        cat = QLabel(self.mod.category)
        cat.setObjectName("categoryTag")
        bot.addWidget(cat)
        bot.addStretch()
        ver = QLabel(f"v{self.mod.version}")
        ver.setObjectName("modCardMeta")
        bot.addWidget(ver)
        date = QLabel(self.mod.date)
        date.setObjectName("modCardMeta")
        bot.addWidget(date)
        layout.addLayout(bot)

    def set_selected(self, v: bool):
        self.setProperty("selected", "true" if v else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.mod)
        super().mousePressEvent(e)

# ─── Detail Panel ─────────────────────────────────────────────────────────────

class DetailPanel(QWidget):
    download_requested = Signal(object)   # Mod
    uninstall_requested = Signal(object)  # Mod

    def __init__(self, api: WorkshopAPI, parent=None):
        super().__init__(parent)
        self.api = api
        self.setObjectName("detailPanel")
        self._mod: Mod | None = None
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        scroll.setWidget(inner)
        outer.addWidget(scroll)

        self._image = QLabel()
        self._image.setFixedHeight(140)
        self._image.setAlignment(Qt.AlignCenter)
        self._image.setStyleSheet(
            "background:#131720;border-radius:8px;border:1px solid #1a1f2e;"
        )
        layout.addWidget(self._image)

        self._title = QLabel()
        self._title.setObjectName("detailTitle")
        self._title.setWordWrap(True)
        layout.addWidget(self._title)

        self._author = QLabel()
        self._author.setObjectName("detailAuthor")
        layout.addWidget(self._author)

        self._date = QLabel()
        self._date.setObjectName("detailDate")
        layout.addWidget(self._date)

        ver_row = QHBoxLayout()
        self._ver = QLabel()
        self._ver.setObjectName("modCardMeta")
        ver_row.addWidget(self._ver)
        ver_row.addStretch()
        self._cat = QLabel()
        self._cat.setObjectName("categoryTag")
        ver_row.addWidget(self._cat)
        layout.addLayout(ver_row)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#1a1f2e;")
        layout.addWidget(sep)

        desc_lbl = QLabel("Description")
        desc_lbl.setObjectName("sectionLabel")
        layout.addWidget(desc_lbl)

        self._desc = QTextEdit()
        self._desc.setObjectName("detailDesc")
        self._desc.setReadOnly(True)
        self._desc.setFixedHeight(100)
        layout.addWidget(self._desc)

        clog_lbl = QLabel("Changelog")
        clog_lbl.setObjectName("sectionLabel")
        layout.addWidget(clog_lbl)

        self._changelog = QTextEdit()
        self._changelog.setObjectName("detailDesc")
        self._changelog.setReadOnly(True)
        self._changelog.setFixedHeight(80)
        layout.addWidget(self._changelog)

        layout.addStretch()

        self._progress = QProgressBar()
        self._progress.hide()
        layout.addWidget(self._progress)

        self._status_lbl = QLabel()
        self._status_lbl.setObjectName("modCardMeta")
        self._status_lbl.hide()
        layout.addWidget(self._status_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self._dl_btn = QPushButton("Download")
        self._dl_btn.setObjectName("primaryBtn")
        self._dl_btn.clicked.connect(self._on_download)
        btn_row.addWidget(self._dl_btn)

        self._uninst_btn = QPushButton("Uninstall")
        self._uninst_btn.setObjectName("dangerBtn")
        self._uninst_btn.clicked.connect(self._on_uninstall)
        btn_row.addWidget(self._uninst_btn)
        layout.addLayout(btn_row)

        self._update_btns()

    def _update_btns(self):
        if self._mod is None:
            self._dl_btn.setEnabled(False)
            self._uninst_btn.hide()
            return
        installed = self.api.is_installed(self._mod)
        has_upd   = self.api.has_update(self._mod)
        self._dl_btn.setEnabled(True)
        self._dl_btn.setText("Update" if has_upd else ("Re-download" if installed else "Download"))
        if installed:
            self._uninst_btn.show()
        else:
            self._uninst_btn.hide()

    def show_mod(self, mod: Mod):
        self._mod = mod
        self._title.setText(mod.name)
        self._author.setText(f"by {mod.author}")
        self._date.setText(mod.date)
        self._ver.setText(f"v{mod.version}")
        self._cat.setText(mod.category)
        self._desc.setPlainText(mod.description or "(No description)")
        self._changelog.setPlainText(mod.changelog or "(No changelog)")
        self._image.setText("Loading image…")
        self._progress.hide()
        self._status_lbl.hide()
        self._update_btns()

        if mod.picture_link:
            worker = FetchWorker(self._fetch_image, mod.picture_link)
            worker.signals.finished.connect(self._set_image)
            QThreadPool.globalInstance().start(worker)

    def _fetch_image(self, url: str):
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.content

    def _set_image(self, data: bytes):
        pix = QPixmap()
        pix.loadFromData(data)
        if not pix.isNull():
            pix = pix.scaled(self._image.width(), self._image.height(),
                             Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._image.setPixmap(pix)
        self._image.setAlignment(Qt.AlignCenter)

    def _on_download(self):
        if self._mod:
            self.download_requested.emit(self._mod)

    def _on_uninstall(self):
        if self._mod:
            self.uninstall_requested.emit(self._mod)

    def set_downloading(self, v: bool, pct: int = 0):
        if v:
            self._progress.setValue(pct)
            self._progress.show()
            self._dl_btn.setEnabled(False)
            self._status_lbl.setText("Downloading…")
            self._status_lbl.show()
        else:
            self._progress.hide()
            self._status_lbl.hide()
            self._dl_btn.setEnabled(True)
            self._update_btns()

# ─── Workshop Page ────────────────────────────────────────────────────────────

class WorkshopPage(QWidget):
    def __init__(self, api: WorkshopAPI, parent=None):
        super().__init__(parent)
        self.api = api
        self._all_mods: list[Mod] = []
        self._filtered: list[Mod] = []
        self._selected: Mod | None = None
        self._selected_card: ModCard | None = None
        self._page = 0
        self._per_page = 12
        self._cards: list[ModCard] = []
        self._pool = QThreadPool.globalInstance()
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left: mod grid
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(12, 12, 12, 12)
        lv.setSpacing(8)

        # Controls bar
        ctrl = QHBoxLayout()
        ctrl.setSpacing(8)

        self._search = QLineEdit()
        self._search.setObjectName("searchBox")
        self._search.setPlaceholderText("Search mods…")
        self._search.textChanged.connect(self._apply_filter)
        ctrl.addWidget(self._search)

        self._cat_combo = QComboBox()
        self._cat_combo.addItem("All")
        self._cat_combo.currentTextChanged.connect(self._apply_filter)
        ctrl.addWidget(self._cat_combo)

        ctrl.addStretch()

        self._refresh_btn = QPushButton("⟳  Refresh")
        self._refresh_btn.setObjectName("secondaryBtn")
        self._refresh_btn.clicked.connect(self.load_mods)
        ctrl.addWidget(self._refresh_btn)

        lv.addLayout(ctrl)

        # Scroll area for cards
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._grid_widget = QWidget()
        self._grid_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(6)
        self._grid.setContentsMargins(4, 4, 4, 4)
        self._grid.setAlignment(Qt.AlignTop)
        self._scroll.setWidget(self._grid_widget)
        lv.addWidget(self._scroll)

        # Pagination
        pag = QHBoxLayout()
        pag.setSpacing(8)
        self._prev_btn = QPushButton("‹")
        self._prev_btn.setObjectName("pageBtn")
        self._prev_btn.clicked.connect(self._prev_page)
        pag.addWidget(self._prev_btn)

        self._page_lbl = QLabel("Page 1")
        self._page_lbl.setObjectName("pageLabel")
        pag.addWidget(self._page_lbl)

        self._next_btn = QPushButton("›")
        self._next_btn.setObjectName("pageBtn")
        self._next_btn.clicked.connect(self._next_page)
        pag.addWidget(self._next_btn)
        pag.addStretch()

        per_page_lbl = QLabel("Per page:")
        per_page_lbl.setObjectName("pageLabel")
        pag.addWidget(per_page_lbl)

        self._per_page_spin = QSpinBox()
        self._per_page_spin.setRange(4, 48)
        self._per_page_spin.setValue(self._per_page)
        self._per_page_spin.valueChanged.connect(self._on_per_page_changed)
        pag.addWidget(self._per_page_spin)

        lv.addLayout(pag)
        root.addWidget(left, 1)

        # Right: detail panel
        self._detail = DetailPanel(self.api)
        self._detail.download_requested.connect(self._do_download)
        self._detail.uninstall_requested.connect(self._do_uninstall)
        root.addWidget(self._detail)

    def load_mods(self):
        self._refresh_btn.setEnabled(False)
        self._refresh_btn.setText("Loading…")
        self._clear_grid()

        empty = QLabel("Loading mods from workshop…")
        empty.setObjectName("emptyMsg")
        empty.setAlignment(Qt.AlignCenter)
        self._grid.addWidget(empty, 0, 0)

        worker = FetchWorker(self.api.fetch_mods)
        worker.signals.finished.connect(self._on_mods_loaded)
        worker.signals.error.connect(self._on_load_error)
        self._pool.start(worker)

    def _on_mods_loaded(self, mods: list[Mod]):
        self._all_mods = mods
        cats = self.api.get_categories()
        self._cat_combo.blockSignals(True)
        self._cat_combo.clear()
        for c in cats:
            self._cat_combo.addItem(c)
        self._cat_combo.blockSignals(False)
        self._apply_filter()
        self._refresh_btn.setEnabled(True)
        self._refresh_btn.setText("⟳  Refresh")

    def _on_load_error(self, err: str):
        self._clear_grid()
        lbl = QLabel(f"Failed to load mods:\n{err}")
        lbl.setObjectName("emptyMsg")
        lbl.setAlignment(Qt.AlignCenter)
        self._grid.addWidget(lbl, 0, 0)
        self._refresh_btn.setEnabled(True)
        self._refresh_btn.setText("⟳  Refresh")

    def _apply_filter(self):
        query = self._search.text().lower()
        cat   = self._cat_combo.currentText()
        self._filtered = [
            m for m in self._all_mods
            if (cat == "All" or m.category == cat)
            and (not query or query in m.name.lower()
                           or query in m.author.lower()
                           or query in m.description.lower())
        ]
        self._page = 0
        self._render_page()

    def _render_page(self):
        self._clear_grid()
        start = self._page * self._per_page
        page_mods = self._filtered[start : start + self._per_page]

        if not page_mods:
            lbl = QLabel("No mods found.")
            lbl.setObjectName("emptyMsg")
            lbl.setAlignment(Qt.AlignCenter)
            self._grid.addWidget(lbl, 0, 0, 1, 2)
        else:
            cols = 2
            for i, mod in enumerate(page_mods):
                card = ModCard(mod, self.api)
                card.clicked.connect(self._select_mod)
                self._grid.addWidget(card, i // cols, i % cols)
                self._cards.append(card)

        total = max(1, (len(self._filtered) + self._per_page - 1) // self._per_page)
        self._page_lbl.setText(f"Page {self._page + 1} / {total}")
        self._prev_btn.setEnabled(self._page > 0)
        self._next_btn.setEnabled(self._page < total - 1)

    def _clear_grid(self):
        self._cards.clear()
        self._selected_card = None  # widget is about to be deleted by Qt
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _select_mod(self, mod: Mod):
        if self._selected_card is not None:
            try:
                self._selected_card.set_selected(False)
            except RuntimeError:
                pass  # C++ object already deleted
            self._selected_card = None
        self._selected = mod
        for card in self._cards:
            if card.mod is mod:
                card.set_selected(True)
                self._selected_card = card
                break
        self._detail.show_mod(mod)

    def _prev_page(self):
        self._page -= 1
        self._render_page()
        self._scroll.verticalScrollBar().setValue(0)

    def _next_page(self):
        self._page += 1
        self._render_page()
        self._scroll.verticalScrollBar().setValue(0)

    def _on_per_page_changed(self, v: int):
        self._per_page = v
        self._page = 0
        self._render_page()

    def _do_download(self, mod: Mod):
        self._detail.set_downloading(True)

        def do():
            def prog(pct):
                self._detail.set_downloading(True, pct)
            self.api.download(mod, progress_cb=prog)

        worker = FetchWorker(do)
        worker.signals.finished.connect(lambda _: self._on_download_done(mod))
        worker.signals.error.connect(self._on_download_error)
        self._pool.start(worker)

    def _on_download_done(self, mod: Mod):
        self._detail.set_downloading(False)
        self._detail.show_mod(mod)
        self._render_page()

    def _on_download_error(self, err: str):
        self._detail.set_downloading(False)
        QMessageBox.critical(self, "Download Failed", f"Failed to download mod:\n{err}")

    def _do_uninstall(self, mod: Mod):
        reply = QMessageBox.question(
            self, "Uninstall Mod",
            f"Are you sure you want to uninstall «{mod.name}»?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.api.uninstall(mod)
            self._detail.show_mod(mod)
            self._render_page()

    def refresh_cards(self):
        self._render_page()

# ─── My Mods Page ─────────────────────────────────────────────────────────────

class MyModsPage(QWidget):
    def __init__(self, api: WorkshopAPI, parent=None):
        super().__init__(parent)
        self.api = api
        self._cards: list[ModCard] = []
        self._page = 0
        self._per_page = 12
        self._pool = QThreadPool.globalInstance()
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(12, 12, 12, 12)
        lv.setSpacing(8)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(8)
        ctrl.addStretch()
        self._open_folder_btn = QPushButton("📂  Open Mods Folder")
        self._open_folder_btn.setObjectName("secondaryBtn")
        self._open_folder_btn.clicked.connect(self._open_folder)
        ctrl.addWidget(self._open_folder_btn)

        self._del_btn = QPushButton("🗑  Delete Selected")
        self._del_btn.setObjectName("dangerBtn")
        self._del_btn.clicked.connect(self._delete_selected)
        ctrl.addWidget(self._del_btn)
        lv.addLayout(ctrl)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._gw = QWidget()
        self._gw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._grid = QGridLayout(self._gw)
        self._grid.setSpacing(6)
        self._grid.setContentsMargins(4, 4, 4, 4)
        self._grid.setAlignment(Qt.AlignTop)
        self._scroll.setWidget(self._gw)
        lv.addWidget(self._scroll)

        pag = QHBoxLayout()
        pag.setSpacing(8)
        self._prev_btn = QPushButton("‹")
        self._prev_btn.setObjectName("pageBtn")
        self._prev_btn.clicked.connect(self._prev_page)
        pag.addWidget(self._prev_btn)
        self._page_lbl = QLabel("Page 1")
        self._page_lbl.setObjectName("pageLabel")
        pag.addWidget(self._page_lbl)
        self._next_btn = QPushButton("›")
        self._next_btn.setObjectName("pageBtn")
        self._next_btn.clicked.connect(self._next_page)
        pag.addWidget(self._next_btn)
        pag.addStretch()
        lv.addLayout(pag)
        root.addWidget(left, 1)

        self._detail = DetailPanel(self.api)
        self._detail.download_requested.connect(self._re_download)
        self._detail.uninstall_requested.connect(self._uninstall)
        root.addWidget(self._detail)

        self._selected: Mod | None = None
        self._selected_card: ModCard | None = None

    def refresh(self):
        self._page = 0
        self._render()

    def _render(self):
        self._cards.clear()
        self._selected_card = None  # widgets being deleted
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        installed = self.api.get_installed_mods()
        start = self._page * self._per_page
        page_mods = installed[start : start + self._per_page]

        if not page_mods:
            lbl = QLabel("No installed mods.\nHead to the Workshop to download some!")
            lbl.setObjectName("emptyMsg")
            lbl.setAlignment(Qt.AlignCenter)
            self._grid.addWidget(lbl, 0, 0, 1, 2)
        else:
            cols = 2
            for i, mod in enumerate(page_mods):
                card = ModCard(mod, self.api)
                card.clicked.connect(self._select)
                self._grid.addWidget(card, i // cols, i % cols)
                self._cards.append(card)

        total = max(1, (len(installed) + self._per_page - 1) // self._per_page)
        self._page_lbl.setText(f"Page {self._page + 1} / {total}")
        self._prev_btn.setEnabled(self._page > 0)
        self._next_btn.setEnabled(self._page < total - 1)

    def _select(self, mod: Mod):
        if self._selected_card is not None:
            try:
                self._selected_card.set_selected(False)
            except RuntimeError:
                pass
            self._selected_card = None
        self._selected = mod
        for card in self._cards:
            if card.mod is mod:
                card.set_selected(True)
                self._selected_card = card
                break
        self._detail.show_mod(mod)

    def _delete_selected(self):
        if not self._selected:
            return
        reply = QMessageBox.question(
            self, "Delete Mod",
            f"Uninstall «{self._selected.name}»?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.api.uninstall(self._selected)
            self._selected = None
            self._selected_card = None
            self.refresh()

    def _open_folder(self):
        tld_path = self.api.config.get("tld_path", "")
        folder = os.path.join(tld_path, "Mods") if tld_path else os.path.abspath("Mods")
        os.makedirs(folder, exist_ok=True)
        QMessageBox.information(self, "Mods Folder", f"Mods are located at:\n{folder}")

    def _re_download(self, mod: Mod):
        worker = FetchWorker(self.api.download, mod)
        worker.signals.finished.connect(lambda _: self.refresh())
        worker.signals.error.connect(
            lambda e: QMessageBox.critical(self, "Error", e)
        )
        self._pool.start(worker)

    def _uninstall(self, mod: Mod):
        self.api.uninstall(mod)
        self.refresh()

    def _prev_page(self):
        self._page -= 1
        self._render()

    def _next_page(self):
        self._page += 1
        self._render()

# ─── Settings Page ────────────────────────────────────────────────────────────

class SettingsPage(QWidget):
    def __init__(self, api: WorkshopAPI, parent=None):
        super().__init__(parent)
        self.api = api
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # ── Info section ──
        info_sec = QLabel("INFORMATION")
        info_sec.setObjectName("sectionLabel")
        layout.addWidget(info_sec)

        self._info_frame = QFrame()
        self._info_frame.setObjectName("settingRow")
        info_lv = QVBoxLayout(self._info_frame)
        info_lv.setContentsMargins(16, 12, 16, 12)
        info_lv.setSpacing(4)
        self._total_lbl = QLabel("Total mods on Workshop: —")
        self._total_lbl.setObjectName("infoLabel")
        info_lv.addWidget(self._total_lbl)
        self._inst_lbl = QLabel("Installed mods: —")
        self._inst_lbl.setObjectName("infoLabel")
        info_lv.addWidget(self._inst_lbl)
        self._upd_lbl = QLabel("Mods with updates: —")
        self._upd_lbl.setObjectName("infoLabel")
        info_lv.addWidget(self._upd_lbl)
        layout.addWidget(self._info_frame)

        # ── Workshop settings ──
        ws_sec = QLabel("WORKSHOP")
        ws_sec.setObjectName("sectionLabel")
        layout.addWidget(ws_sec)

        ws_frame = QFrame()
        ws_frame.setObjectName("settingRow")
        ws_lv = QVBoxLayout(ws_frame)
        ws_lv.setContentsMargins(16, 12, 16, 12)
        ws_lv.setSpacing(10)

        self._check_updates_cb = QCheckBox("Check for mod updates on startup")
        self._check_updates_cb.setChecked(
            self.api.config.get("checkformodupdates", True)
        )
        ws_lv.addWidget(self._check_updates_cb)

        per_row = QHBoxLayout()
        per_lbl = QLabel("Default mods per page:")
        per_lbl.setObjectName("infoLabel")
        per_row.addWidget(per_lbl)
        per_row.addStretch()
        self._per_page_spin = QSpinBox()
        self._per_page_spin.setRange(4, 48)
        self._per_page_spin.setValue(
            self.api.config.get("numberofmodsperpage", 12)
        )
        per_row.addWidget(self._per_page_spin)
        ws_lv.addLayout(per_row)
        layout.addWidget(ws_frame)

        # ── Game path ──
        path_sec = QLabel("GAME PATH")
        path_sec.setObjectName("sectionLabel")
        layout.addWidget(path_sec)

        path_frame = QFrame()
        path_frame.setObjectName("settingRow")
        path_lv = QVBoxLayout(path_frame)
        path_lv.setContentsMargins(16, 12, 16, 12)
        path_lv.setSpacing(8)

        tld_row = QHBoxLayout()
        tld_lbl = QLabel("TLD Path:")
        tld_lbl.setObjectName("infoLabel")
        tld_lbl.setFixedWidth(80)
        tld_row.addWidget(tld_lbl)
        self._tld_path = QLineEdit()
        self._tld_path.setObjectName("searchBox")
        self._tld_path.setText(self.api.config.get("tld_path", ""))
        self._tld_path.setPlaceholderText("Path to The Long Drive…")
        tld_row.addWidget(self._tld_path, 1)
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondaryBtn")
        browse_btn.clicked.connect(self._browse_tld)
        tld_row.addWidget(browse_btn)
        path_lv.addLayout(tld_row)
        layout.addWidget(path_frame)

        # ── Advanced ──
        adv_sec = QLabel("ADVANCED")
        adv_sec.setObjectName("sectionLabel")
        layout.addWidget(adv_sec)

        adv_frame = QFrame()
        adv_frame.setObjectName("settingRow")
        adv_lv = QHBoxLayout(adv_frame)
        adv_lv.setContentsMargins(16, 12, 16, 12)

        self._uninst_all_btn = QPushButton("Uninstall All Mods")
        self._uninst_all_btn.setObjectName("dangerBtn")
        self._uninst_all_btn.clicked.connect(self._uninstall_all)
        adv_lv.addWidget(self._uninst_all_btn)
        adv_lv.addStretch()
        layout.addWidget(adv_frame)

        layout.addStretch()

        # Save
        save_row = QHBoxLayout()
        save_row.addStretch()
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save)
        save_row.addWidget(save_btn)
        layout.addLayout(save_row)

        note = QLabel("Changes to per-page count will take effect on next page load.")
        note.setObjectName("modCardMeta")
        layout.addWidget(note)

    def refresh_info(self):
        total = len(self.api.get_cached_mods())
        inst  = len(self.api.get_installed_mods())
        upd   = len(self.api.get_mods_with_updates())
        self._total_lbl.setText(f"Total mods on Workshop: {total}")
        self._inst_lbl.setText(f"Installed mods: {inst}")
        self._upd_lbl.setText(f"Mods with updates: {upd}")

    def _browse_tld(self):
        d = QFileDialog.getExistingDirectory(self, "Select The Long Drive folder")
        if d:
            self._tld_path.setText(d)

    def _save(self):
        self.api.config.set("checkformodupdates", self._check_updates_cb.isChecked())
        self.api.config.set("numberofmodsperpage", self._per_page_spin.value())
        self.api.config.set("tld_path", self._tld_path.text())
        self.api.config.save()
        QMessageBox.information(self, "Settings", "Settings saved.")

    def _uninstall_all(self):
        mods = self.api.get_installed_mods()
        if not mods:
            QMessageBox.information(self, "Nothing to do", "No installed mods.")
            return
        reply = QMessageBox.question(
            self, "Uninstall All",
            f"Uninstall all {len(mods)} installed mod(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for m in mods:
                self.api.uninstall(m)
            self.refresh_info()
            QMessageBox.information(self, "Done", "All mods uninstalled.")

# ─── Sidebar button ───────────────────────────────────────────────────────────

class NavBtn(QPushButton):
    def __init__(self, icon: str, tooltip: str, parent=None):
        super().__init__(icon, parent)
        self.setObjectName("navBtn")
        self.setToolTip(tooltip)
        self.setFixedSize(44, 44)
        self.setProperty("active", "false")

    def set_active(self, v: bool):
        self.setProperty("active", "true" if v else "false")
        self.style().unpolish(self)
        self.style().polish(self)

# ─── Main Window ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"TLD Workshop Rework  v{APP_VERSION}")
        self.resize(1100, 700)
        self.setMinimumSize(820, 560)

        self._config = Config()
        self._api    = WorkshopAPI(self._config)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ──
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sv = QVBoxLayout(sidebar)
        sv.setContentsMargins(6, 12, 6, 12)
        sv.setSpacing(6)
        sv.setAlignment(Qt.AlignTop)

        logo = QLabel("🎮")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size:22px;padding:4px;")
        sv.addWidget(logo)
        sv.addSpacing(8)

        self._nav_workshop = NavBtn("🏪", "Workshop")
        self._nav_mymods   = NavBtn("📦", "My Mods")
        self._nav_settings = NavBtn("⚙", "Settings")

        self._nav_btns = [self._nav_workshop, self._nav_mymods, self._nav_settings]
        for btn in self._nav_btns:
            sv.addWidget(btn)
        sv.addStretch()

        self._nav_workshop.clicked.connect(lambda: self._switch(0))
        self._nav_mymods.clicked.connect(lambda: self._switch(1))
        self._nav_settings.clicked.connect(lambda: self._switch(2))

        root.addWidget(sidebar)

        # ── Content area ──
        content_area = QWidget()
        cv = QVBoxLayout(content_area)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(0)

        # Top bar
        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        tb = QHBoxLayout(top_bar)
        tb.setContentsMargins(16, 0, 16, 0)
        self._page_title = QLabel("Workshop")
        self._page_title.setObjectName("pageTitle")
        tb.addWidget(self._page_title)
        tb.addStretch()
        ver_lbl = QLabel(f"v{APP_VERSION}")
        ver_lbl.setObjectName("modCardMeta")
        tb.addWidget(ver_lbl)
        cv.addWidget(top_bar)

        # Stacked pages
        self._stack = QStackedWidget()

        self._workshop_page = WorkshopPage(self._api)
        self._mymods_page   = MyModsPage(self._api)
        self._settings_page = SettingsPage(self._api)

        self._stack.addWidget(self._workshop_page)
        self._stack.addWidget(self._mymods_page)
        self._stack.addWidget(self._settings_page)

        cv.addWidget(self._stack, 1)
        root.addWidget(content_area, 1)

        self._switch(0)
        QTimer.singleShot(200, self._workshop_page.load_mods)

    PAGE_TITLES = ["Workshop", "My Mods", "Settings"]

    def _switch(self, idx: int):
        for i, btn in enumerate(self._nav_btns):
            btn.set_active(i == idx)
        self._stack.setCurrentIndex(idx)
        self._page_title.setText(self.PAGE_TITLES[idx])

        if idx == 1:
            self._mymods_page.refresh()
        elif idx == 2:
            self._settings_page.refresh_info()

# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    app.setApplicationName("TLD Workshop Rework")
    app.setApplicationVersion(APP_VERSION)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
