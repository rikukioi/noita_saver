import psutil
from pathlib import Path


def get_process_by_name(process_name: str) -> psutil.Process | None:
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
    path = Path(path)

    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")
    return any(obj.is_file() for obj in path.iterdir())
