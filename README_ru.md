# Plasma-Shortcut — Сервисное меню Dolphin

[**English version**](README.md)

Добавляет пункты **«Создать ярлык»** и **«Изменить ярлык»** в контекстное меню Dolphin. Создаёт `.desktop` файлы — аналог Windows `.lnk`.

## Возможности

- **Создать ярлык** — ПКМ по любому файлу/папке → создаёт `.desktop` ярлык рядом
- **Изменить ярлык** — ПКМ по существующему `.desktop` ярлыку → сменить Wine/Proton
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

### Arch Linux (PKGBUILD)

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
    ├── dolphin-shortcut-dialog.py     # Python GUI диалог
    ├── create-shortcut.desktop        # Сервисное меню (все файлы)
    └── edit-shortcut.desktop          # Сервисное меню (только .desktop)
```

## Лицензия

GNU GPL v2
