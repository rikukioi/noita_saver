import platform
import psutil
import subprocess
import time
import logging
from utils import get_process_by_name

if platform.system() == "Windows":
    import win32gui  # type: ignore
    import win32con  # type: ignore
    import win32process  # type: ignore


PROCESS_NAME = "noita.exe"
TIMEOUT_TO_GRACEFULLY = 10
MAX_RETRIES = 20
RETRY_DELAY = 0.2


logger = logging.getLogger(__name__)


class NoitaProcess:
    def __init__(self):
        self.noita = self._find_noita_process()

        try:
            # This data needs to be retrieved once because it usually not changing during gameplay.
            self.noita_cmd = self.noita.cmdline()
            self.noita_cwd = self.noita.cwd()
        except (psutil.AccessDenied, psutil.ZombieProcess) as e:
            raise RuntimeError("Can't retrieve command line or cwd for Noita") from e

        if not self.noita_cmd:
            raise RuntimeError("Can't retrieve command line for Noita")

    def start_noita(self) -> None:
        logger.info(
            "Noita starting with cmd: %s, cwd: %s",
            self.noita_cmd,
            self.noita_cwd,
        )
        try:
            subprocess.Popen(
                self.noita_cmd,
                cwd=self.noita_cwd,
            )
        except Exception as e:
            raise RuntimeError("Failed to start Noita") from e

        self.noita = self._wait_for_process_restart()
        logger.info("Noita successfully started")

    def terminate_noita(self) -> None:
        if not self._is_process_alive():
            logger.warning(
                "Noita already terminated",
            )
            return

        logger.info("Attempting to terminate Noita")

        if platform.system() == "Windows":
            self._graceful_terminate_windows()
        else:
            self._hard_terminate()

    def _graceful_terminate_windows(self) -> None:
        def enum_windows_callback(hwnd, pid):
            try:
                _, win_pid = win32process.GetWindowThreadProcessId(hwnd)
                if win_pid == pid and win32gui.IsWindowVisible(hwnd):
                    logger.info(
                        "Sending WM_CLOSE to Noita window (HWND: %s)",
                        hwnd,
                    )
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            except Exception as e:
                raise RuntimeError("Failed to gracefully close Noita window") from e

        win32gui.EnumWindows(enum_windows_callback, self.noita.pid)

        try:
            self.noita.wait(timeout=TIMEOUT_TO_GRACEFULLY)
            logger.info("Noita terminated gracefully")
        except psutil.TimeoutExpired:
            logger.warning("Graceful close timeout expired")
            raise RuntimeError("Can't close Noita window gracefully")

    def _hard_terminate(self) -> None:
        self.noita.terminate()
        try:
            self.noita.wait(timeout=TIMEOUT_TO_GRACEFULLY)
            logger.info(
                "Noita hard-terminated succesfully",
            )

        except psutil.TimeoutExpired:
            self.noita.kill()
            logger.warning(
                "Noita process killed, because timeout expired",
            )

    def _is_process_alive(self) -> bool:
        return self.noita.is_running() and self.noita.status() != psutil.STATUS_ZOMBIE

    def _find_noita_process(self) -> psutil.Process:
        process = get_process_by_name(PROCESS_NAME)
        if not process:
            raise RuntimeError("Noita is not running")

        logger.info(
            "Noita process found, PID: %s",
            process.pid,
        )
        return process

    def _wait_for_process_restart(self) -> psutil.Process:
        for _ in range(MAX_RETRIES):
            time.sleep(RETRY_DELAY)
            process = get_process_by_name(PROCESS_NAME)
            if process:
                logger.info(
                    "Noita process successfully restarted, PID: %s",
                    process.pid,
                )
                return process

        raise RuntimeError("Failed to find new instance of process Noita")
