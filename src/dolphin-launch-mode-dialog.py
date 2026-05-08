#!/usr/bin/env python3

import sys
import os
import re
import glob
import shutil
import subprocess

from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon


LANG = os.environ.get("LANG", "en_US")

T = {}

if LANG.startswith("ru"):
    T["title"] = "Режим запуска — v1.1"
    T["header"] = "Настройка режима запуска для:"
    T["file"] = "Файл:"
    T["path"] = "Путь:"
    T["exec"] = "Команда:"
    T["launch_mode"] = "Режим запуска:"
    T["auto"] = "Авто (по умолчанию)"
    T["integrated"] = "Встроенная графика"
    T["discrete_nvidia"] = "Дискретная NVIDIA"
    T["detected_gpu"] = "Обнаружено:"
    T["preview"] = "Предпросмотр команды:"
    T["cancel"] = "Отмена"
    T["apply"] = "Применить"
    T["saved"] = "Настройки режима запуска сохранены."
    T["error"] = "Ошибка"
elif LANG.startswith("uk"):
    T["title"] = "Режим запуску — v1.1"
    T["header"] = "Налаштування режиму запуску для:"
    T["file"] = "Файл:"
    T["path"] = "Шлях:"
    T["exec"] = "Команда:"
    T["launch_mode"] = "Режим запуску:"
    T["auto"] = "Авто (за замовчуванням)"
    T["integrated"] = "Вбудована графіка"
    T["discrete_nvidia"] = "Дискретна NVIDIA"
    T["detected_gpu"] = "Виявлено:"
    T["preview"] = "Попередній перегляд команди:"
    T["cancel"] = "Скасувати"
    T["apply"] = "Застосувати"
    T["saved"] = "Налаштування режиму запуску збережено."
    T["error"] = "Помилка"
else:
    T["title"] = "Launch Mode — v1.1"
    T["header"] = "Configure Launch Mode for:"
    T["file"] = "File:"
    T["path"] = "Path:"
    T["exec"] = "Command:"
    T["launch_mode"] = "Launch Mode:"
    T["auto"] = "Auto (system default)"
    T["integrated"] = "Integrated Graphics"
    T["discrete_nvidia"] = "NVIDIA Discrete"
    T["detected_gpu"] = "Detected:"
    T["preview"] = "Command preview:"
    T["cancel"] = "Cancel"
    T["apply"] = "Apply"
    T["saved"] = "Launch mode settings saved."
    T["error"] = "Error"


def detect_gpus():
    gpus = {"integrated": None, "discrete_type": None,
            "has_prime_run": shutil.which("prime-run") is not None}

    vendor_map = {"0x8086": "Intel", "0x1002": "AMD", "0x10de": "NVIDIA"}

    for card in sorted(glob.glob("/sys/class/drm/card*")):
        vendor_file = os.path.join(card, "device", "vendor")
        if not os.path.isfile(vendor_file):
            continue
        try:
            with open(vendor_file) as f:
                vendor_id = f.read().strip()
        except (IOError, PermissionError):
            continue

        name = vendor_map.get(vendor_id)
        if not name:
            continue

        if vendor_id == "0x8086":
            gpus["integrated"] = name
        elif vendor_id == "0x10de":
            gpus["discrete_type"] = name
        elif vendor_id == "0x1002":
            if gpus["integrated"] is None:
                gpus["integrated"] = name

    return gpus


GPU_VARS = {"__NV_PRIME_RENDER_OFFLOAD", "__GLX_VENDOR_LIBRARY_NAME",
            "DRI_PRIME", "__EGL_VENDOR_LIBRARY_FILENAMES",
            "__VK_LAYER_NV_optimus"}


def _find_nvidia_egl_vendor():
    for d in ["/usr/share/glvnd/egl_vendor.d", "/etc/glvnd/egl_vendor.d"]:
        for f in sorted(glob.glob(os.path.join(d, "*nvidia*.json"))):
            if os.path.isfile(f):
                return f
    return None


def _split_shell_tokens(line):
    """Split a shell command line respecting quotes."""
    tokens = []
    current = ""
    in_quote = None
    for c in line:
        if in_quote:
            if c == in_quote:
                in_quote = None
            current += c
        elif c in "\"'":
            in_quote = c
            current += c
        elif c.isspace():
            if current:
                tokens.append(current)
                current = ""
        else:
            current += c
    if current:
        tokens.append(current)
    return tokens


