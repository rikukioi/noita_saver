import psutil
import re
import os
from pathlib import Path


def get_process_by_name(process_name: str) -> psutil.Process | None:
    """
    Функция поиска процесса по имени.

    Args:
        process_name (str): Имя процесса для происка.

    Returns:
        (psutil.Process | None): Объект процесса, если найден, иначе None.
    """
    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            if proc.name() == process_name:
                return proc
        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            return None


def has_files(path: str | Path) -> bool:
    """
    Функция проверки наличия файлов в папке.

    Args:
        path (str | Path): Путь к папке.

    Raises:
        ValueError: Если путь не является папкой.

    Returns:
        bool: True если присутствует хоть один файл.
    """
    path = Path(path)

    if not path.is_dir():
        raise ValueError(f"Путь не является папкой: {path}")
    return any(obj.is_file() for obj in path.iterdir())


# TODO: Добавить использование этой функции в cmdline_resolver
def get_steam_library_paths_windows() -> list[Path]:
    program_files = os.getenv("PROGRAMFILES(X86)")
    if not program_files:
        program_files = Path("C:/Program Files (x86)")
        if not program_files.exists() or not program_files.is_dir():
            return []

    library_folders_file = (
        Path(program_files) / "Steam" / "steamapps" / "libraryfolders.vdf"
    )
    if not library_folders_file.exists():
        return []

    raw = library_folders_file.read_text(encoding="utf-8", errors="ignore")

    paths = re.findall(r'"path"\s+"([^"]+)"', raw)
    return [Path(p) for p in paths]
