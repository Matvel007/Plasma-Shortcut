#!/usr/bin/env python3

import sys
import os
import subprocess
import tempfile
import glob
import hashlib
import shutil
import re

from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QFileDialog, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon


LANG = os.environ.get("LANG", "en_US")

T = {}

if LANG.startswith("ru"):
    T["create_title"] = "Создать ярлык — v1.1"
    T["edit_title"] = "Изменить ярлык — v1.1"
    T["create_header"] = "Создать ярлык для:"
    T["edit_header"] = "Изменить ярлык для:"
    T["file"] = "Файл:"
    T["path"] = "Путь:"
    T["run_with"] = "Запускать через:"
    T["wine_default"] = "Wine (по умолчанию)"
    T["browse"] = "Обзор…"
    T["cancel"] = "Отмена"
    T["create"] = "Создать"
    T["save"] = "Сохранить"
    T["no_icon"] = "Нет иконки"
    T["select_proton"] = "Выберите Proton"
elif LANG.startswith("uk"):
    T["create_title"] = "Створити ярлик — v1.1"
    T["edit_title"] = "Змінити ярлик — v1.1"
    T["create_header"] = "Створити ярлик для:"
    T["edit_header"] = "Змінити ярлик для:"
    T["file"] = "Файл:"
    T["path"] = "Шлях:"
    T["run_with"] = "Запускати через:"
    T["wine_default"] = "Wine (за замовчуванням)"
    T["browse"] = "Огляд…"
    T["cancel"] = "Скасувати"
    T["create"] = "Створити"
    T["save"] = "Зберегти"
    T["no_icon"] = "Немає іконки"
    T["select_proton"] = "Виберіть Proton"
else:
    T["create_title"] = "Create Shortcut — v1.1"
    T["edit_title"] = "Edit Shortcut — v1.1"
    T["create_header"] = "Create Shortcut for:"
    T["edit_header"] = "Edit Shortcut for:"
    T["file"] = "File:"
    T["path"] = "Path:"
    T["run_with"] = "Run with:"
    T["wine_default"] = "Wine (default)"
    T["browse"] = "Browse…"
    T["cancel"] = "Cancel"
    T["create"] = "Create"
    T["save"] = "Save"
    T["no_icon"] = "No icon"
    T["select_proton"] = "Select Proton binary"
    T["about_title"] = "About Plasma-Shortcut"
    T["about_btn"] = "Info"
    T["about_text"] = (
        "<b>Plasma-Shortcut v1.1</b><br><br>"
        "A Dolphin Service Menu for creating and editing .desktop shortcuts "
        "with GPU launch mode selector.<br><br>"
        "License: GNU GPL v2<br>"
        "Author: <a href='https://github.com/Matvel007'>Matvel007</a><br>"
        "Built with: DeepSeek-v4-flash<br><br>"
        "Source: <a href='https://github.com/Matvel007/Plasma-Shortcut'>github.com/Matvel007/Plasma-Shortcut</a>"
    )

if LANG.startswith("ru"):
    T["about_title"] = "О программе Plasma-Shortcut"
    T["about_btn"] = "Инфо"
    T["about_text"] = (
        "<b>Plasma-Shortcut v1.1</b><br><br>"
        "Сервисное меню Dolphin для создания и редактирования .desktop ярлыков "
        "с выбором режима запуска GPU.<br><br>"
        "Лицензия: GNU GPL v2<br>"
        "Создатель: <a href='https://github.com/Matvel007'>Matvel007</a><br>"
        "Создано с помощью: DeepSeek-v4-flash<br><br>"
        "Исходный код: <a href='https://github.com/Matvel007/Plasma-Shortcut'>github.com/Matvel007/Plasma-Shortcut</a>"
    )
