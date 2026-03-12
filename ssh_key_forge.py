# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import math
import tempfile
from pathlib import Path

from PyQt6.QtCore import Qt, QRect, QUrl, QRectF, QSettings, QProcess, QProcessEnvironment, QTimer
from PyQt6.QtGui import QColor, QPainter, QLinearGradient, QPen, QFont, QPainterPath
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QComboBox,
    QSpinBox,
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QSizePolicy,
    QScrollArea,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QFrame,
)

try:
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
except Exception:
    QMediaPlayer = None
    QAudioOutput = None

APP_BG = QColor(12, 12, 28)
ACCENT = QColor(130, 80, 255)
ACCENT_2 = QColor(56, 122, 255)
TEXT = QColor(230, 234, 255)
MUTED = QColor(150, 160, 190)
ERROR = QColor(255, 120, 140)
SUCCESS = QColor(120, 220, 160)

DEFAULT_SIZE = 726
MAX_SIZE = 900
BUTTON_STYLE = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(90, 80, 255, 220),
        stop:1 rgba(40, 110, 255, 220));
    color: white;
    border: 1px solid rgba(120, 140, 255, 200);
    border-radius: 12px;
    padding: 8px 12px;
    font-weight: 600;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(110, 95, 255, 240),
        stop:1 rgba(60, 130, 255, 240));
}
QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(70, 60, 210, 240),
        stop:1 rgba(30, 90, 210, 240));
}
"""
TRANSLATIONS = {
    "EN": {
        "app_title": "SSH Key Forge",
        "section_gen": "Key generation",
        "section_agent": "SSH agent",
        "agent_key_path_label": "Key path",
        "enable_agent": "Enable ssh-agent",
        "disable_agent": "Disable ssh-agent",
        "section_upload": "Remote connection",
        "section_remote_keys": "Remote keys",
        "language_label": "Language",
        "key_type_label": "Key type",
        "key_bits_label": "Key length (RSA)",
        "comment_label": "Comment",
        "comment_placeholder": "e.g. user@host",
        "passphrase_label": "Passphrase",
        "passphrase_placeholder": "Optional passphrase",
        "path_label": "Save path",
        "browse": "Browse...",
        "reset_default": "Reset default",
        "host_label": "Host / Address",
        "host_placeholder": "e.g. 192.168.0.10",
        "port_label": "Port",
        "user_label": "Login",
        "password_label": "Password",
        "auth_method_label": "Auth method",
        "auth_key_path": "Key path",
        "auth_key_pass": "Key passphrase",
        "auth_password": "Password",
        "auth_key": "Private key",
        "auth_key_passphrase": "Private key + passphrase",
        "auth_agent": "SSH agent",
        "generate_btn": "Generate key",
        "upload_btn": "Upload key",
        "music_toggle": "Background music",
        "instruction_btn": "Instruction",
        "instruction_title": "How to generate SSH keys",
        "instruction_body": "<b>Step-by-step (key generation)</b><br><ul><li>Choose a key type (recommended: ED25519). For RSA, select the key length.</li><li>Optionally set a comment and a passphrase to protect the private key.</li><li>Choose the save path and click Generate key; confirm overwrite if asked.</li><li>If prompts appear (passphrase or overwrite), use the embedded terminal input; Auto-yes can answer y/n prompts.</li><li>After generation, you can automatically add the key to ssh-agent by checking Auto-add generated key to agent.</li></ul><br><b>What the files mean</b><br><ul><li><b>id_ed25519.pub</b> is the public key that you upload to the remote computer (authorized_keys).</li><li><b>id_ed25519</b> (no extension) is the private key kept on your computer for authentication. Never share it.</li></ul><br><b>All application features</b><br><ul><li><b>Key generation</b> for ED25519, RSA, ECDSA, and hardware-backed keys, with optional comment and passphrase.</li><li><b>Auto-add to ssh-agent (Windows)</b> loads the new key into the agent so you can connect without typing the passphrase every time; it enables agent-based logins.</li><li><b>Manual add to ssh-agent (Windows)</b> lets you load any existing private key.</li><li><b>Install/Enable ssh-agent (Windows)</b> and <b>Disable ssh-agent</b> manage the agent service.</li><li><b>Remote connection</b> supports password, private key, private key + passphrase, or ssh-agent authentication.</li><li><b>Upload key</b> appends the public key to authorized_keys on the remote host.</li><li><b>Remote keys</b>: detect keys, remove selected, or replace with the local public key.</li><li><b>Open remote terminal</b> launches an SSH session with the selected auth method.</li><li><b>Embedded terminal</b> handles ssh-keygen/ssh-add prompts directly inside the app.</li><li><b>Language switch</b> and <b>background music</b> toggle.</li></ul>",
        "auto_add_agent": "Auto-add generated key to agent",
        "auto_add_agent_note": "(Windows will remember it)",
        "agent_toggle": "Add key to ssh-agent (Windows)",
        "refresh_local_keys": "Refresh local keys",
        "add_selected_agent": "Add private key to agent",
        "install_agent": "Install/Enable ssh-agent",
        "open_terminal": "Open remote terminal",
        "terminal_label": "Terminal",
        "terminal_input_placeholder": "Type response and press Enter",
        "terminal_send": "Send",
        "auto_yes": "Auto-answer yes",
        "process_running": "Another process is already running.",
        "gen_started": "Key generation started. See terminal.",
        "agent_started": "ssh-add started. See terminal.",
        "no_process": "No active process.",
        "detect_remote": "Detect remote keys",
        "remove_remote": "Remove selected",
        "replace_remote": "Replace with local key",
        "status_ready": "Ready",
        "minimize": "Minimize",
        "maximize": "Maximize",
        "restore": "Restore",
        "close": "Close",
        "file_exists_title": "File exists",
        "file_exists_body": "File already exists. Overwrite?",
        "terminal_overwrite_hint": "If ssh-keygen asks, type y/n in the terminal below.",
        "path_missing": "Provide a key save path.",
        "cancel_gen": "Key generation canceled.",
        "missing_ssh_keygen": "ssh-keygen not found in PATH. Install OpenSSH.",
        "gen_error": "Key generation error.",
        "key_generated": "Key generated: {path} and {pub}",
        "host_login_pass_required": "Provide host, login and SSH password.",
        "auth_required": "Select auth method and fill required fields.",
        "pub_missing": "Public key not found. Generate the key first.",
        "paramiko_missing": "Missing paramiko. Install: pip install paramiko",
        "pub_empty": "Public key file is empty.",
        "upload_ok": "Key uploaded to remote device.",
        "upload_exists": "Key already present in authorized_keys.",
        "ssh_error": "SSH connection error: {err}",
        "music_missing": "bg.mp3 not found next to the app. Music disabled.",
        "music_disabled": "QtMultimedia missing. Music disabled.",
        "agent_added": "Key added to Windows ssh-agent.",
        "remote_shell_opened": "Remote terminal opened in app.",
        "remote_shell_closed": "Remote terminal closed.",
        "agent_prompt": "Opened a console to enter key passphrase for ssh-agent.",
        "agent_missing": "ssh-add not found in PATH. Install OpenSSH Client.",
        "agent_err": "ssh-add error: {err}",
        "agent_windows_only": "ssh-agent is available only on Windows.",
        "agent_install_started": "Installation started (admin window).",
        "agent_install_failed": "Failed to start installer: {err}",
        "agent_no_keys": "No local keys found in ~/.ssh.",
        "agent_none_selected": "Select at least one local key.",
        "remote_keys_loaded": "Remote keys loaded: {count}",
        "remote_keys_removed": "Selected remote keys removed.",
        "remote_keys_replaced": "Remote keys replaced with local key.",
        "remote_keys_none": "No remote keys selected.",
        "remote_keys_empty": "No keys on remote device.",
        "file_dialog_title": "Save key",
        "file_dialog_key": "Select private key",
        "agent_key_passphrase_label": "Agent key passphrase",
        "agent_key_passphrase_placeholder": "Passphrase for key added to agent",
        "agent_key_passphrase_required": "Key requires passphrase, enter it before adding.",
        "agent_passphrase_prompt": "Enter the key passphrase in the input below and press Send (leave empty for none).",
        "agent_passphrase_status": "Passphrase required to add the key to ssh-agent.",
        "agent_passphrase_submitted": "> [passphrase submitted]",
    },
    "PL": {
        "app_title": "SSH Key Forge",
        "section_gen": "Generowanie klucza",
        "section_agent": "SSH agent",
        "agent_key_path_label": "Sciezka klucza",
        "enable_agent": "Wlacz ssh-agent",
        "disable_agent": "Wylacz ssh-agent",
        "section_upload": "Polaczenie zdalne",
        "section_remote_keys": "Klucze na zdalnym",
        "language_label": "Jezyk",
        "key_type_label": "Typ klucza",
        "key_bits_label": "Dlugosc klucza (RSA)",
        "comment_label": "Komentarz",
        "comment_placeholder": "np. user@host",
        "passphrase_label": "Haslo klucza",
        "passphrase_placeholder": "Opcjonalne haslo",
        "path_label": "Sciezka zapisu",
        "browse": "Wybierz...",
        "reset_default": "Przywroc domyslna",
        "host_label": "Adres / Host",
        "host_placeholder": "np. 192.168.0.10",
        "port_label": "Port",
        "user_label": "Login",
        "password_label": "Haslo",
        "auth_method_label": "Metoda logowania",
        "auth_key_path": "Sciezka klucza",
        "auth_key_pass": "Haslo klucza",
        "auth_password": "Haslo",
        "auth_key": "Klucz prywatny",
        "auth_key_passphrase": "Klucz + haslo",
        "auth_agent": "SSH agent",
        "generate_btn": "Generuj klucz",
        "upload_btn": "Wgraj klucz",
        "music_toggle": "Muzyka w tle",
        "instruction_btn": "Instrukcja",
        "instruction_title": "Instrukcja generowania klucza SSH",
        "instruction_body": "<b>Krok po kroku (generowanie klucza)</b><br><ul><li>Wybierz typ klucza (zalecany ED25519). Dla RSA ustaw dlugosc klucza.</li><li>Opcjonalnie ustaw komentarz i haslo (passphrase), aby zabezpieczyc klucz prywatny.</li><li>Wybierz sciezke zapisu i kliknij Generuj klucz; w razie potrzeby potwierdz nadpisanie.</li><li>Gdy pojawiaja sie pytania (haslo lub nadpisanie), uzyj wbudowanego terminala; Auto-yes moze odpowiadac na pytania y/n.</li><li>Po wygenerowaniu mozesz automatycznie dodac klucz do ssh-agent, zaznaczajac Auto-dodaj klucz do agenta.</li></ul><br><b>Znaczenie plikow</b><br><ul><li><b>id_ed25519.pub</b> to klucz publiczny, ktory wgrywasz na zdalny komputer (authorized_keys).</li><li><b>id_ed25519</b> (bez rozszerzenia) to klucz prywatny przechowywany lokalnie do autoryzacji polaczenia. Nie udostepniaj go.</li></ul><b>Wszystkie funkcje aplikacji</b><br><ul><li><b>Generowanie kluczy</b> ED25519, RSA, ECDSA i sprzetowych, z komentarzem i haslem.</li><li><b>Auto-dodanie do ssh-agent (Windows)</b> laduje nowy klucz do agenta, dzieki czemu mozesz laczyc sie bez wpisywania hasla za kazdym razem; umozliwia logowanie przez agenta.</li><li><b>Reczne dodanie do ssh-agent (Windows)</b> pozwala zaladowac dowolny istniejacy klucz prywatny.</li><li><b>Instalacja/Wlaczenie ssh-agent (Windows)</b> oraz <b>Wylaczenie ssh-agent</b> zarzadzaja usluga agenta.</li><li><b>Polaczenie zdalne</b> obsluguje logowanie haslem, kluczem, kluczem + haslem oraz przez ssh-agent.</li><li><b>Wgranie klucza</b> dopisuje klucz publiczny do authorized_keys na zdalnym hoscie.</li><li><b>Klucze zdalne</b>: wykrywanie, usuwanie zaznaczonych, lub zamiana na lokalny klucz.</li><li><b>Otworz terminal zdalny</b> uruchamia sesje SSH z wybrana metoda logowania.</li><li><b>Wbudowany terminal</b> obsluguje pytania ssh-keygen/ssh-add bez opuszczania aplikacji.</li><li><b>Zmiana jezyka</b> i <b>muzyka w tle</b>.</li></ul>",
        "auto_add_agent": "Auto-dodaj klucz do agenta",
        "auto_add_agent_note": "(Windows zapamieta klucz)",
        "agent_toggle": "Dodaj klucz do ssh-agent (Windows)",
        "refresh_local_keys": "Odswiez lokalne klucze",
        "add_selected_agent": "Dodaj klucz prywatny do agenta",
        "install_agent": "Zainstaluj/Wlacz ssh-agent",
        "open_terminal": "Otworz terminal zdalny",
        "terminal_label": "Terminal",
        "terminal_input_placeholder": "Wpisz odpowiedz i Enter",
        "terminal_send": "Wyslij",
        "auto_yes": "Auto-odpowiedz: tak",
        "process_running": "Inny proces juz trwa.",
        "gen_started": "Generowanie uruchomione. Zobacz terminal.",
        "agent_started": "ssh-add uruchomione. Zobacz terminal.",
        "no_process": "Brak aktywnego procesu.",
        "detect_remote": "Wykryj klucze zdalne",
        "remove_remote": "Usun zaznaczone",
        "replace_remote": "Zamien na lokalny",
        "status_ready": "Gotowe",
        "minimize": "Minimalizuj",
        "maximize": "Powieksz",
        "restore": "Przywroc",
        "close": "Zamknij",
        "file_exists_title": "Plik istnieje",
        "file_exists_body": "Plik juz istnieje. Nadpisac?",
        "terminal_overwrite_hint": "Jesli ssh-keygen zapyta o nadpisanie, wpisz y/n w terminalu ponizej.",
        "path_missing": "Podaj sciezke zapisu klucza.",
        "cancel_gen": "Anulowano generowanie klucza.",
        "missing_ssh_keygen": "Brak ssh-keygen w PATH. Zainstaluj OpenSSH.",
        "gen_error": "Blad generowania klucza.",
        "key_generated": "Klucz wygenerowany: {path} i {pub}",
        "host_login_pass_required": "Podaj host, login i haslo SSH.",
        "auth_required": "Wybierz metode logowania i wypelnij pola.",
        "pub_missing": "Nie znaleziono klucza publicznego. Najpierw wygeneruj klucz.",
        "paramiko_missing": "Brak biblioteki paramiko. Zainstaluj: pip install paramiko",
        "pub_empty": "Plik klucza publicznego jest pusty.",
        "upload_ok": "Klucz zostal wgrany na urzadzenie.",
        "upload_exists": "Klucz juz znajduje sie w authorized_keys.",
        "ssh_error": "Blad polaczenia SSH: {err}",
        "music_missing": "Brak pliku bg.mp3 obok programu. Muzyka wylaczona.",
        "music_disabled": "Brak QtMultimedia. Muzyka wylaczona.",
        "agent_added": "Klucz dodany do agenta Windows.",
        "remote_shell_opened": "Terminal zdalny otwarty w aplikacji.",
        "remote_shell_closed": "Terminal zdalny zamkniety.",
        "agent_prompt": "Otworzono konsole do wpisania hasla klucza dla ssh-agent.",
        "agent_missing": "Brak ssh-add w PATH. Zainstaluj OpenSSH Client.",
        "agent_err": "Blad ssh-add: {err}",
        "agent_windows_only": "Dodawanie do ssh-agent jest dostepne tylko w Windows.",
        "agent_install_started": "Uruchomiono instalacje (okno admina).",
        "agent_install_failed": "Nie udalo sie uruchomic instalatora: {err}",
        "agent_no_keys": "Brak lokalnych kluczy w ~/.ssh.",
        "agent_none_selected": "Zaznacz co najmniej jeden klucz.",
        "remote_keys_loaded": "Zaladowano klucze zdalne: {count}",
        "remote_keys_removed": "Usunieto wybrane klucze zdalne.",
        "remote_keys_replaced": "Zamieniono klucze na lokalny klucz.",
        "remote_keys_none": "Brak zaznaczonych kluczy zdalnych.",
        "remote_keys_empty": "Brak kluczy na zdalnym urzadzeniu.",
        "file_dialog_title": "Zapisz klucz",
        "file_dialog_key": "Wybierz klucz prywatny",
        "agent_key_passphrase_label": "Haslo do klucza (agent)",
        "agent_key_passphrase_placeholder": "Haslo do klucza dodawanego do agenta",
        "agent_key_passphrase_required": "Klucz wymaga hasla, podaj je przed dodaniem.",
        "agent_passphrase_prompt": "Wpisz haslo do klucza w polu ponizej i kliknij Wyslij (puste = brak hasla).",
        "agent_passphrase_status": "Wymagane haslo do dodania klucza do ssh-agent.",
        "agent_passphrase_submitted": "> [haslo wyslane]",
    },
}

KEY_TYPE_INFO = {
    "EN": {
        "ed25519": "Strongest, fast and modern.",
        "rsa": "Compatible but larger keys.",
        "ecdsa": "Fast, widely supported.",
        "ed25519-sk": "Hardware-backed (FIDO/U2F).",
        "ecdsa-sk": "Hardware-backed (FIDO/U2F).",
        "dsa": "Deprecated and not recommended.",
        "xmss": "Experimental, very large keys.",
    },
    "PL": {
        "ed25519": "Najmocniejsze szyfrowanie, szybki i nowoczesny.",
        "rsa": "Kompatybilny, ale wiekszy rozmiar klucza.",
        "ecdsa": "Szybki, szeroko wspierany.",
        "ed25519-sk": "Klucz sprzetowy (FIDO/U2F).",
        "ecdsa-sk": "Klucz sprzetowy (FIDO/U2F).",
        "dsa": "Przestarzaly i niezalecany.",
        "xmss": "Eksperymentalny, bardzo duze klucze.",
    },
}


def key_type_items(lang: str):
    if lang == "PL":
        return [
            "ED25519 - najmocniejsze szyfrowanie (nowoczesny)",
            "RSA - kompatybilny, ale wolniejszy",
            "ECDSA - szybki, szeroko wspierany",
            "ED25519-SK - klucz sprzetowy (FIDO)",
            "ECDSA-SK - klucz sprzetowy (FIDO)",
            "XMSS - eksperymentalny (duze klucze)",
            "DSA - przestarzaly (niezalecany)",
        ]
    return [
        "ED25519 - strongest (modern)",
        "RSA - compatible but slower",
        "ECDSA - fast, widely supported",
        "ED25519-SK - hardware key (FIDO)",
        "ECDSA-SK - hardware key (FIDO)",
        "XMSS - experimental (large keys)",
        "DSA - deprecated (not recommended)",
    ]


def default_key_path(key_type: str) -> Path:
    home = Path.home()
    ssh_dir = home / ".ssh"
    name = key_type.lower()
    if name == "ed25519":
        return ssh_dir / "id_ed25519"
    if name == "ed25519-sk":
        return ssh_dir / "id_ed25519_sk"
    if name == "ecdsa":
        return ssh_dir / "id_ecdsa"
    if name == "ecdsa-sk":
        return ssh_dir / "id_ecdsa_sk"
    if name == "dsa":
        return ssh_dir / "id_dsa"
    if name == "xmss":
        return ssh_dir / "id_xmss"
    return ssh_dir / "id_rsa"


def parse_key_type(text: str) -> str:
    return text.split(" - ")[0].strip().lower()


def short_key_label(line: str) -> str:
    parts = line.strip().split()
    if not parts:
        return ""
    key_type = parts[0]
    comment = parts[2] if len(parts) > 2 else ""
    suffix = parts[1][-10:] if len(parts) > 1 else ""
    label = f"{key_type} {comment}".strip()
    if suffix:
        label = f"{label} …{suffix}".strip()
    return label


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
        self._drag_pos = None
        self.setFixedHeight(58)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 10, 18, 6)
        layout.setSpacing(10)

        self.title = QLabel("SSH Key Forge")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: rgb(230,234,255); font-size: 18px; font-weight: 700;")
        layout.addWidget(self.title, 1)

        self.btn_min = QPushButton("-")
        self.btn_max = QPushButton("□")
        self.btn_close = QPushButton("x")

        self.btn_min.setObjectName("title_min")
        self.btn_max.setObjectName("title_max")
        self.btn_close.setObjectName("title_close")

        icon_font = QFont()
        icon_font.setPointSize(11)
        icon_font.setBold(True)
        for btn in (self.btn_min, self.btn_max, self.btn_close):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(30, 30)
            btn.setFont(icon_font)

        self.btn_min.clicked.connect(self._parent.showMinimized)
        self.btn_max.clicked.connect(self._parent.toggle_maximize)
        self.btn_close.clicked.connect(self._parent.close)

        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)

    def set_title(self, text: str):
        self.title.setText(text)

    def set_tooltips(self, min_text: str, max_text: str, close_text: str):
        self.btn_min.setToolTip(min_text)
        self.btn_max.setToolTip(max_text)
        self.btn_close.setToolTip(close_text)

    def set_maximize_tooltip(self, text: str):
        self.btn_max.setToolTip(text)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(6, 6, -6, -6)
        button_area = 3 * 30 + 2 * 10 + 18
        drag_rect = QRectF(rect)
        drag_rect.setRight(rect.right() - button_area)
        if drag_rect.width() <= 40:
            return

        path = QPainterPath()
        path.addRoundedRect(drag_rect, 16, 16)
        painter.setClipPath(path)

        grid_pen = QPen(QColor(120, 140, 255, 35), 1)
        painter.setPen(grid_pen)
        spacing = 14
        w = int(drag_rect.width())
        h = int(drag_rect.height())
        x0 = int(drag_rect.left())
        y0 = int(drag_rect.top())
        for i in range(-h, w, spacing):
            painter.drawLine(x0 + i, y0, x0 + i + h, y0 + h)

        ring_pen = QPen(QColor(90, 120, 255, 55), 1.0)
        painter.setPen(ring_pen)
        inset = 6
        for r in range(4):
            rr = drag_rect.adjusted(inset + r * 6, inset + r * 4, -(inset + r * 6), -(inset + r * 4))
            painter.drawRoundedRect(rr, 12, 12)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            self._parent.set_drag_active(True)
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._parent.move(self._parent.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._parent.set_drag_active(False)
        event.accept()


class BackgroundWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(6, 6, -6, -6)
        radius = 22
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)
        rectf = QRectF(rect)

        gradient = QLinearGradient(rectf.topLeft(), rectf.bottomRight())
        gradient.setColorAt(0.0, QColor(16, 12, 38))
        gradient.setColorAt(0.55, QColor(18, 24, 60))
        gradient.setColorAt(1.0, QColor(12, 10, 26))
        painter.fillPath(path, gradient)

        beam = QLinearGradient(rectf.topLeft(), rectf.bottomRight())
        beam.setColorAt(0.0, QColor(110, 90, 255, 120))
        beam.setColorAt(0.4, QColor(90, 120, 255, 40))
        beam.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillPath(path, beam)

        painter.setClipPath(path)
        line_pen = QPen(QColor(80, 110, 255, 40), 1)
        painter.setPen(line_pen)
        spacing = 24
        w = rect.width()
        h = rect.height()
        for i in range(-h, w, spacing):
            painter.drawLine(rect.left() + i, rect.top(), rect.left() + i + h, rect.bottom())

        painter.setPen(QPen(QColor(90, 90, 140, 140), 1.2))
        painter.drawPath(path)

class InstructionTitleBar(QWidget):
    def __init__(self, parent, title: str):
        super().__init__(parent)
        self._drag_pos = None
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 6)
        layout.setSpacing(8)

        left_spacer = QWidget()
        left_spacer.setFixedWidth(30)
        layout.addWidget(left_spacer, 0)

        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: rgb(230,234,255); font-size: 16px; font-weight: 700;")
        layout.addWidget(self.title, 1)

        self.btn_close = QPushButton("x")
        self.btn_close.setObjectName("title_close")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.clicked.connect(parent.close)
        layout.addWidget(self.btn_close, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(6, 6, -6, -6)
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 14, 14)
        painter.setClipPath(path)

        grid_pen = QPen(QColor(120, 140, 255, 35), 1)
        painter.setPen(grid_pen)
        spacing = 12
        w = rect.width()
        h = rect.height()
        for i in range(-h, w, spacing):
            painter.drawLine(rect.left() + i, rect.top(), rect.left() + i + h, rect.bottom())

        ring_pen = QPen(QColor(90, 120, 255, 55), 1.0)
        painter.setPen(ring_pen)
        inset = 6
        for r in range(3):
            rr = rect.adjusted(inset + r * 5, inset + r * 3, -(inset + r * 5), -(inset + r * 3))
            painter.drawRoundedRect(rr, 10, 10)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.window().move(self.window().pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        event.accept()


class InstructionDialog(QDialog):
    def __init__(self, parent, title: str, body_html: str):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setFixedSize(720, 560)
        if parent is not None:
            self.setStyleSheet(parent.styleSheet())

        container = BackgroundWidget()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.titlebar = InstructionTitleBar(self, title)
        layout.addWidget(self.titlebar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        scroll.viewport().setAutoFillBackground(False)

        content = QWidget()
        content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 6, 8, 10)
        content_layout.setSpacing(6)

        body = QLabel()
        body.setWordWrap(True)
        body.setTextFormat(Qt.TextFormat.RichText)
        body.setText(f"<div style='text-align: justify'>{body_html}</div>")
        body.setAlignment(Qt.AlignmentFlag.AlignTop)
        body.setStyleSheet("color: rgb(210,220,255); font-size: 11px; line-height: 1.35;")
        content_layout.addWidget(body)
        content_layout.addStretch(1)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Kosmo", "SSHKeyForge")
        self.lang = self.settings.value("language", "EN")
        if self.lang not in ("EN", "PL"):
            self.lang = "EN"
        self._saved_key_type = self.settings.value("key_type", "ed25519")

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(DEFAULT_SIZE, DEFAULT_SIZE)
        self._is_maximized = False
        self._drag_active = False
        self._base_size = DEFAULT_SIZE
        self._drag_size = self._base_size

        self._container = BackgroundWidget()
        self._container.setObjectName("container")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._container)

        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self.titlebar = TitleBar(self)
        layout.addWidget(self.titlebar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        scroll.viewport().setAutoFillBackground(False)

        content = QWidget()
        content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(18, 10, 18, 12)
        content_layout.setSpacing(10)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "EN")
        self.lang_combo.addItem("Polski", "PL")
        self.lang_combo.setFixedWidth(160)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)

        self.btn_instruction = QPushButton()
        self.btn_instruction.setObjectName("actionButton")
        self.btn_instruction.clicked.connect(self.show_instructions)

        self.music_toggle = QCheckBox()
        self.music_toggle.setChecked(True)
        self.music_toggle.stateChanged.connect(self.toggle_music)
        self._player = None
        self._audio = None

        self.key_type = QComboBox()
        self.key_type.setMinimumWidth(220)
        self.key_type.currentTextChanged.connect(self.on_key_type_changed)

        self.key_type_desc = QLabel("")
        self.key_type_desc.setWordWrap(True)
        self.key_type_desc.setStyleSheet("color: rgb(140,150,190); font-size: 11px;")

        self.key_bits = QSpinBox()
        self.key_bits.setRange(2048, 8192)
        self.key_bits.setSingleStep(1024)
        self.key_bits.setValue(4096)

        self.comment = QLineEdit()
        self.passphrase = QLineEdit()
        self.passphrase.setEchoMode(QLineEdit.EchoMode.Password)

        self.auto_add_agent = QCheckBox()
        self.auto_add_agent.setChecked(False)

        self.path_edit = QLineEdit()

        self.btn_browse = QPushButton()
        self.btn_browse.setObjectName("actionButton")
        self.btn_reset = QPushButton()
        self.btn_reset.setObjectName("actionButton")
        self.btn_browse.clicked.connect(self.pick_path)
        self.btn_reset.clicked.connect(self.reset_path)

        self.auth_method = QComboBox()
        self.auth_method.currentIndexChanged.connect(self.update_auth_ui)

        self.auth_key_path = QLineEdit()
        self.auth_key_browse = QPushButton()
        self.auth_key_browse.setObjectName("actionButton")
        self.auth_key_browse.clicked.connect(self.pick_auth_key)
        self.auth_key_passphrase = QLineEdit()
        self.auth_key_passphrase.setEchoMode(QLineEdit.EchoMode.Password)

        self.host = QLineEdit()
        self.port = QSpinBox()
        self.port.setRange(1, 65535)
        self.port.setValue(22)
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_generate = QPushButton()
        self.btn_generate.setObjectName("actionButton")
        self.btn_upload = QPushButton()
        self.btn_upload.setObjectName("actionButton")
        self.btn_open_terminal = QPushButton()
        self.btn_open_terminal.setObjectName("actionButton")


        self.btn_generate.clicked.connect(self.generate_key)
        self.btn_upload.clicked.connect(self.upload_key)
        self.btn_open_terminal.clicked.connect(self.open_remote_terminal)

        self.agent_key_path = QLineEdit()
        self.agent_key_browse = QPushButton()
        self.agent_key_browse.setObjectName("actionButton")
        self.agent_key_browse.clicked.connect(self.pick_agent_key)

        self.btn_add_agent = QPushButton()
        self.btn_add_agent.setObjectName("actionButton")
        self.btn_enable_agent = QPushButton()
        self.btn_enable_agent.setObjectName("actionButton")
        self.btn_disable_agent = QPushButton()
        self.btn_disable_agent.setObjectName("actionButton")
        self.btn_add_agent.clicked.connect(lambda: self.add_key_to_agent())
        self.btn_enable_agent.clicked.connect(self.enable_ssh_agent)
        self.btn_disable_agent.clicked.connect(self.disable_ssh_agent)

        self.remote_keys_list = QListWidget()
        self.remote_keys_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.remote_keys_list.setFixedHeight(120)
        self.btn_detect_remote = QPushButton()
        self.btn_detect_remote.setObjectName("actionButton")
        self.btn_remove_remote = QPushButton()
        self.btn_remove_remote.setObjectName("actionButton")
        self.btn_replace_remote = QPushButton()
        self.btn_replace_remote.setObjectName("actionButton")
        self.btn_detect_remote.clicked.connect(self.detect_remote_keys)
        self.btn_remove_remote.clicked.connect(self.remove_remote_keys)
        self.btn_replace_remote.clicked.connect(self.replace_remote_keys)

        self.status = QLabel("")
        self.status.setObjectName("status_label")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.status.setWordWrap(True)

        self.section_gen = self._section_label("")
        self.section_agent = self._section_label("")
        self.section_upload = self._section_label("")
        self.section_remote = self._section_label("")

        self.lbl_language = QLabel("")
        self.lbl_key_type = QLabel("")
        self.lbl_key_bits = QLabel("")
        self.lbl_comment = QLabel("")
        self.lbl_passphrase = QLabel("")
        self.lbl_path = QLabel("")
        self.lbl_host = QLabel("")
        self.lbl_port = QLabel("")
        self.lbl_user = QLabel("")
        self.lbl_password = QLabel("")
        self.lbl_auth_method = QLabel("")
        self.lbl_auth_key_path = QLabel("")
        self.lbl_auth_key_pass = QLabel("")
        self.lbl_agent_key_path = QLabel("")

        self.terminal_label = QLabel("")
        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setObjectName("terminal_output")
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setMaximumBlockCount(1000)
        self.terminal_input = QLineEdit()
        self.terminal_input.setObjectName("terminal_input")
        self.terminal_send = QPushButton()
        self.terminal_send.setObjectName("actionButton")
        self.terminal_send.clicked.connect(self.send_terminal_input)
        self.terminal_input.returnPressed.connect(self.send_terminal_input)
        self.auto_yes = QCheckBox()
        self.auto_yes.setChecked(False)
        for btn in (
            self.btn_instruction,
            self.btn_browse,
            self.btn_reset,
            self.auth_key_browse,
            self.btn_generate,
            self.btn_upload,
            self.btn_open_terminal,
            self.agent_key_browse,
            self.btn_add_agent,
            self.btn_enable_agent,
            self.btn_disable_agent,
            self.btn_detect_remote,
            self.btn_remove_remote,
            self.btn_replace_remote,
            self.terminal_send,
        ):
            self._apply_action_button_style(btn)

        term_row = QHBoxLayout()
        term_row.setSpacing(8)
        term_row.addWidget(self.terminal_input, 1)
        term_row.addWidget(self.terminal_send)
        term_row.addWidget(self.auto_yes)

        self.terminal_panel = QWidget()
        term_layout = QVBoxLayout(self.terminal_panel)
        term_layout.setContentsMargins(18, 6, 18, 6)
        term_layout.setSpacing(6)
        term_layout.addWidget(self.terminal_label)
        term_layout.addWidget(self.terminal_output)
        term_layout.addLayout(term_row)

        content_layout.addLayout(self._row_language())
        content_layout.addWidget(self.section_gen)
        content_layout.addLayout(self._row_key_type())
        content_layout.addLayout(self._row_label(self.lbl_key_bits, self.key_bits))
        content_layout.addLayout(self._row_label(self.lbl_comment, self.comment))
        content_layout.addLayout(self._row_label(self.lbl_passphrase, self.passphrase))
        content_layout.addLayout(self._row_label(QLabel(""), self.auto_add_agent))
        content_layout.addLayout(self._row_path(self.lbl_path, self.path_edit, self.btn_browse, self.btn_reset))

        content_layout.addSpacing(6)

        self.btn_generate.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        row_gen = QHBoxLayout()
        row_gen.addWidget(self.btn_generate)
        content_layout.addLayout(row_gen)

        content_layout.addWidget(self.section_agent)
        content_layout.addLayout(self._row_agent_key_path())
        content_layout.addLayout(self._row_three_buttons(self.btn_add_agent, self.btn_enable_agent, self.btn_disable_agent))

        content_layout.addWidget(self.section_upload)
        content_layout.addLayout(self._row_label(self.lbl_auth_method, self.auth_method))
        content_layout.addLayout(self._row_key_path_auth())
        content_layout.addLayout(self._row_label(self.lbl_auth_key_pass, self.auth_key_passphrase))
        content_layout.addLayout(self._row_label(self.lbl_host, self.host))
        content_layout.addLayout(self._row_label(self.lbl_port, self.port))
        content_layout.addLayout(self._row_label(self.lbl_user, self.username))
        content_layout.addLayout(self._row_label(self.lbl_password, self.password))

        self.btn_upload.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        row_upload = QHBoxLayout()
        row_upload.addWidget(self.btn_upload)
        content_layout.addLayout(row_upload)

        content_layout.addLayout(self._row_single_button(self.btn_open_terminal))

        content_layout.addWidget(self.section_remote)
        content_layout.addWidget(self.remote_keys_list)
        content_layout.addLayout(self._row_three_buttons(self.btn_detect_remote, self.btn_remove_remote, self.btn_replace_remote))

        layout.addWidget(self.terminal_panel)
        layout.addWidget(self.status, 0, Qt.AlignmentFlag.AlignHCenter)

        self.proc = None
        self.proc_purpose = None
        self._last_keygen_path = None
        self._pending_auto_add = False
        self._auto_yes_sent = False
        self._awaiting_agent_passphrase = False
        self._pending_agent_path = None
        self._askpass_path = None
        self._remote_client = None
        self._remote_channel = None
        self._remote_timer = QTimer(self)
        self._remote_timer.setInterval(100)
        self._remote_timer.timeout.connect(self._poll_remote_shell)

        self.load_settings()
        self.apply_styles()
        self.apply_language()
        self.on_key_type_changed(self.key_type.currentText())
        self.update_auth_ui()
        self.init_music()
        self.init_pulse()

    def tr(self, key: str, **kwargs) -> str:
        text = TRANSLATIONS.get(self.lang, TRANSLATIONS["EN"]).get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

    def load_settings(self):
        lang = self.settings.value("language", "EN")
        if lang in ("EN", "PL"):
            self.lang = lang
        idx = 0 if self.lang == "EN" else 1
        self.lang_combo.setCurrentIndex(idx)

        self._saved_key_type = self.settings.value("key_type", "ed25519")
        self.key_bits.setValue(int(self.settings.value("key_bits", 4096)))
        self.comment.setText(self.settings.value("comment", ""))
        self.path_edit.setText(self.settings.value("path", ""))
        self.host.setText(self.settings.value("host", ""))
        self.port.setValue(int(self.settings.value("port", 22)))
        self.username.setText(self.settings.value("username", ""))
        self.music_toggle.setChecked(self.settings.value("music", "true") == "true")
        self.auto_add_agent.setChecked(self.settings.value("auto_agent", "false") == "true")
        self.auth_method.setCurrentIndex(int(self.settings.value("auth_method", 0)))
        self.auth_key_path.setText(self.settings.value("auth_key_path", ""))
        self.agent_key_path.setText(self.settings.value("agent_key_path", ""))

    def save_settings(self):
        self.settings.setValue("language", self.lang)
        self.settings.setValue("key_type", parse_key_type(self.key_type.currentText()))
        self.settings.setValue("key_bits", self.key_bits.value())
        self.settings.setValue("comment", self.comment.text())
        self.settings.setValue("path", self.path_edit.text())
        self.settings.setValue("host", self.host.text())
        self.settings.setValue("port", self.port.value())
        self.settings.setValue("username", self.username.text())
        self.settings.setValue("music", "true" if self.music_toggle.isChecked() else "false")
        self.settings.setValue("auto_agent", "true" if self.auto_add_agent.isChecked() else "false")
        self.settings.setValue("auth_method", self.auth_method.currentIndex())
        self.settings.setValue("auth_key_path", self.auth_key_path.text())
        self.settings.setValue("agent_key_path", self.agent_key_path.text())

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def apply_language(self):
        self.titlebar.set_title(self.tr("app_title"))
        self.titlebar.set_tooltips(self.tr("minimize"), self.tr("maximize"), self.tr("close"))

        self.section_gen.setText(self.tr("section_gen"))
        self.section_agent.setText(self.tr("section_agent"))
        self.section_upload.setText(self.tr("section_upload"))
        self.section_remote.setText(self.tr("section_remote_keys"))

        self.lbl_language.setText(self.tr("language_label"))
        self.lbl_key_type.setText(self.tr("key_type_label"))
        self.lbl_key_bits.setText(self.tr("key_bits_label"))
        self.lbl_comment.setText(self.tr("comment_label"))
        self.lbl_passphrase.setText(self.tr("passphrase_label"))
        self.lbl_path.setText(self.tr("path_label"))
        self.lbl_host.setText(self.tr("host_label"))
        self.lbl_port.setText(self.tr("port_label"))
        self.lbl_user.setText(self.tr("user_label"))
        self.lbl_password.setText(self.tr("password_label"))
        self.lbl_auth_method.setText(self.tr("auth_method_label"))
        self.lbl_auth_key_path.setText(self.tr("auth_key_path"))
        self.lbl_auth_key_pass.setText(self.tr("auth_key_pass"))
        self.lbl_agent_key_path.setText(self.tr("agent_key_path_label"))

        self.terminal_label.setText(self.tr("terminal_label"))
        self.terminal_input.setPlaceholderText(self.tr("terminal_input_placeholder"))
        self.terminal_send.setText(self.tr("terminal_send"))
        self.auto_yes.setText(self.tr("auto_yes"))

        self.comment.setPlaceholderText(self.tr("comment_placeholder"))
        self.passphrase.setPlaceholderText(self.tr("passphrase_placeholder"))
        self.host.setPlaceholderText(self.tr("host_placeholder"))

        self.btn_browse.setText(self.tr("browse"))
        self.btn_reset.setText(self.tr("reset_default"))
        self.auth_key_browse.setText(self.tr("browse"))
        self.agent_key_browse.setText(self.tr("browse"))
        self.btn_generate.setText(self.tr("generate_btn"))
        self.btn_upload.setText(self.tr("upload_btn"))
        self.btn_open_terminal.setText(self.tr("open_terminal"))
        self.music_toggle.setText(self.tr("music_toggle"))
        self.btn_instruction.setText(self.tr("instruction_btn"))
        self.auto_add_agent.setText(f"{self.tr('auto_add_agent')} {self.tr('auto_add_agent_note')}")

        self.btn_add_agent.setText(self.tr("add_selected_agent"))
        self.btn_enable_agent.setText(self.tr("enable_agent"))
        self.btn_disable_agent.setText(self.tr("disable_agent"))

        self.btn_detect_remote.setText(self.tr("detect_remote"))
        self.btn_remove_remote.setText(self.tr("remove_remote"))
        self.btn_replace_remote.setText(self.tr("replace_remote"))

        self.auth_method.blockSignals(True)
        self.auth_method.clear()
        self.auth_method.addItem(self.tr("auth_password"), "password")
        self.auth_method.addItem(self.tr("auth_key"), "key")
        self.auth_method.addItem(self.tr("auth_key_passphrase"), "key_pass")
        self.auth_method.addItem(self.tr("auth_agent"), "agent")
        self.auth_method.blockSignals(False)
        saved_auth = int(self.settings.value("auth_method", 0))
        if saved_auth < self.auth_method.count():
            self.auth_method.setCurrentIndex(saved_auth)
        else:
            self.auth_method.setCurrentIndex(0)

        items = key_type_items(self.lang)
        current_type = self._saved_key_type or parse_key_type(self.key_type.currentText())
        self.key_type.blockSignals(True)
        self.key_type.clear()
        self.key_type.addItems(items)
        self.key_type.blockSignals(False)
        self.set_key_type(current_type)
        self._saved_key_type = None

        if not self.path_edit.text().strip():
            self.path_edit.setText(str(default_key_path(parse_key_type(self.key_type.currentText()))))

        self.set_status(self.tr("status_ready"), MUTED)

    def show_instructions(self):
        dialog = InstructionDialog(self, self.tr("instruction_title"), self.tr("instruction_body"))
        dialog.exec()

    def set_key_type(self, key_type: str):
        for i in range(self.key_type.count()):
            if parse_key_type(self.key_type.itemText(i)) == key_type:
                self.key_type.setCurrentIndex(i)
                return
        self.key_type.setCurrentIndex(0)

    def on_key_type_changed(self, key_type_text: str):
        key_type = parse_key_type(key_type_text)
        is_rsa = key_type == "rsa"
        self.key_bits.setEnabled(is_rsa)
        self.key_type_desc.setText(KEY_TYPE_INFO[self.lang].get(key_type, ""))
        current = Path(self.path_edit.text().strip()) if self.path_edit.text().strip() else None
        default_path = default_key_path(key_type)
        if current is None or current.name in (
            "id_rsa",
            "id_ed25519",
            "id_ecdsa",
            "id_ed25519_sk",
            "id_ecdsa_sk",
            "id_dsa",
            "id_xmss",
        ):
            self.path_edit.setText(str(default_path))

    def on_language_changed(self):
        self.lang = self.lang_combo.currentData()
        self.settings.setValue("language", self.lang)
        self.apply_language()
        self.on_key_type_changed(self.key_type.currentText())
        self.update_auth_ui()

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color: rgb(200,210,255); font-size: 14px; font-weight: 700;")
        return lbl

    def _row_label(self, label_widget: QLabel, widget: QWidget) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        label_widget.setStyleSheet("color: rgb(180,190,230); font-size: 12px;")
        label_widget.setFixedWidth(160)
        row.addWidget(label_widget)
        row.addWidget(widget, 1)
        return row

    def _row_language(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        self.lbl_language.setStyleSheet("color: rgb(180,190,230); font-size: 12px;")
        self.lbl_language.setFixedWidth(160)
        row.addWidget(self.lbl_language)
        row.addWidget(self.lang_combo, 0)
        row.addWidget(self.btn_instruction, 0)
        row.addStretch(1)
        row.addWidget(self.music_toggle)
        return row

    def _row_key_type(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        self.lbl_key_type.setStyleSheet("color: rgb(180,190,230); font-size: 12px;")
        self.lbl_key_type.setFixedWidth(160)
        row.addWidget(self.lbl_key_type)
        row.addWidget(self.key_type, 0)
        row.addWidget(self.key_type_desc, 1)
        return row

    def _row_key_path_auth(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        self.lbl_auth_key_path.setStyleSheet("color: rgb(180,190,230); font-size: 12px;")
        self.lbl_auth_key_path.setFixedWidth(160)
        row.addWidget(self.lbl_auth_key_path)
        row.addWidget(self.auth_key_path, 1)
        row.addWidget(self.auth_key_browse)
        return row

    def _row_agent_key_path(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        self.lbl_agent_key_path.setStyleSheet("color: rgb(180,190,230); font-size: 12px;")
        self.lbl_agent_key_path.setFixedWidth(160)
        row.addWidget(self.lbl_agent_key_path)
        row.addWidget(self.agent_key_path, 1)
        row.addWidget(self.agent_key_browse)
        return row

    def _row_path(self, label_widget: QLabel, edit: QLineEdit, btn1: QPushButton, btn2: QPushButton) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        label_widget.setStyleSheet("color: rgb(180,190,230); font-size: 12px;")
        label_widget.setFixedWidth(160)
        row.addWidget(label_widget)
        row.addWidget(edit, 1)
        row.addWidget(btn1)
        row.addWidget(btn2)
        return row

    def _row_three_buttons(self, b1: QPushButton, b2: QPushButton, b3: QPushButton) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(b1, 1)
        row.addWidget(b2, 1)
        row.addWidget(b3, 1)
        return row

    def _row_single_button(self, btn: QPushButton) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(btn, 0)
        row.addStretch(1)
        return row

    def _apply_action_button_style(self, btn: QPushButton):
        btn.setStyleSheet(BUTTON_STYLE)

    def apply_styles(self):
        self.setStyleSheet(
            """
            QLabel { color: rgb(230,234,255); }
            QLabel#status_label {
                background: rgba(30, 40, 90, 180);
                border: 1px solid rgba(140, 160, 255, 180);
                border-radius: 12px;
                padding: 6px 14px;
                color: rgb(220, 230, 255);
            }

            QLineEdit, QSpinBox, QListWidget {
                background-color: rgb(18, 26, 64);
                background: rgb(18, 26, 64);
                color: rgb(230,234,255);
                border: 1px solid rgba(90, 100, 170, 220);
                border-radius: 12px;
                padding: 6px 10px;
                min-height: 28px;
            }

            QLineEdit:enabled, QSpinBox:enabled, QListWidget:enabled {
                background-color: rgb(10, 20, 60);
                background: rgb(10, 20, 60);
            }

            QLineEdit:disabled, QSpinBox:disabled, QListWidget:disabled {
                background-color: rgb(26, 32, 70);
                background: rgb(26, 32, 70);
                color: rgb(140,150,190);
            }

            QPlainTextEdit#terminal_output {
                background-color: rgb(10, 20, 60);
                color: rgb(230,234,255);
                border: 1px solid rgba(90, 100, 170, 220);
                border-radius: 12px;
                padding: 6px 10px;
                min-height: 90px;
            }

            QComboBox {
                background-color: rgb(10, 20, 60);
                background: rgb(10, 20, 60);
                color: rgb(230,234,255);
                border: 1px solid rgba(90, 100, 170, 220);
                border-radius: 12px;
                padding: 6px 10px;
                min-height: 28px;
            }

            QComboBox:enabled {
                background-color: rgb(10, 20, 60);
                background: rgb(10, 20, 60);
            }

            QComboBox:disabled {
                background-color: rgb(26, 32, 70);
                background: rgb(26, 32, 70);
                color: rgb(140,150,190);
            }

            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 1px solid rgba(110, 130, 255, 220);
            }

            QComboBox::drop-down {
                border: 0px;
                width: 26px;
            }

            QListWidget::item { padding: 2px 6px; }

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(90, 80, 255, 220),
                    stop:1 rgba(40, 110, 255, 220));
                color: white;
                border: 1px solid rgba(120, 140, 255, 200);
                border-radius: 12px;
                padding: 8px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(110, 95, 255, 240),
                    stop:1 rgba(60, 130, 255, 240));
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(70, 60, 210, 240),
                    stop:1 rgba(30, 90, 210, 240));
            }
            QPushButton#title_min, QPushButton#title_max, QPushButton#title_close {
                background: rgba(20, 26, 50, 200);
                border: 1px solid rgba(120, 140, 255, 160);
                border-radius: 10px;
                padding: 0px;
                min-height: 0px;
            }
            QPushButton#title_min:hover, QPushButton#title_max:hover {
                background: rgba(40, 60, 120, 220);
            }
            QPushButton#title_close {
                background: rgba(70, 24, 40, 220);
                border: 1px solid rgba(220, 120, 150, 180);
            }
            QPushButton#title_close:hover {
                background: rgba(110, 30, 50, 240);
            }

            QCheckBox { color: rgb(190, 200, 230); }
            QScrollArea { background: transparent; }

            QComboBox QAbstractItemView {
                background-color: rgba(10, 20, 60, 128);
                color: rgb(230,234,255);
                border: 1px solid rgba(90, 100, 170, 220);
                outline: 0px;
                selection-background-color: rgba(60, 80, 160, 220);
                padding: 6px;
            }
            QComboBox QAbstractItemView::item {
                background-color: rgba(10, 20, 60, 180);
                padding: 4px 6px;
            }
            QComboBox QAbstractItemView::item:selected {
                color: rgb(230,234,255);
            }

            QMenu {
                background-color: rgba(10, 20, 60, 128);
                color: rgb(230,234,255);
                border: 1px solid rgba(90, 100, 170, 220);
            }
            QMenu::item {
                background-color: rgba(10, 20, 60, 180);
                padding: 6px 12px;
            }
            QMenu::item:selected {
                background-color: rgba(60, 80, 160, 220);
                color: rgb(230,234,255);
            }

            QScrollBar:vertical {
                background: rgba(10, 14, 34, 180);
                width: 10px;
                margin: 6px 6px 6px 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(70, 90, 170, 210),
                    stop:1 rgba(30, 50, 110, 210));
                border: 1px solid rgba(120, 140, 210, 200);
                border-radius: 4px;
                min-height: 24px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(90, 120, 200, 230),
                    stop:1 rgba(40, 70, 140, 230));
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            """
        )

    def _append_terminal(self, text: str):
        if not text:
            return
        clean = text.replace("\r\n", "\n").replace("\r", "\n")
        for line in clean.split("\n"):
            self.terminal_output.appendPlainText(line)

    def _send_to_process(self, text: str):
        if not self.proc or self.proc.state() != QProcess.ProcessState.Running:
            self.set_status(self.tr("no_process"), MUTED)
            return
        self.proc.write((text + "\n").encode("utf-8"))

    def send_terminal_input(self):
        text_raw = self.terminal_input.text()
        if self._awaiting_agent_passphrase and (
            not self.proc or self.proc.state() != QProcess.ProcessState.Running
        ):
            self.terminal_input.clear()
            self._append_terminal(self.tr("agent_passphrase_submitted"))
            passphrase = text_raw
            key_path = self._pending_agent_path or self.agent_key_path.text().strip()
            self._awaiting_agent_passphrase = False
            self._pending_agent_path = None
            if not key_path:
                self.set_status(self.tr("auth_required"), ERROR)
                return
            self._start_ssh_add(key_path, passphrase)
            return

        if self._remote_channel and (not self.proc or self.proc.state() != QProcess.ProcessState.Running):
            if not text_raw.strip():
                return
            self.terminal_input.clear()
            self._append_terminal(f"> {text_raw}")
            try:
                self._remote_channel.send((text_raw + "\n").encode("utf-8"))
            except Exception as exc:
                self.set_status(self.tr("ssh_error", err=exc), ERROR)
            return

        text = text_raw.strip()
        if not text:
            return
        self._append_terminal(f"> {text}")
        self.terminal_input.clear()
        self._send_to_process(text)

    def _maybe_auto_yes(self, text: str):
        if not self.auto_yes.isChecked() or self._auto_yes_sent:
            return
        lower = text.lower()
        if "overwrite" in lower or "(y/n" in lower or "[y/n" in lower or "yes/no" in lower:
            self._auto_yes_sent = True
            self._append_terminal("> y")
            self._send_to_process("y")

    def _maybe_focus_terminal(self, text: str):
        lower = text.lower()
        if (
            "overwrite" in lower
            or "(y/n" in lower
            or "[y/n" in lower
            or "yes/no" in lower
            or "passphrase" in lower
        ):
            self.terminal_input.setFocus()
            self.terminal_input.selectAll()

    def _ensure_askpass_helper(self) -> str:
        if self._askpass_path and Path(self._askpass_path).is_file():
            return self._askpass_path
        path = Path(tempfile.gettempdir()) / "ssh_key_forge_askpass.cmd"
        content = "@echo off\r\npowershell -NoProfile -Command \"[Console]::Write($env:SSH_ASKPASS_PASS)\"\r\n"
        try:
            path.write_text(content, encoding="utf-8")
        except Exception:
            pass
        self._askpass_path = str(path)
        return self._askpass_path

    def _make_askpass_env(self, passphrase: str) -> QProcessEnvironment:
        env = QProcessEnvironment.systemEnvironment()
        helper = self._ensure_askpass_helper()
        env.insert("SSH_ASKPASS", helper)
        env.insert("SSH_ASKPASS_REQUIRE", "force")
        env.insert("SSH_ASKPASS_PASS", passphrase)
        env.insert("DISPLAY", "1")
        return env

    def _start_ssh_add(self, key_path: str, passphrase: str) -> bool:
        env = self._make_askpass_env(passphrase or "")
        if self._start_process("ssh-add", [key_path], "ssh-add", env=env):
            self.set_status(self.tr("agent_started"), MUTED)
            return True
        return False

    def _start_process(self, program: str, args: list, purpose: str, env=None) -> bool:
        if self.proc and self.proc.state() == QProcess.ProcessState.Running:
            self.set_status(self.tr("process_running"), MUTED)
            return False
        self.proc = QProcess(self)
        self.proc.setProgram(program)
        self.proc.setArguments(args)
        if env is not None:
            self.proc.setProcessEnvironment(env)
        self.proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        if os.name == "nt":
            def _modifier(args):
                args.flags |= 0x08000000  # CREATE_NO_WINDOW
                args.flags |= 0x00000200  # CREATE_NEW_PROCESS_GROUP
            try:
                self.proc.setCreateProcessArgumentsModifier(_modifier)
            except Exception:
                pass
        self.proc.readyReadStandardOutput.connect(self._on_process_output)
        self.proc.errorOccurred.connect(self._on_process_error)
        self.proc.finished.connect(self._on_process_finished)
        self.proc_purpose = purpose
        self._auto_yes_sent = False

        cmd_line = " ".join([program] + [f'"{a}"' if " " in a else a for a in args])
        self._append_terminal(f"$ {cmd_line}")
        self.proc.start()
        return True

    def _on_process_output(self):
        if not self.proc:
            return
        data = bytes(self.proc.readAllStandardOutput()).decode("utf-8", errors="replace")
        if data:
            self._append_terminal(data)
            self._maybe_auto_yes(data)
            self._maybe_focus_terminal(data)

    def _poll_remote_shell(self):
        if not self._remote_channel:
            return
        try:
            if self._remote_channel.recv_ready():
                data = self._remote_channel.recv(4096)
                if data:
                    text = data.decode("utf-8", errors="replace")
                    self._append_terminal(text)
            if self._remote_channel.closed or self._remote_channel.exit_status_ready():
                self._remote_timer.stop()
                try:
                    self._remote_channel.close()
                except Exception:
                    pass
                try:
                    if self._remote_client:
                        self._remote_client.close()
                except Exception:
                    pass
                self._remote_channel = None
                self._remote_client = None
                self.set_status(self.tr("remote_shell_closed"), MUTED)
        except Exception as exc:
            self._remote_timer.stop()
            self._remote_channel = None
            if self._remote_client:
                try:
                    self._remote_client.close()
                except Exception:
                    pass
            self._remote_client = None
            self.set_status(self.tr("ssh_error", err=exc), ERROR)

    def _on_process_error(self, error):
        if self.proc_purpose == "keygen":
            if error == QProcess.ProcessError.FailedToStart:
                self.set_status(self.tr("missing_ssh_keygen"), ERROR)
            else:
                self.set_status(self.tr("gen_error"), ERROR)
        elif self.proc_purpose == "ssh-add":
            if error == QProcess.ProcessError.FailedToStart:
                self.set_status(self.tr("agent_missing"), ERROR)
            else:
                self.set_status(self.tr("agent_err", err=error), ERROR)
        else:
            self.set_status(self.tr("gen_error"), ERROR)

        self.proc = None
        self.proc_purpose = None

    def _on_process_finished(self, exit_code, exit_status):
        success = exit_status == QProcess.ExitStatus.NormalExit and exit_code == 0

        if self.proc_purpose == "keygen":
            if success:
                path_obj = self._last_keygen_path
                pub_path = f"{path_obj}.pub" if path_obj else ""
                self.set_status(self.tr("key_generated", path=path_obj, pub=pub_path), SUCCESS)
                if path_obj:
                    self.agent_key_path.setText(str(path_obj))
                if self._pending_auto_add:
                    self._pending_auto_add = False
                    self.proc = None
                    self.proc_purpose = None
                    passphrase = self.passphrase.text()
                    if passphrase:
                        QTimer.singleShot(0, lambda p=passphrase: self.add_key_to_agent(p))
                    else:
                        QTimer.singleShot(0, self.add_key_to_agent)
                    return
            else:
                self.set_status(self.tr("gen_error"), ERROR)
                self._pending_auto_add = False
        elif self.proc_purpose == "ssh-add":
            if success:
                self.set_status(self.tr("agent_added"), SUCCESS)
            else:
                self.set_status(self.tr("agent_err", err=exit_code), ERROR)

        self.proc = None
        self.proc_purpose = None

    def update_auth_ui(self):
        method = self.auth_method.currentData()
        use_password = method == "password"
        use_key = method in ("key", "key_pass")
        use_key_pass = method == "key_pass"

        self.password.setEnabled(use_password)
        self.auth_key_path.setEnabled(use_key)
        self.auth_key_browse.setEnabled(use_key)
        self.auth_key_passphrase.setEnabled(use_key_pass)

    def pick_path(self):
        path, _ = QFileDialog.getSaveFileName(self, self.tr("file_dialog_title"), self.path_edit.text())
        if path:
            self.path_edit.setText(path)

    def pick_auth_key(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr("file_dialog_key"), str(Path.home()))
        if path:
            self.auth_key_path.setText(path)

    def reset_path(self):
        self.path_edit.setText(str(default_key_path(parse_key_type(self.key_type.currentText()))))

    def set_status(self, text: str, color: QColor = MUTED):
        self.status.setText(text)
        self.status.setStyleSheet(
            f"QLabel#status_label {{ background: rgba(30, 40, 90, 180); border: 1px solid rgba(140, 160, 255, 180); border-radius: 12px; padding: 6px 14px; color: rgba({color.red()}, {color.green()}, {color.blue()}, 230); }}"
        )
        self.status.adjustSize()

    def generate_key(self):
        key_type = parse_key_type(self.key_type.currentText())
        path = self.path_edit.text().strip()
        if not path:
            self.set_status(self.tr("path_missing"), ERROR)
            return
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        if path_obj.exists():
            self._append_terminal(self.tr("file_exists_body"))
            self._append_terminal(self.tr("terminal_overwrite_hint"))
        comment = self.comment.text().strip()
        passphrase = self.passphrase.text()
        bits = self.key_bits.value() if key_type == "rsa" else None
        args = ["-t", key_type, "-f", str(path_obj), "-N", passphrase]
        if comment:
            args.extend(["-C", comment])
        if key_type == "rsa" and bits:
            args.extend(["-b", str(bits)])

        self._last_keygen_path = path_obj
        self._pending_auto_add = self.auto_add_agent.isChecked()
        if self._start_process("ssh-keygen", args, "keygen"):
            self.set_status(self.tr("gen_started"), MUTED)

    def pick_agent_key(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr("file_dialog_key"), str(Path.home()))
        if path:
            self.agent_key_path.setText(path)

    def add_key_to_agent(self, passphrase: str = None):
        if isinstance(passphrase, bool):
            passphrase = None
        if os.name != "nt":
            self.set_status(self.tr("agent_windows_only"), MUTED)
            return

        key_path = self.agent_key_path.text().strip()
        if not key_path:
            self.set_status(self.tr("auth_required"), ERROR)
            return

        path_obj = Path(key_path).expanduser()
        if not path_obj.is_file():
            self.set_status(f"Plik klucza nie istnieje: {path_obj}", ERROR)
            return

        if passphrase is None:
            self._pending_agent_path = str(path_obj)
            self._awaiting_agent_passphrase = True
            self._append_terminal(self.tr("agent_passphrase_prompt"))
            self.set_status(self.tr("agent_passphrase_status"), MUTED)
            self.terminal_input.setFocus()
            self.terminal_input.selectAll()
            return

        self._awaiting_agent_passphrase = False
        self._pending_agent_path = None
        self._start_ssh_add(str(path_obj), passphrase)

    def enable_ssh_agent(self):
        if os.name != "nt":
            self.set_status(self.tr("agent_windows_only"), MUTED)
            return
        try:
            cmd = (
                "Start-Process PowerShell -Verb RunAs -ArgumentList "
                "'Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0; "
                "Set-Service ssh-agent -StartupType Automatic; Start-Service ssh-agent'"
            )
            subprocess.Popen(["powershell", "-NoProfile", "-Command", cmd])
            self.set_status(self.tr("agent_install_started"), MUTED)
        except Exception as exc:
            self.set_status(self.tr("agent_install_failed", err=exc), ERROR)

    def disable_ssh_agent(self):
        if os.name != "nt":
            self.set_status(self.tr("agent_windows_only"), MUTED)
            return
        try:
            cmd = (
                "Start-Process PowerShell -Verb RunAs -ArgumentList "
                "'Stop-Service ssh-agent -ErrorAction SilentlyContinue; "
                "Set-Service ssh-agent -StartupType Disabled'"
            )
            subprocess.Popen(["powershell", "-NoProfile", "-Command", cmd])
            self.set_status(self.tr("disable_agent"), MUTED)
        except Exception as exc:
            self.set_status(self.tr("agent_install_failed", err=exc), ERROR)

    def load_private_key(self, key_path: str, passphrase: str):
        try:
            import paramiko
        except Exception:
            self.set_status(self.tr("paramiko_missing"), ERROR)
            return None

        pkey = None
        for cls in (paramiko.Ed25519Key, paramiko.ECDSAKey, paramiko.RSAKey, paramiko.DSSKey):
            try:
                pkey = cls.from_private_key_file(key_path, password=passphrase or None)
                if pkey:
                    return pkey
            except Exception:
                continue
        return None

    def connect_client(self):
        host = self.host.text().strip()
        user = self.username.text().strip()
        if not host or not user:
            self.set_status(self.tr("host_login_pass_required"), ERROR)
            return None

        method = self.auth_method.currentData()
        password = self.password.text()
        key_path = self.auth_key_path.text().strip()
        key_pass = self.auth_key_passphrase.text()

        try:
            import paramiko
        except Exception:
            self.set_status(self.tr("paramiko_missing"), ERROR)
            return None

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if method == "password":
                if not password:
                    self.set_status(self.tr("auth_required"), ERROR)
                    return None
                client.connect(hostname=host, port=self.port.value(), username=user, password=password, timeout=8, allow_agent=False, look_for_keys=False)
                return client

            if method in ("key", "key_pass"):
                if not key_path:
                    self.set_status(self.tr("auth_required"), ERROR)
                    return None
                pkey = self.load_private_key(key_path, key_pass if method == "key_pass" else "")
                if not pkey:
                    self.set_status(self.tr("auth_required"), ERROR)
                    return None
                client.connect(
                    hostname=host,
                    port=self.port.value(),
                    username=user,
                    pkey=pkey,
                    allow_agent=False,
                    look_for_keys=False,
                    timeout=8,
                )
                return client

            if method == "agent":
                client.connect(
                    hostname=host,
                    port=self.port.value(),
                    username=user,
                    allow_agent=True,
                    look_for_keys=True,
                    timeout=8,
                )
                return client
        except Exception as exc:
            self.set_status(self.tr("ssh_error", err=exc), ERROR)
            return None

        self.set_status(self.tr("auth_required"), ERROR)
        return None

    def upload_key(self):
        pub_path = Path(self.path_edit.text().strip() + ".pub")
        if not pub_path.exists():
            self.set_status(self.tr("pub_missing"), ERROR)
            return

        pub_key = pub_path.read_text(encoding="utf-8").strip()
        if not pub_key:
            self.set_status(self.tr("pub_empty"), ERROR)
            return

        client = self.connect_client()
        if not client:
            return

        try:
            client.exec_command("mkdir -p ~/.ssh && chmod 700 ~/.ssh")
            sftp = client.open_sftp()
            auth_path = ".ssh/authorized_keys"

            existing = ""
            try:
                with sftp.open(auth_path, "r") as f:
                    existing = f.read().decode("utf-8")
            except IOError:
                existing = ""

            if pub_key in existing:
                self.set_status(self.tr("upload_exists"), MUTED)
            else:
                with sftp.open(auth_path, "a") as f:
                    if existing and not existing.endswith("\n"):
                        f.write("\n")
                    f.write(pub_key + "\n")
                client.exec_command("chmod 600 ~/.ssh/authorized_keys")
                self.set_status(self.tr("upload_ok"), SUCCESS)

            sftp.close()
            client.close()
        except Exception as exc:
            self.set_status(self.tr("ssh_error", err=exc), ERROR)

    def open_remote_terminal(self):
        if self.proc and self.proc.state() == QProcess.ProcessState.Running:
            self.set_status(self.tr("process_running"), MUTED)
            return
        if self._remote_channel:
            try:
                self._remote_channel.close()
            except Exception:
                pass
            self._remote_channel = None
        if self._remote_client:
            try:
                self._remote_client.close()
            except Exception:
                pass
            self._remote_client = None

        host = self.host.text().strip()
        user = self.username.text().strip()
        if not host or not user:
            self.set_status(self.tr("host_login_pass_required"), ERROR)
            return

        client = self.connect_client()
        if not client:
            return

        try:
            channel = client.invoke_shell()
            self._remote_client = client
            self._remote_channel = channel
            self._remote_timer.start()
            self._append_terminal(f"$ ssh {user}@{host}")
            self.set_status(self.tr("remote_shell_opened"), SUCCESS)
            self.terminal_input.setFocus()
            self.terminal_input.selectAll()
        except Exception as exc:
            try:
                client.close()
            except Exception:
                pass
            self.set_status(self.tr("ssh_error", err=exc), ERROR)

    def detect_remote_keys(self):
        client = self.connect_client()
        if not client:
            return

        self.remote_keys_list.clear()
        try:
            sftp = client.open_sftp()
            auth_path = ".ssh/authorized_keys"
            content = ""
            try:
                with sftp.open(auth_path, "r") as f:
                    content = f.read().decode("utf-8")
            except IOError:
                content = ""

            lines = [ln.strip() for ln in content.splitlines() if ln.strip() and not ln.strip().startswith("#")]
            for line in lines:
                item = QListWidgetItem(short_key_label(line))
                item.setData(Qt.ItemDataRole.UserRole, line)
                self.remote_keys_list.addItem(item)

            if not lines:
                self.set_status(self.tr("remote_keys_empty"), MUTED)
            else:
                self.set_status(self.tr("remote_keys_loaded", count=len(lines)), SUCCESS)

            sftp.close()
            client.close()
        except Exception as exc:
            self.set_status(self.tr("ssh_error", err=exc), ERROR)

    def remove_remote_keys(self):
        selected = [item.data(Qt.ItemDataRole.UserRole) for item in self.remote_keys_list.selectedItems()]
        if not selected:
            self.set_status(self.tr("remote_keys_none"), MUTED)
            return

        client = self.connect_client()
        if not client:
            return

        try:
            sftp = client.open_sftp()
            auth_path = ".ssh/authorized_keys"
            content = ""
            try:
                with sftp.open(auth_path, "r") as f:
                    content = f.read().decode("utf-8")
            except IOError:
                content = ""

            lines = [ln for ln in content.splitlines()]
            remaining = [ln for ln in lines if ln.strip() not in selected]

            with sftp.open(auth_path, "w") as f:
                f.write("\n".join([ln for ln in remaining if ln.strip()]) + "\n" if remaining else "")
            client.exec_command("chmod 600 ~/.ssh/authorized_keys")

            sftp.close()
            client.close()

            self.detect_remote_keys()
            self.set_status(self.tr("remote_keys_removed"), SUCCESS)
        except Exception as exc:
            self.set_status(self.tr("ssh_error", err=exc), ERROR)

    def replace_remote_keys(self):
        pub_path = Path(self.path_edit.text().strip() + ".pub")
        if not pub_path.exists():
            self.set_status(self.tr("pub_missing"), ERROR)
            return
        pub_key = pub_path.read_text(encoding="utf-8").strip()
        if not pub_key:
            self.set_status(self.tr("pub_empty"), ERROR)
            return

        selected = [item.data(Qt.ItemDataRole.UserRole) for item in self.remote_keys_list.selectedItems()]

        client = self.connect_client()
        if not client:
            return

        try:
            sftp = client.open_sftp()
            auth_path = ".ssh/authorized_keys"
            content = ""
            try:
                with sftp.open(auth_path, "r") as f:
                    content = f.read().decode("utf-8")
            except IOError:
                content = ""

            if selected:
                lines = [ln for ln in content.splitlines() if ln.strip() and ln.strip() not in selected]
                lines.append(pub_key)
            else:
                lines = [pub_key]

            with sftp.open(auth_path, "w") as f:
                f.write("\n".join(lines) + "\n")
            client.exec_command("chmod 600 ~/.ssh/authorized_keys")

            sftp.close()
            client.close()

            self.detect_remote_keys()
            self.set_status(self.tr("remote_keys_replaced"), SUCCESS)
        except Exception as exc:
            self.set_status(self.tr("ssh_error", err=exc), ERROR)

    def init_music(self):
        if QMediaPlayer is None:
            self.music_toggle.setChecked(False)
            self.music_toggle.setEnabled(False)
            self.set_status(self.tr("music_disabled"), MUTED)
            return

        music_path = Path(__file__).with_name("bg.mp3")
        if not music_path.exists():
            self.music_toggle.setChecked(False)
            self.set_status(self.tr("music_missing"), MUTED)
            return

        self._player = QMediaPlayer()
        self._audio = QAudioOutput()
        self._audio.setVolume(0.25)
        self._player.setAudioOutput(self._audio)
        self._player.setSource(QUrl.fromLocalFile(str(music_path)))
        try:
            self._player.setLoops(QMediaPlayer.Loops.Infinite)
        except Exception:
            pass
        try:
            self._player.mediaStatusChanged.connect(self._on_media_status)
        except Exception:
            pass
        if self.music_toggle.isChecked():
            self._player.play()

    def _on_media_status(self, status):
        try:
            if status == QMediaPlayer.MediaStatus.EndOfMedia and self.music_toggle.isChecked():
                self._player.setPosition(0)
                self._player.play()
        except Exception:
            pass

    def toggle_music(self):
        if not self._player:
            return
        if self.music_toggle.isChecked():
            self._player.play()
        else:
            self._player.stop()

    def init_pulse(self):
        self._pulse_phase = 0.0
        self._pulse_inputs = [
            self.comment,
            self.passphrase,
            self.path_edit,
            self.auth_key_path,
            self.auth_key_passphrase,
            self.host,
            self.username,
            self.password,
            self.agent_key_path,
            self.terminal_input,
            self.key_bits,
            self.port,
        ]
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._update_input_pulse)
        self._pulse_timer.start(80)

    def _update_input_pulse(self):
        self._pulse_phase = (self._pulse_phase + 0.08) % (2 * math.pi)
        t = (math.sin(self._pulse_phase) + 1.0) / 2.0
        c1 = QColor(90, 140, 255)
        c2 = QColor(140, 90, 255)
        r = int(c1.red() + (c2.red() - c1.red()) * t)
        g = int(c1.green() + (c2.green() - c1.green()) * t)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
        border = f"border: 1px solid rgba({r}, {g}, {b}, 220);"
        for widget in self._pulse_inputs:
            if widget.isEnabled():
                if isinstance(widget, QLineEdit):
                    widget.setStyleSheet(
                        "background-color: rgb(10, 20, 60);"
                        "color: rgb(230,234,255);"
                        "border-radius: 12px;"
                        "padding: 6px 10px;"
                        "min-height: 28px;"
                        + border
                    )
                elif isinstance(widget, QSpinBox):
                    widget.setStyleSheet(
                        "background-color: rgb(10, 20, 60);"
                        "color: rgb(230,234,255);"
                        "border-radius: 12px;"
                        "padding: 6px 10px;"
                        "min-height: 28px;"
                        + border
                    )
                else:
                    widget.setStyleSheet(border)
            else:
                widget.setStyleSheet("")
    def set_drag_active(self, active: bool):
        if self._is_maximized:
            return
        self._drag_active = active

    def toggle_maximize(self):
        if not self._is_maximized:
            self.setFixedSize(MAX_SIZE, MAX_SIZE)
            self._is_maximized = True
            self._drag_active = False
            self.titlebar.btn_max.setText("❐")
            self.titlebar.set_maximize_tooltip(self.tr("restore"))
        else:
            self.setFixedSize(self._base_size, self._base_size)
            self._is_maximized = False
            self._drag_active = False
            self.titlebar.btn_max.setText("□")
            self.titlebar.set_maximize_tooltip(self.tr("maximize"))


def main():
    if "QT_LOGGING_RULES" not in os.environ:
        os.environ["QT_LOGGING_RULES"] = "qt.multimedia.ffmpeg=false"
    app = QApplication(sys.argv)
    app.setApplicationName("SSH Key Forge")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()