def strip_gpu_env(exec_line):
    cleaned = exec_line.strip()

    if cleaned.startswith("prime-run "):
        cleaned = cleaned[len("prime-run "):]

    if cleaned.startswith("env "):
        cleaned = _strip_gpu_from_env_prefix(cleaned)
    else:
        cleaned = re.sub(r'^__NV_PRIME_RENDER_OFFLOAD=\S+\s*', '', cleaned)
        cleaned = re.sub(r'^__GLX_VENDOR_LIBRARY_NAME=\S+\s*', '', cleaned)
        cleaned = re.sub(r'^__VK_LAYER_NV_optimus=\S+\s*', '', cleaned)
        cleaned = re.sub(r'^DRI_PRIME=\S+\s*', '', cleaned)

    cleaned = re.sub(r'\s*--env=__NV_PRIME_RENDER_OFFLOAD=\S+', '', cleaned)
    cleaned = re.sub(r'\s*--env=__GLX_VENDOR_LIBRARY_NAME=\S+', '', cleaned)
    cleaned = re.sub(r'\s*--env=__VK_LAYER_NV_optimus=\S+', '', cleaned)
    cleaned = re.sub(r'\s*--env=DRI_PRIME=\S+', '', cleaned)
    cleaned = re.sub(r'\s*--env=__EGL_VENDOR_LIBRARY_FILENAMES=\S+', '', cleaned)

    return cleaned.strip()


def _strip_gpu_from_env_prefix(exec_line):
    prefix, cmd = _split_env_prefix(exec_line)
    clean_vars = [v for v in prefix if v.split("=")[0] not in GPU_VARS]
    if clean_vars:
        return "env " + " ".join(clean_vars + cmd)
    return " ".join(cmd)


def _split_env_prefix(exec_line):
    tokens = _split_shell_tokens(exec_line)
    env_vars = []
    cmd_start = 1
    for i in range(1, len(tokens)):
        tok = tokens[i]
        if "=" in tok:
            env_vars.append(tok)
        else:
            cmd_start = i
            break
    return env_vars, tokens[cmd_start:]


def add_gpu_env(clean_exec, mode, has_prime_run):
    if mode == "auto":
        return clean_exec

    is_flatpak = "flatpak" in clean_exec and " run " in clean_exec
    if is_flatpak:
        return _add_gpu_flatpak(clean_exec, mode, has_prime_run)

    gpu_vars = []
    if mode == "integrated":
        gpu_vars = ["DRI_PRIME=0"]
    elif mode == "nvidia":
        gpu_vars = ["__NV_PRIME_RENDER_OFFLOAD=1",
                     "__GLX_VENDOR_LIBRARY_NAME=nvidia",
                     "__VK_LAYER_NV_optimus=NVIDIA_only"]

    if not gpu_vars:
        return clean_exec

    if clean_exec.startswith("env "):
        existing_vars, cmd = _split_env_prefix(clean_exec)
        return "env " + " ".join(existing_vars + gpu_vars + cmd)

    return "env " + " ".join(gpu_vars) + " " + clean_exec


def _add_gpu_flatpak(exec_line, mode, has_prime_run):
    parts = exec_line.split()
    try:
        run_idx = parts.index("run")
    except ValueError:
        return exec_line

    app_idx = None
    for i in range(run_idx + 1, len(parts)):
        if not parts[i].startswith("-"):
            app_idx = i
            break

    if app_idx is None:
        return exec_line

    env_flags = []
    if mode == "integrated":
        env_flags.append("--env=DRI_PRIME=0")
    elif mode == "nvidia":
        env_flags.append("--env=__NV_PRIME_RENDER_OFFLOAD=1")
        env_flags.append("--env=__GLX_VENDOR_LIBRARY_NAME=nvidia")
        env_flags.append("--env=__VK_LAYER_NV_optimus=NVIDIA_only")

    before_app = parts[:app_idx]
    after_app = parts[app_idx:]
    result = before_app + env_flags + after_app
    return " ".join(result)


