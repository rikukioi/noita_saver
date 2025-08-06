import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


LOG_DIR = Path(__file__).parent / "logs"


def configure_logging(level=logging.INFO) -> None:
    LOG_DIR.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        fmt="[%(asctime)s.%(msecs)03d] | %(levelname)7s | [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d  %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        filename=LOG_DIR / "noita_saver.log",
        maxBytes=10_000_000,
        encoding="UTF-8",
        backupCount=5,
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    error_handler = RotatingFileHandler(
        filename=LOG_DIR / "noita_saver_error.log",
        maxBytes=10_000_000,
        encoding="UTF-8",
        backupCount=5,
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if not root_logger.handlers:
        root_logger.addHandler(file_handler)
        root_logger.addHandler(error_handler)
