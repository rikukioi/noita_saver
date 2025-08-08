import pystray
import logging
from PIL import Image

from config.paths import ICON_PATH

logger = logging.getLogger(__name__)


def on_exit(icon) -> None:
    logger.debug("Выключение иконки трей-приложения.")
    icon.stop()


def create_tray():
    icon = pystray.Icon(
        title="Noita Saver",
        name="Noita Saver",
        icon=Image.open(ICON_PATH),
    )
    icon.menu = pystray.Menu(
        pystray.MenuItem("Выйти", lambda: on_exit(icon)),
    )
    return icon