def parse_desktop(desktop_path):
    try:
        with open(desktop_path) as f:
            content = f.read()
    except (IOError, PermissionError):
        return None, None, None, None, None

    name_match = re.search(r'^Name=([^\n]+)', content, re.MULTILINE)
    name = name_match.group(1) if name_match else os.path.basename(desktop_path)

    exec_match = re.search(r'^Exec=([^\n]+)', content, re.MULTILINE)
    if not exec_match:
        return name[:40], None, None, None, content

    exec_line = exec_match.group(1).strip()

    mode_match = re.search(r'^X-PlasmaShortcut-LaunchMode=(\S+)',
                           content, re.MULTILINE)
    current_mode = mode_match.group(1) if mode_match else "auto"

    clean_match = re.search(r'^X-PlasmaShortcut-CleanExec=([^\n]+)',
                            content, re.MULTILINE)
    clean_exec = clean_match.group(1) if clean_match else strip_gpu_env(exec_line)

    return name[:40], exec_line, clean_exec, current_mode, content


def resolve_desktop(desktop_path):
    """Copy to ~/.local/share/applications/ if file is in a system location."""
    real_path = os.path.realpath(desktop_path)
    user_apps = os.path.expanduser("~/.local/share/applications")

    filename = os.path.basename(real_path)
    user_path = os.path.join(user_apps, filename)

    if os.path.isfile(user_path):
        return user_path, real_path

    system_prefixes = ["/usr", "/var", "/etc"]
    is_system = any(real_path.startswith(p) for p in system_prefixes)

    if not is_system:
        try:
            with open(real_path, "a"):
                pass
            return real_path, real_path
        except (IOError, PermissionError):
            is_system = True

    if is_system:
        os.makedirs(user_apps, exist_ok=True)
        try:
            with open(real_path) as src:
                content = src.read()
            with open(user_path, "w") as dst:
                dst.write(content)
            os.chmod(user_path, 0o755)
            return user_path, real_path
        except (IOError, PermissionError):
            return None, real_path

    return real_path, real_path


def extract_flatpak_app_id(exec_line):
    """Extract the Flatpak app ID from a flatpak run command."""
    parts = exec_line.split()
    try:
        run_idx = parts.index("run")
    except ValueError:
        return None

    for i in range(run_idx + 1, len(parts)):
        if not parts[i].startswith("-"):
            app_id = parts[i]
            if app_id.startswith("@@") or app_id.startswith("%"):
                continue
            return app_id
    return None


