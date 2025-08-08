import logging

from app.hotkey_daemon import (
    start_daemon,
    stop_daemon,
)
from app.tray import create_tray
from config.logger_conf import configure_logging

logger = logging.getLogger(__name__)


def main():
    configure_logging(level=20)

    logger.info("Запуск Noita Saver")

    start_daemon()

    tray_icon = create_tray()

    # Блокирующий вызов - пока пользователь не выйдет
    tray_icon.run()

    stop_daemon()

    logger.info("Noita Saver завершил работу")


if __name__ == "__main__":
    main()