elif LANG.startswith("uk"):
    T["about_title"] = "Про програму Plasma-Shortcut"
    T["about_btn"] = "Інфо"
    T["about_text"] = (
        "<b>Plasma-Shortcut v1.1</b><br><br>"
        "Сервісне меню Dolphin для створення та редагування .desktop ярликів "
        "з вибором режиму запуску GPU.<br><br>"
        "Ліцензія: GNU GPL v2<br>"
        "Автор: <a href='https://github.com/Matvel007'>Matvel007</a><br>"
        "Створено за допомогою: DeepSeek-v4-flash<br><br>"
        "Вихідний код: <a href='https://github.com/Matvel007/Plasma-Shortcut'>github.com/Matvel007/Plasma-Shortcut</a>"
    )


def find_proton_versions():
    versions = []
    search_dirs = [
        os.path.expanduser("~/.steam/root/compatibilitytools.d"),
        os.path.expanduser("~/.local/share/Steam/compatibilitytools.d"),
        os.path.expanduser("~/.local/share/Steam/steamapps/common"),
        "/usr/share/steam/compatibilitytools.d",
    ]
    seen = set()
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for entry in sorted(os.listdir(d), key=str.lower):
            full = os.path.join(d, entry)
            if os.path.isdir(full):
                proton_bin = os.path.join(full, "proton")
                if os.path.isfile(proton_bin) and os.access(proton_bin, os.X_OK):
                    if full not in seen:
                        seen.add(full)
                        versions.append((entry, proton_bin))
    return versions


def extract_icon(exe_path):
    ico_dir = os.path.expanduser("~/.local/share/create-shortcut/icons")
    os.makedirs(ico_dir, exist_ok=True)

    h = hashlib.md5(exe_path.encode()).hexdigest()
    cached_png = os.path.join(ico_dir, f"{h}.png")

    if os.path.isfile(cached_png):
        return cached_png

    try:
        result = subprocess.run(
            ["wrestool", "-x", "--type=14", exe_path],
            capture_output=True, timeout=15,
        )
        if not result.stdout:
            return None

        with tempfile.NamedTemporaryFile(suffix=".ico", delete=False) as f:
            f.write(result.stdout)
            ico_path = f.name

        png_dir = tempfile.mkdtemp()
        subprocess.run(
            ["icotool", "-x", ico_path, "-o", png_dir],
            capture_output=True, timeout=15,
        )

        pngs = sorted(
            glob.glob(os.path.join(png_dir, "*.png")),
            key=os.path.getsize, reverse=True,
        )
        if pngs:
            shutil.move(pngs[0], cached_png)

        os.unlink(ico_path)
        shutil.rmtree(png_dir, ignore_errors=True)

        if os.path.isfile(cached_png):
            return cached_png
    except Exception:
        pass
    return None


def parse_shortcut(shortcut_path):
    exe_path = None
    runner_type = "wine"
    runner_path = None

    try:
        with open(shortcut_path, "r") as f:
            content = f.read()

        m = re.search(r'^Exec=(.+)$', content, re.MULTILINE)
        if not m:
            return None, None, None

        exec_line = m.group(1).strip()

        if exec_line.startswith("env "):
            proton_match = re.search(r'"([^"]*proton[^"]*)"', exec_line)
            if proton_match:
                runner_type = "proton"
                runner_path = proton_match.group(1)

            exe_match = re.search(r'run "([^"]+)"', exec_line)
            if exe_match:
                exe_path = exe_match.group(1)
        elif exec_line.startswith("wine "):
            exe_match = re.search(r'wine "([^"]+)"', exec_line)
            if exe_match:
                exe_path = exe_match.group(1)

        return exe_path, runner_type, runner_path
    except Exception:
        return None, None, None


