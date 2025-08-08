class NoitaError(Exception):
    """Базовый класс исключений для всего приложения."""


class NotSupportedError(NoitaError):
    """Функционал не поддерживается в данной версии приложения."""


# -- УРОВЕНЬ ПРОЦЕССА
class NoitaProcessError(NoitaError):
    """Базовый класс исключений, связанных с процессом Noita."""


class ProcessNotFoundError(NoitaProcessError):
    """Процесс Noita не найден."""


class ProcessAccessError(NoitaProcessError):
    """Не удалось получить доступ к процессу."""


class ProcessWaitTimeoutError(NoitaProcessError):
    """Процесс не завершился за отведённое время."""


class ProcessIsDeadError(NoitaProcessError):
    """Попытка провести операцию над завершенным процессом."""


# -- УРОВЕНЬ МЕНЕДЖЕРА
class NoitaManagerError(NoitaError):
    """Базовый класс исключений, связанных с ошибками менеджера Noita."""


class ShutdownFailError(NoitaManagerError):
    """Проблема с закрытием Noita."""


class StartupFailError(NoitaManagerError):
    """Проблема с запуском Noita."""


# -- ПОИСК ИСПОЛНЯЕМОГО ФАЙЛА
class NoitaCmdlineResolverError(NoitaError):
    """Базовый класс исключений, связанных с ошибками поиска аргументов командной строки."""


class NoitaExecutableNotFound(NoitaCmdlineResolverError):
    """Не найден исполняемый файл Noita."""


# -- СПЕЦИФИЧНЫЕ ДЛЯ РАБОТЫ С БЭКАПАМИ
class BackupServiceError(NoitaError):
    """Базовый класс исключений, связанных с ошибками бэкап-сервиса Noita."""


class DirectoryNotExist(BackupServiceError):
    """Папка с бэкапом/актуальными сохранениями не существует."""


class EmptyDirectoryError(BackupServiceError):
    """Попытка перенести данные из пустой папки."""
