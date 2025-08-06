import logging
import threading
import keyboard
import pystray
from PIL import Image

from logger_conf import configure_logging
from backup_service import BackupService
from noita_process import NoitaProcess
from pathlib import Path

ICON_PATH = Path(__file__).parent / "icons" / "noita.png"

backup_service = BackupService()

logger = logging.getLogger(__name__)

stop_hotkey_daemon = threading.Event()


def backup_handler():
    noita_process = NoitaProcess()
    noita_process.terminate_noita()

    backup_service.backup_saves()

    noita_process.start_noita()


def restore_handler():
    noita_process = NoitaProcess()
    noita_process.terminate_noita()

    backup_service.restore_saves()

    noita_process.start_noita()


def register_hotkeys():
    keyboard.add_hotkey("ctrl+alt+f7", backup_handler)
    keyboard.add_hotkey("ctrl+alt+f8", restore_handler)
    logger.info("Hotkeys registered, starting hotkey daemon")

    while not stop_hotkey_daemon.is_set():
        stop_hotkey_daemon.wait(timeout=1)

    logger.info("Hotkeys daemon stopped")


def on_exit(icon, item):
    logger.info("Closing Noita Saver app")
    icon.stop()
    stop_hotkey_daemon.set()


def create_and_run_tray():
    icon = pystray.Icon(
        title="Noita Saver",
        name="Noita Saver Daemon",
        icon=Image.open(ICON_PATH),
    )
    icon.menu = pystray.Menu(
        pystray.MenuItem("Exit", lambda: on_exit(icon, None)),
    )
    icon.run()


def main():
    configure_logging()

    threading.Thread(target=register_hotkeys, daemon=True).start()
    create_and_run_tray()


if __name__ == "__main__":
    main()
