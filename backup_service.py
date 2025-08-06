from pathlib import Path
from utils import has_files
import shutil
import logging


NOITA_SAVES_DIR = Path.home() / "AppData" / "LocalLow" / "Nolla_Games_Noita" / "save00"
BACKUP_SAVES_DIR = Path(__file__).parent / "backup" / "save00"


logger = logging.getLogger(__name__)


class BackupService:
    def __init__(
        self,
        saves_dir: Path = NOITA_SAVES_DIR,
        backup_dir: Path = BACKUP_SAVES_DIR,
    ):
        self._check_noita_save_dir_exists(saves_dir)
        self.saves_dir = saves_dir
        self.backup_dir = backup_dir

    def backup_saves(self) -> None:
        if not has_files(self.saves_dir):
            raise RuntimeError(
                f"Noita saves directory doesn't have any save files: {self.saves_dir} ",
            )

        if self.backup_dir.exists():
            shutil.rmtree(path=self.backup_dir)
            logger.info(
                "Previous backup at %s was removed",
                self.backup_dir,
            )

        shutil.copytree(src=self.saves_dir, dst=self.backup_dir)
        logger.info(
            "Save backup created at %s",
            self.backup_dir,
        )

    def restore_saves(self) -> None:
        if not has_files(self.backup_dir):
            raise RuntimeError(
                f"Try to restore save from empty backup directory: {self.backup_dir}",
            )
        if self.saves_dir.exists():
            shutil.rmtree(path=self.saves_dir)
            logger.info("Previous actual save at %s was removed", self.saves_dir)

        shutil.copytree(src=self.backup_dir, dst=self.saves_dir)
        logger.info(
            "Save was restored from backup at %s",
            self.backup_dir,
        )

    def _check_noita_save_dir_exists(
        self,
        saves_dir: Path,
    ) -> None:
        if not saves_dir.exists() or not saves_dir.is_dir():
            raise RuntimeError(
                f"Noita saves directory does not exist: {saves_dir}",
            )