def apply_launch_mode(desktop_path, clean_exec, mode, has_prime_run, real_path=None):
    target = desktop_path
    parent_path = os.path.dirname(os.path.dirname(__file__))
    if os.path.isabs(parent_path):
        exec_bin = os.path.join(parent_path, "bin", "dolphin-launch-mode")
    else:
        exec_bin = "dolphin-launch-mode"

    if not os.path.isfile(exec_bin):
        exec_bin = os.path.expanduser("~/.local/bin/dolphin-launch-mode")

    if real_path:
        exec_bin = os.path.expanduser(f"~/.local/bin/dolphin-launch-mode")

    try:
        with open(target) as f:
            content = f.read()
    except (IOError, PermissionError):
        return False, None

    is_flatpak = "flatpak" in clean_exec and " run " in clean_exec
    new_exec = clean_exec

    if is_flatpak:
        app_id = extract_flatpak_app_id(clean_exec)
        if app_id:
            if mode == "auto":
                subprocess.run(
                    ["flatpak", "override", "--user", "--reset", app_id],
                    capture_output=True)
            else:
                args = ["flatpak", "override", "--user"]
                for var in GPU_VARS:
                    args.append("--unset-env=" + var)
                if mode == "integrated":
                    args.append("--env=DRI_PRIME=0")
                elif mode == "nvidia":
                    args.append("--env=__NV_PRIME_RENDER_OFFLOAD=1")
                    args.append("--env=__GLX_VENDOR_LIBRARY_NAME=nvidia")
                    args.append("--env=__VK_LAYER_NV_optimus=NVIDIA_only")
                args.append(app_id)
                subprocess.run(args, capture_output=True)
    else:
        new_exec = add_gpu_env(clean_exec, mode, has_prime_run)

    if re.search(r'^X-PlasmaShortcut-CleanExec=', content, re.MULTILINE):
        content = re.sub(
            r'^X-PlasmaShortcut-CleanExec=.*$',
            f'X-PlasmaShortcut-CleanExec={clean_exec}',
            content, flags=re.MULTILINE)
    else:
        content = content.rstrip() + f'\nX-PlasmaShortcut-CleanExec={clean_exec}\n'

    if re.search(r'^X-PlasmaShortcut-LaunchMode=', content, re.MULTILINE):
        content = re.sub(
            r'^X-PlasmaShortcut-LaunchMode=.*$',
            f'X-PlasmaShortcut-LaunchMode={mode}',
            content, flags=re.MULTILINE)
    else:
        content = content.rstrip() + f'\nX-PlasmaShortcut-LaunchMode={mode}\n'

    content = re.sub(r'^Exec=.*$', f'Exec={new_exec}', content, flags=re.MULTILINE)

    has_actions = bool(re.search(r'^Actions=.*launch-mode', content, re.MULTILINE))
    has_desktop_action = bool(re.search(r'^\[Desktop Action launch-mode\]',
                                        content, re.MULTILINE))

    if not has_desktop_action:
        desktop_action_text = (
            f'\n[Desktop Action launch-mode]\n'
            f'Name=Launch Mode…\n'
            f'Name[ru]=Режим запуска…\n'
            f'Name[uk]=Режим запуску…\n'
            f'Icon=preferences-system\n'
            f'Exec={exec_bin} %f\n'
        )
        content = content.rstrip() + desktop_action_text + '\n'

        if not has_actions:
            content = re.sub(
                r'(^\[Desktop Entry\]\n)',
                r'\1Actions=launch-mode;\n',
                content,
                flags=re.MULTILINE)
        else:
            content = re.sub(
                r'^Actions=(.*)$',
                lambda m: f'Actions={m.group(1)}launch-mode;'
                if 'launch-mode;' not in m.group(1)
                else m.group(0),
                content,
                flags=re.MULTILINE)

    try:
        with open(target, 'w') as f:
            f.write(content)
        return True, target
    except (IOError, PermissionError):
        return False, None


