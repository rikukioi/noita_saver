import shutil
import logging
from pathlib import Path

from core.utils import has_files
from core.exceptions import (
    DirectoryNotExist,
    EmptyDirectoryError,
)
from config.paths import (
    NOITA_SAVES_DIR,
    BACKUP_SAVES_DIR,
)


logger = logging.getLogger(__name__)


class BackupService:
    """
    Бэкап-сервис для игры Noita позволяющий:
    - создавать бэкап папки сохранений.
    - восстанавливать сохранение из бэкапа.
    """

    def __init__(
        self,
        saves_dir: Path = NOITA_SAVES_DIR,
        backup_dir: Path = BACKUP_SAVES_DIR,
    ):
        self.saves_dir = saves_dir
        self.backup_dir = backup_dir

    def backup(self) -> None:
        """
        Создает бэкап из сохранения.

        Raises:
            DirectoryNotExist: Если не существует папки с актуальным сохранением.
            EmptyDirectoryError: Если папка сохранения пуста.
        """
        self._dir_and_files_exist_or_raise(self.saves_dir)
        self._swap_folders(src=self.saves_dir, dst=self.backup_dir)
        logger.info("Создан бэкап сохранения.")

    def restore(self) -> None:
        """
        Восстанавливает сохранение из бэкапа.

        Raises:
            DirectoryNotExist: Если не существует папки с бэкапом.
            EmptyDirectoryError: Если папка бэкапа пуста.
        """
        self._dir_and_files_exist_or_raise(self.backup_dir)
        self._swap_folders(src=self.backup_dir, dst=self.saves_dir)
        logger.info("Сохранение восстановлено из бэкапа.")

    def _dir_and_files_exist_or_raise(self, folder_path: Path) -> None:
        """
        Проверяет существование папки, затем наличие файлов в папке.

        Args:
            folder_path (Path): Путь к папке.

        Raises:
            DirectoryNotExist: Если путь не является папкой или не существует.
            EmptyDirectoryError: Если нет файлов в папке.
        """
        if not folder_path.exists() or not folder_path.is_dir():
            raise DirectoryNotExist(
                f"Папки не существует по пути: {folder_path}",
            )

        if not has_files(folder_path):
            raise EmptyDirectoryError(
                f"Папка по пути: {folder_path} не содержит файлов"
            )

    # Необходимо убедиться в существовании папки 'src'
    def _swap_folders(self, src: Path, dst: Path) -> None:
        """
        Копирует файлы из папки 'src' в папку 'dst', перед этим полностью удалив 'dst'.

        Args:
            src (Path): Папка из которой копируются файлы.
            dst (Path): Папка в которую копируются файлы.
        """
        if dst.exists():
            shutil.rmtree(path=dst)
            logger.debug("Сохранение в папке %s удалено", dst)

        shutil.copytree(src, dst)
        logger.debug("Сохранение перемещено из папки %s, в папку %s", src, dst)
