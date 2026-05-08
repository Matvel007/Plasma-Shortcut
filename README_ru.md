# Plasma-Shortcut — Сервисное меню Dolphin

[**English version**](README.md) | [![AUR](https://img.shields.io/aur/version/plasma-shortcut)](https://aur.archlinux.org/packages/plasma-shortcut)

Добавляет пункты **«Создать ярлык»**, **«Изменить ярлык»** и **«Режим запуска»** в контекстное меню Dolphin. Создаёт `.desktop` файлы — аналог Windows `.lnk`.

## Возможности

- **Создать ярлык** — ПКМ по любому файлу/папке → создаёт `.desktop` ярлык рядом
- **Изменить ярлык** — ПКМ по существующему `.desktop` ярлыку → сменить Wine/Proton
- **Режим запуска** — ПКМ по любому `.desktop` ярлыку → выбрать встроенную графику или NVIDIA для запуска. Работает с **Flatpak**, **Wine/Proton** и нативными приложениями
- **Автоопределение GPU** — автоматически находит Intel (встройка) и NVIDIA (дискретная)
- **Поддержка .exe** — создаёт `Type=Application` ярлыки (запуск через Wine или Proton)
- **Извлечение иконок** — автоматически извлекает и кеширует иконки из `.exe` (требуется `icoutils`)
- **Поддержка Proton** — находит установленные версии Proton (GE-Proton, Steam Proton и т.д.)
- **GUI диалог** — нативное окно в стиле Plasma 6 с предпросмотром иконки и выбором раннера
- **Минималистичный интерфейс** — только то, что нужно, без лишнего
- **Работает нативно** — не требует установки PortProton или его аналогов
- **Авто-язык** — меню и диалог на русском/украинском/английском (определяется из системы)

## Зависимости

| Пакет | Назначение |
|-------|------------|
| `kio` | Поддержка сервисных меню Dolphin (обычно уже установлен) |
| `icoutils` | Извлечение иконок из `.exe` файлов |
| `pyside6` | GUI диалог для выбора раннера .exe |

Установка зависимостей:

```bash
sudo pacman -S icoutils pyside6
```

## Установка

### Быстрая (только для текущего пользователя)

```bash
git clone https://github.com/yourusername/Plasma-Shortcut
cd Plasma-Shortcut
./install.sh
```

### Для всех пользователей

```bash
sudo ./install.sh
```

### Arch Linux (AUR)

```bash
yay -S plasma-shortcut
# или
paru -S plasma-shortcut
```

### Arch Linux (PKGBUILD вручную)

```bash
makepkg -si
```

### Удаление

```bash
# пользовательская установка
./uninstall.sh

# системная установка
sudo ./uninstall.sh
```

## Скриншоты

<p align="center">
  <img src="1.png" alt="Диалог создания ярлыка" width="45%">
  <img src="2.png" alt="Контекстное меню" width="45%">
</p>

<p align="center">
  <img src="3.png" alt="Диалог режима запуска" width="45%">
</p>

## Использование

### Создать ярлык

ПКМ по любому файлу или папке в Dolphin → **Create Shortcut** → **Создать .desktop ярлык**

Для `.exe` файлов открывается диалог с:
- Предпросмотром иконки (извлечённой из .exe)
- Выбором раннера: **Wine** (по умолчанию) или любой **Proton**
- Кнопка **Создать** → `.desktop` файл появляется рядом

Перетащите `.desktop` файл на рабочий стол или панель для закрепления.

### Изменить ярлык

ПКМ по `.desktop` ярлыку → **Edit Shortcut** → изменить Wine ↔ Proton → **Сохранить**

### Настроить режим запуска GPU

ПКМ по любому `.desktop` ярлыку → **Режим запуска** → выбрать **Авто**, **Intel (iGPU)** или **NVIDIA (dGPU)** → **Применить**

Диалог автоматически определяет GPU вашей системы. Работает с:
- **Flatpak** приложениями (через `flatpak override`)
- **Wine/Proton** ярлыками
- **Нативными** приложениями
- **AUR/системными** пакетами (автокопирование в `~/.local/share/applications/`)

Для Flatpak/NVIDIA: устанавливает `__NV_PRIME_RENDER_OFFLOAD=1`, `__GLX_VENDOR_LIBRARY_NAME=nvidia`, `__VK_LAYER_NV_optimus=NVIDIA_only`.

## Структура проекта

```
Plasma-Shortcut/
├── install.sh                         # Скрипт установки
├── uninstall.sh                       # Скрипт удаления
├── PKGBUILD                           # Пакет для Arch Linux
├── README.md                          # README на английском
├── README_ru.md                       # README на русском (этот файл)
├── Plasma-Shortcut.install # Хуки pacman
└── src/
    ├── dolphin-create-shortcut        # Bash скрипт (режим создания)
    ├── dolphin-edit-shortcut          # Bash скрипт (режим редактирования)
    ├── dolphin-launch-mode            # Bash скрипт (режим запуска)
    ├── dolphin-shortcut-dialog.py     # Python GUI (создание/изменение)
    ├── dolphin-launch-mode-dialog.py  # Python GUI (режим запуска)
    ├── create-shortcut.desktop        # Сервисное меню (все файлы)
    ├── edit-shortcut.desktop          # Сервисное меню (.desktop)
    └── launch-mode.desktop            # Сервисное меню (.desktop)
```

## Лицензия

GNU GPL v2