class LaunchModeDialog(QDialog):
    def __init__(self, desktop_path, parent=None):
        super().__init__(parent)
        self.original_path = desktop_path

        resolved, real = resolve_desktop(desktop_path)
        if resolved is None:
            QMessageBox.critical(None, T["error"],
                                 f"Cannot access: {desktop_path}")
            self._resolved_path = None
            return
        self._resolved_path = resolved
        self._real_path = real

        self.desktop_path = resolved

        self.setWindowTitle(T["title"])
        self.setMinimumWidth(580)
        self.setModal(True)

        self.setStyleSheet("""
            QDialog {
                background-color: palette(window);
            }
            QLabel#header {
                font-size: 14px;
                font-weight: 600;
                color: palette(windowText);
            }
            QLabel#sub {
                color: palette(placeholderText);
                font-size: 11px;
            }
            QLabel#previewLabel {
                background-color: palette(base);
                color: palette(windowText);
                padding: 8px 12px;
                border: 1px solid palette(mid);
                border-radius: 6px;
                font-family: monospace;
                font-size: 12px;
            }
            QComboBox {
                padding: 6px 10px;
                border: 1px solid palette(mid);
                border-radius: 6px;
                background-color: palette(base);
                color: palette(windowText);
                min-height: 24px;
            }
            QComboBox:hover {
                border-color: palette(highlight);
            }
            QComboBox::drop-down {
                border: none;
                width: 28px;
            }
            QComboBox QAbstractItemView {
                background-color: palette(base);
                color: palette(windowText);
                selection-background-color: palette(highlight);
                selection-color: palette(highlightedText);
                padding: 4px;
            }
            QPushButton {
                padding: 8px 24px;
                border-radius: 6px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton#btnApply {
                background-color: palette(highlight);
                color: palette(highlightedText);
                border: none;
                font-weight: 600;
            }
            QPushButton#btnApply:hover {
                background-color: palette(highlight);
            }
            QPushButton#btnCancel {
                background-color: palette(button);
                color: palette(buttonText);
                border: 1px solid palette(mid);
            }
            QPushButton#btnCancel:hover {
                background-color: palette(light);
            }
            QFrame#infoFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 8px;
            }
        """)

        self.gpus = detect_gpus()
        if self._resolved_path is None:
            return
        self.name, self.exec_line, self.clean_exec, self.current_mode, self.content = \
            parse_desktop(self.desktop_path)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel(T["header"])
        header.setObjectName("header")
        layout.addWidget(header)

        name_label = QLabel(self.name)
        name_label.setObjectName("sub")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        card = QFrame()
        card.setObjectName("infoFrame")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        card_layout.addWidget(QLabel(f"<b>{T['path']}</b> {self.desktop_path}"))

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel(f"<b>{T['launch_mode']}</b>"))

        self.mode_combo = QComboBox()
        self.mode_combo.setMinimumWidth(260)
        self._populate_modes()
        self.mode_combo.currentIndexChanged.connect(self._update_preview)
        mode_layout.addWidget(self.mode_combo, 1)
        card_layout.addLayout(mode_layout)

        gpu_text_parts = []
        if self.gpus["integrated"]:
            gpu_text_parts.append(f"{self.gpus['integrated']} (iGPU)")
        else:
            gpu_text_parts.append("—")
        if self.gpus["discrete_type"]:
            gpu_text_parts.append(f"{self.gpus['discrete_type']} (dGPU)")
        else:
            gpu_text_parts.append("—")

        gpu_label = QLabel(
            f"<b>{T['detected_gpu']}</b> "
            f"{' + '.join(gpu_text_parts)}"
        )
        card_layout.addWidget(gpu_label)

        card_layout.addWidget(QLabel(f"<b>{T['preview']}</b>"))

        self.preview_label = QLabel("")
        self.preview_label.setObjectName("previewLabel")
        self.preview_label.setWordWrap(True)
        self.preview_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        card_layout.addWidget(self.preview_label)

        layout.addWidget(card)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton(T["cancel"])
        cancel_btn.setObjectName("btnCancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        apply_btn = QPushButton(T["apply"])
        apply_btn.setObjectName("btnApply")
        apply_btn.setDefault(True)
        apply_btn.clicked.connect(self._apply)
        btn_layout.addWidget(apply_btn)

        layout.addLayout(btn_layout)

        self._update_preview()

    def _populate_modes(self):
        self.mode_combo.addItem(T["auto"], "auto")

        igpu_name = self.gpus["integrated"] or T["integrated"]
        self.mode_combo.addItem(f"{igpu_name} (iGPU)", "integrated")

        self.mode_combo.addItem(T["discrete_nvidia"], "nvidia")

        for i in range(self.mode_combo.count()):
            if self.mode_combo.itemData(i) == self.current_mode:
                self.mode_combo.setCurrentIndex(i)
                break

    def _update_preview(self):
        mode = self.mode_combo.currentData()
        clean = self.clean_exec or ""
        preview = add_gpu_env(clean, mode, self.gpus["has_prime_run"])
        self.preview_label.setText(preview)

    def _apply(self):
        if self._resolved_path is None:
            self.reject()
            return
        mode = self.mode_combo.currentData()
        clean = self.clean_exec or ""
        ok, new_path = apply_launch_mode(
            self._resolved_path, clean, mode,
            self.gpus["has_prime_run"], self._real_path)
        if ok:
            self.accept()
            msg = T["saved"]
            if new_path and new_path != self._real_path:
                msg += f"\n\nCopied to: {new_path}"
            QMessageBox.information(None, T["title"], msg)
        else:
            QMessageBox.critical(self, T["error"],
                                 "Failed to write to .desktop file.")


def main():
    if len(sys.argv) < 2:
        print("Usage: dolphin-launch-mode-dialog.py <desktop_path>",
              file=sys.stderr)
        sys.exit(1)

    desktop_path = sys.argv[1]

    if not os.path.isfile(desktop_path):
        print(f"File not found: {desktop_path}", file=sys.stderr)
        sys.exit(1)

    app = QApplication(sys.argv)
    dialog = LaunchModeDialog(desktop_path)
    dialog.exec()


if __name__ == "__main__":
    main()
