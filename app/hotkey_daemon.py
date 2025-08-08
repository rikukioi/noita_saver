import keyboard
import logging
import threading

from services import (
    NoitaManager,
    BackupService,
)
from core.exceptions import NoitaError

logger = logging.getLogger(__name__)
noita_manager = NoitaManager()
backup_service = BackupService()
stop_daemon_event = threading.Event()


def handle_backup():
    try:
        noita_manager.shutdown_noita()
        backup_service.backup()
        noita_manager.launch_noita()
    except NoitaError as err:
        logger.warning("Произошла ошибка во время бэкапа сохранений: %s", err)


def handle_restore():
    try:
        noita_manager.shutdown_noita()
        backup_service.restore()
        noita_manager.launch_noita()
    except NoitaError as err:
        logger.warning("Произошла ошибка во время восстановления сохранений: %s", err)


def keyboard_event_loop() -> None:
    keyboard.add_hotkey("ctrl+alt+f7", handle_backup)
    keyboard.add_hotkey("ctrl+alt+f8", handle_restore)

    logger.info("Демон для прослушивания комбинаций клавиш запущен.")

    # Основной loop демона
    while not stop_daemon_event.is_set():
        stop_daemon_event.wait(timeout=1)

    logger.info("Демон для прослушивания комбинаций клавиш остановлен.")


def start_daemon() -> None:
    threading.Thread(target=keyboard_event_loop, daemon=True).start()


def stop_daemon() -> None:
    stop_daemon_event.set()
