class WindowsCloser:
    """
    Класс для поиска и отправки сообщения WM_CLOSE окнам заданного процесса Windows по его PID. Класс импортирует Windows-специфичные модули из библиотеки pywin.

    Содержит флаг завершения процесса success_close.
    """

    def __init__(self):
        import win32con
        import win32gui
        import win32process
        import logging

        self._logger = logging.getLogger(name="windows_closer")

        self._gui = win32gui
        self._con = win32con
        self._prc = win32process

        self.success_close = False

    def close_window(self, target_pid: int) -> None:
        """
        Убирает прошлое значение флага завершения и пытается закрыть окна процесса с 'target_pid'.

        Args:
            target_pid (int): PID-процесса.
        """
        self.success_close = False

        # Итерируется по всем окнам.
        self._gui.EnumWindows(self, target_pid)

    def __call__(self, hwnd: int, lparam: int) -> bool:
        """
        Callback-функция для EnumWindows.

        Проверяет, принадлежит ли окно процессу с PID = lparam, и является ли окно видимым. Если да - отправляет сообщение WM_CLOSE окну и прерывает дальнейший обход окон.

        Args:
            hwnd (int): Дескриптор текущего окна.
            lparam (int): PID целевого процесса, переданный через EnumWindows.

        Returns:
            bool: False для прекращения обхода после успешного закрытия окна. True для продолжения обхода.
        """
        try:
            _, win_pid = self._prc.GetWindowThreadProcessId(hwnd)
            if win_pid == lparam and self._gui.IsWindowVisible(hwnd):
                self._gui.PostMessage(hwnd, self._con.WM_CLOSE, 0, 0)
                self.success_close = True
                return False
        except Exception as e:
            # Игнорируются специфичные исключения, т.к. логика приложения не завязана на этом. Пока что просто пишется в лог.
            self._logger.warning("Ошибка при обработке окна HWND=%s: %s", hwnd, e)
            pass
        return True
