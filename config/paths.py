from pathlib import Path

# Главная директория приложения
APP_DIR = Path(__file__).parent.parent

# Логи
LOG_DIR = APP_DIR / "logs"

# Для бэкап-сервиса
NOITA_SAVES_DIR = Path.home() / "AppData" / "LocalLow" / "Nolla_Games_Noita" / "save00"
BACKUP_SAVES_DIR = APP_DIR / "backup" / "save00"

# Иконка для приложения в трее
ICON_PATH = APP_DIR / "icons" / "noita.png"