class ShortcutDialog(QDialog):
    def __init__(self, exe_path, icon_path, edit_mode=False,
                 current_runner=None, current_runner_path=None, parent=None):
        super().__init__(parent)
        self.exe_path = exe_path
        self.edit_mode = edit_mode

        if edit_mode:
            self.setWindowTitle(T["edit_title"])
        else:
            self.setWindowTitle(T["create_title"])

        self.setMinimumWidth(540)
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
            QPushButton#btnOk {
                background-color: palette(highlight);
                color: palette(highlightedText);
                border: none;
                font-weight: 600;
            }
            QPushButton#btnOk:hover {
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
            QFrame#iconFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 8px;
            }
        """)

        self._build_ui(icon_path, current_runner, current_runner_path)

    def _build_ui(self, icon_path, current_runner, current_runner_path):
        header_text = T["edit_header"] if self.edit_mode else T["create_header"]
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel(header_text)
        header.setObjectName("header")
        layout.addWidget(header)

        name_label = QLabel(os.path.basename(self.exe_path))
        name_label.setObjectName("sub")
        name_label.setWordWrap(True)
        name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(name_label)

        card = QFrame()
        card.setObjectName("iconFrame")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(20)

        icon_widget = QLabel()
        icon_widget.setFixedSize(96, 96)
        icon_widget.setAlignment(Qt.AlignCenter)
        if icon_path and os.path.isfile(icon_path):
            pix = QPixmap(icon_path)
            if not pix.isNull():
                icon_widget.setPixmap(pix.scaled(
                    96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
            else:
                icon_widget.setText(T["no_icon"])
        else:
            icon_widget.setText(T["no_icon"])
        card_layout.addWidget(icon_widget)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        info_layout.addWidget(QLabel(f"<b>{T['file']}</b> {os.path.basename(self.exe_path)}"))
        info_layout.addWidget(QLabel(f"<b>{T['path']}</b> {self.exe_path}"))

        runner_layout = QHBoxLayout()
        runner_layout.setSpacing(8)
        runner_label = QLabel(f"<b>{T['run_with']}</b>")
        runner_layout.addWidget(runner_label)

        self.runner_combo = QComboBox()
        self.runner_combo.setMinimumWidth(240)
        self.runner_combo.addItem(T["wine_default"], None)

        preselect_idx = 0
        idx = 1
        self.proton_versions = find_proton_versions()
        if self.proton_versions:
            for name, path in self.proton_versions:
                self.runner_combo.addItem(f"Proton: {name}", ("proton", path))
                if (current_runner == "proton" and
                        current_runner_path and
                        os.path.samefile(path, current_runner_path)):
                    preselect_idx = idx
                idx += 1

        self.runner_combo.addItem(T["browse"], "browse")
        self.runner_combo.currentIndexChanged.connect(self._on_runner_changed)
        self.runner_combo.setCurrentIndex(preselect_idx)
        runner_layout.addWidget(self.runner_combo, 1)
        info_layout.addLayout(runner_layout)

        self.custom_path_label = QLabel("")
        self.custom_path_label.setObjectName("sub")
        self.custom_path_label.setWordWrap(True)
        info_layout.addWidget(self.custom_path_label)

        card_layout.addLayout(info_layout, 1)
        layout.addWidget(card)

        btn_layout = QHBoxLayout()

        about_btn = QPushButton(T["about_btn"])
        about_btn.setFixedSize(64, 32)
        about_btn.setObjectName("btnCancel")
        about_btn.clicked.connect(self._show_about)
        btn_layout.addWidget(about_btn)

        btn_layout.addStretch()

        cancel_btn = QPushButton(T["cancel"])
        cancel_btn.setObjectName("btnCancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_text = T["save"] if self.edit_mode else T["create"]
        ok_btn = QPushButton(ok_text)
        ok_btn.setObjectName("btnOk")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def _show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(T["about_title"])
        msg.setTextFormat(Qt.RichText)
        msg.setText(T["about_text"])
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def _on_runner_changed(self, idx):
        data = self.runner_combo.currentData()
        if data == "browse":
            path, _ = QFileDialog.getOpenFileName(
                self, T["select_proton"],
                os.path.expanduser("~"),
                "Proton binary (proton);;All files (*)"
            )
            if path:
                name = os.path.basename(os.path.dirname(path))
                self.runner_combo.insertItem(
                    self.runner_combo.count() - 1,
                    f"Proton: {name} ({path})",
                    ("proton", path),
                )
                self.runner_combo.setCurrentIndex(self.runner_combo.count() - 2)
                self.custom_path_label.setText(f"{path}")
            else:
                self.runner_combo.setCurrentIndex(0)
                self.custom_path_label.setText("")

    def get_runner(self):
        data = self.runner_combo.currentData()
        if data is None:
            return ("wine", None)
        return data


def write_shortcut(exe_path, shortcut_path, runner_type, runner_path, icon_path):
    dirname = os.path.dirname(exe_path)
    basename = os.path.basename(exe_path)
    name = os.path.splitext(basename)[0]

    if runner_type == "wine":
        exec_cmd = f'wine "{exe_path}"'
        icon_val = icon_path if icon_path else "wine"
        categories = "Wine;"
    else:
        compat_data = os.path.join(dirname, ".ProtonCompatData")
        os.makedirs(compat_data, exist_ok=True)
        steam_path = os.path.expanduser("~/.local/share/Steam")
        exec_cmd = (
            f'env STEAM_COMPAT_DATA_PATH="{compat_data}" '
            f'STEAM_COMPAT_CLIENT_INSTALL_PATH="{steam_path}" '
            f'"{runner_path}" run "{exe_path}"'
        )
        icon_val = icon_path if icon_path else "steam"
        categories = "Game;"

    prefix = "Shortcut to"
    if LANG.startswith("ru"):
        prefix = "Ярлык для"
    elif LANG.startswith("uk"):
        prefix = "Ярлик для"

    with open(shortcut_path, "w") as f:
        f.write("[Desktop Entry]\n")
        f.write("Type=Application\n")
        f.write(f"Name={name}\n")
        f.write(f"Exec={exec_cmd}\n")
        f.write(f"Icon={icon_val}\n")
        f.write("Terminal=false\n")
        f.write(f"Comment={prefix} {basename}\n")
        f.write(f"Categories={categories}\n")

    os.chmod(shortcut_path, 0o755)


def main():
    if len(sys.argv) < 2:
        print("Usage: dolphin-shortcut-dialog.py <exe_path> [<shortcut_path>]",
              file=sys.stderr)
        sys.exit(1)

    exe_path = sys.argv[1]
    edit_mode = len(sys.argv) >= 3 and sys.argv[2]

    if not os.path.isfile(exe_path):
        print(f"File not found: {exe_path}", file=sys.stderr)
        sys.exit(1)

    app = QApplication(sys.argv)

    icon_path = extract_icon(exe_path)
    current_runner = None
    current_runner_path = None

    if edit_mode:
        app.setApplicationName(T["edit_title"])
        _, current_runner, current_runner_path = parse_shortcut(edit_mode)
    else:
        app.setApplicationName(T["create_title"])

    dialog = ShortcutDialog(
        exe_path, icon_path,
        edit_mode=bool(edit_mode),
        current_runner=current_runner,
        current_runner_path=current_runner_path,
    )

    if dialog.exec() == QDialog.Accepted:
        runner_type, runner_path = dialog.get_runner()

        if edit_mode:
            shortcut_path = edit_mode
        else:
            dirname = os.path.dirname(exe_path)
            basename = os.path.basename(exe_path)
            prefix = "Shortcut to"
            if LANG.startswith("ru"):
                prefix = "Ярлык для"
            elif LANG.startswith("uk"):
                prefix = "Ярлик для"
            shortcut_name = f"{prefix} {basename}.desktop"
            shortcut_path = os.path.join(dirname, shortcut_name)

        write_shortcut(exe_path, shortcut_path, runner_type, runner_path, icon_path)


if __name__ == "__main__":
    main()
