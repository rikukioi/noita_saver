import platform
import subprocess
import logging

from services.noita_process import NoitaProcess
from services.closers import WindowsCloser
from core.exceptions import (
    ProcessWaitTimeoutError,
    ProcessNotFoundError,
    ShutdownFailError,
    StartupFailError,
)


TIMEOUT_TO_GRACEFULLY = 10

logger = logging.getLogger(__name__)


class NoitaManager:
    """
    Менеджер для управления процессом игры Noita:
    - запуск через psutil.Popen с использованием аргументов командной строки
    - корректное завершение средствами специфичной ОС или принудительное завершение
    - проверка состояния процесса
    """

    def __init__(
        self,
        noita_cmdline: list[str] | None = None,
        cwd: str | None = None,
    ):
        self._launch_cmdline = noita_cmdline
        self._cwd = cwd

    def launch_noita(self) -> None:
        """
        Запускает игру и ожидает её появления в списке процессов.

        Raises:
            StartupFailError: Если игра уже запущена или запуск не удался.
        """
        if not self._launch_cmdline or not self._cwd:
            raise StartupFailError("Нет командной строки для запуска процесса.")
        if self._check_noita_running():
            raise StartupFailError("Процесс игры уже запущен.")

        logger.debug("Запуск процесса по командной строке: %s", self._launch_cmdline)

        try:
            subprocess.Popen(self._launch_cmdline, cwd=self._cwd)
            new_process = NoitaProcess.attach(wait=True)
        except Exception as e:
            raise StartupFailError("Не удалось запустить процесс игры.") from e

        logger.debug("Процесс работает с PID: %s", new_process.pid)
        logger.info("Игра успешно запущена.")

    def shutdown_noita(self) -> None:
        """
        Завершает игру, используя доступные для ОС методы.

        Raises:
            ShutdownFailError: Если процесс не найден или не завершился вовремя.
        """
        if not (running_noita := self._check_noita_running()):
            raise ShutdownFailError(
                "Попытка остановить процесс игры, когда таких процессов в операционной системе нет."
            )

        logger.debug("Попытка завершить процесс игры с PID: %s", running_noita.pid)

        if platform.system() == "Windows":
            self._graceful_terminate_windows(pid=running_noita.pid)
        else:
            self._soft_terminate(process_to_terminate=running_noita)

        # Ожидание завершения
        try:
            running_noita.wait_for_terminate(timeout=TIMEOUT_TO_GRACEFULLY)
        except ProcessWaitTimeoutError as e:
            raise ShutdownFailError(
                "Истекло время ожидания на завершение процесса игры."
            ) from e

        # Для дальнейшего запуска
        self._launch_cmdline = running_noita.cmdline
        self._cwd = running_noita.cwd

        logger.info("Процесс игры завершен успешно.")

    def _check_noita_running(self) -> NoitaProcess | None:
        """
        Проверяет наличие процесса игры.

        Returns:
            (NoitaProcess | None): Объект процесса, если найден; иначе None.
        """
        try:
            noita = NoitaProcess.attach()
            return noita
        except ProcessNotFoundError:
            return None

    def _graceful_terminate_windows(self, pid) -> None:
        closer = WindowsCloser()
        closer.close_window(target_pid=pid)
        if not closer.success_close:
            logger.warning("Не удалось завершить процесс игры средствами Windows API.")

    def _hard_terminate(self, process_to_terminate: NoitaProcess) -> None:
        process_to_terminate.terminate(force=True)

    def _soft_terminate(self, process_to_terminate: NoitaProcess) -> None:
        process_to_terminate.terminate()
