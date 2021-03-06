# from https://github.com/velebit-ai/useful-logs
from ._logger import get_logger

logger = get_logger("wlog.exception_hooks")  # TODO: rename


def except_logging(exc_type, exc_value, exc_traceback):
    """
    Log uncaught exceptions using the root logger. This is a function meant to
    be set as `sys.excepthook` to provide unified logging for regular logs and
    uncaught exceptions.

    Args:
        exc_type (type): Exception type
        exc_value (Exception) : Exception value
        exc_traceback (traceback): Exception traceback
    """
    logger.bind(exception=exc_value).error(
        f"Uncaught exception: {exc_value!r}",
    )


def threading_except_logging(exc_type, exc_value=None, exc_traceback=None, thread=None):
    """
    Log uncaught exceptions from different threads using the root logger. This
    is a function meant to be set as `threading.excepthook` to provide unified
    logging for regular logs and uncaught exceptions from different threads.

    Note: Only supported since Python version 3.8

    Args:
        exc_type (type): Exception type
        exc_value (Exception): Exception value, can be None. Defaults to None
        exc_traceback (traceback): Exception traceback, can be None. Defaults
            to None
        thread (threading.Thread): Thread which raised the exception, can be
            None. Defaults to None
    """
    logger.bind(exception=exc_value).error(
        f"Uncaught threading exception: {exc_value!r}",
    )


def unraisable_logging(
    exc_type, exc_value=None, exc_traceback=None, err_msg=None, object=None
):
    """
    Log unraisable exceptions using the root logger. This is a function meant
    to be set as `sys.unraisablehook` to provide unified logging for regular
    logs and unraisable exceptions.

    Args:
        exc_type (type): Exception type
        exc_value (Exception): Exception value, can be None. Defaults to None
        exc_traceback (traceback): Exception traceback, can be None. Defaults
            to None
        err_msg (str): Error message, can be None. Defaults to None
        object (object): Object causing the exception, can be None. Defaults to
            None
    """
    logger.bind(exception=exc_value).error(
        f"Unraisable exception: {exc_value!r}",
    )
