import psutil
import time

from core.utils import get_process_by_name
from core.exceptions import (
    ProcessNotFoundError,
    ProcessAccessError,
    ProcessWaitTimeoutError,
    ProcessIsDeadError,
)


class NoitaProcess:
    """
    Легкая кросс-платформенная обертка над работающим процессом в операционной системе:
    - Поиск и оборачивание работающего процесса
    - Предоставляет информацию о процессе: cmdline, cwd, pid
    - Позволяет проверить статус процесса
    - Кросс-платформенная реализация завершения
    """

    def __init__(self, process: psutil.Process):
        if not process.is_running():
            raise ProcessIsDeadError(
                "Невозможно обернуть для использования уже завершенный процесс"
            )

        self._process = process
        self.pid = process.pid

        try:
            self.cmdline = process.cmdline()
            self.cwd = process.cwd()
        except (
            psutil.ZombieProcess,
            psutil.AccessDenied,
            psutil.NoSuchProcess,
        ) as e:
            raise ProcessAccessError(
                "Не удалось получить доступ к информации процесса"
            ) from e

    # Стандартное кросс-платформенное завершение процесса.
    def terminate(self, force: bool = False) -> None:
        """
        Завершает связанный процесс Ноиты в операционной системе.

        Args:
            force (bool, optional): Если True - процесс будет убит через kill.
                Defaults to False.
        """
        if force:
            self._process.kill()
            return

        self._process.terminate()

    def wait_for_terminate(self, timeout: float = 5) -> int:
        """
        Ожидает завершения процесса до истечения времени timeout.

        Args:
            timeout (float, optional): Максимальное время (в секундах) ожидания завершения
                процесса. Defaults to 5.

        Raises:
            ProcessWaitTimeoutError: Если по истечению времени ожидания процесс не вернет exit code.
            ValueError: В случае недопустимого значения timeout.

        Returns:
            int: Exit code завершенного процесса.
        """
        if timeout <= 0:
            raise ValueError("Недопустимый параметр timeout")

        try:
            return self._process.wait(timeout)
        except psutil.TimeoutExpired:
            raise ProcessWaitTimeoutError("Процесс не завершился за отведенное время.")

    @classmethod
    def attach(
        cls,
        name: str = "noita.exe",
        wait: bool = False,
        retries: int = 20,
        delay: float = 0.33,
    ) -> "NoitaProcess":
        """
        Ищет работающий процесс Ноиты по имени и оборачивает его в NoitaProcess. Если процесс не найден - выбрасывается исключение.

        Args:
            name (str, optional): Название процесса Ноиты для поиска. Обычно не стоит это менять.
                Defaults to "noita.exe".
            wait (bool, optional): Если True, поиск процесса будет продолжаться до истечения
                максимального количества попыток. Defaults to False.
            retries (int, optional): Максимальное количество попыток, когда 'wait' = True.
                Должно быть >= 1. Defaults to 20.
            delay (float, optional): Время задержки между попытками (в секундах).
                Должно быть >= 0.1. Defaults to 0.33.

        Raises:
            ValueError: Если заданные значения 'retries' или 'delay' недопустимы.
            ProcessNotFoundError: Если процесс не найден.

        Returns:
            NoitaProcess: Класс-обертка над работающим процессом.
        """
        if retries < 1 or delay < 0.1:
            raise ValueError("Недопустимые параметры")

        attempts = retries if wait else 1

        for i in range(attempts):
            process = get_process_by_name(name)
            if process:
                return cls(process)

            if i < attempts - 1:
                time.sleep(delay)

        raise ProcessNotFoundError("Процесс Ноиты не найден")

    @property
    def is_alive(self) -> bool:
        """
        Возвращает статус процесса: работает/завершен.

        Returns:
            bool: True если процесс работает, иначе False.
        """
        try:
            return (
                self._process.is_running()
                and self._process.status() != psutil.STATUS_ZOMBIE
            )
        except psutil.NoSuchProcess:
            return False

    @property
    def _ps_process(self) -> psutil.Process:
        """
        Низкоуровневый доступ к psutil.Process объекту. Следует использовать только когда низкоуровневое взаимодействие оправдано.

        Returns:
            psutil.Process: Объект процесса.
        """
        return self._process
