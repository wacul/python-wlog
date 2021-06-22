"""
loggingの設定

- JSONで出力。pythonのloggingライブラリとは互換性が全くない
- エラーの時にstackにstack traceを保存
- TODO: structlogを捨てて書き換える
"""

import logging
import traceback
import sys
import os.path
from collections import OrderedDict
from datetime import datetime, timezone, timedelta

import structlog

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
NAME_TO_LEVEL = logging._nameToLevel


def processor_basic_information(
    logger, name, event_dict, *, tz=timezone(timedelta(hours=+9), "JST")
):
    event_dict["time"] = datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    event_dict["level"] = name
    return event_dict


def processor_find_caller_information(depth=4, homedir=None):
    def processor(logger, name, event_dict):
        f = sys._getframe(depth)
        # On some versions of IronPython, currentframe() returns None if
        # IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            sinfo = None
            filename = os.path.abspath(os.path.normcase(co.co_filename))
            if homedir is not None:
                filename = filename.replace(homedir, "~")
            rv = (filename, f.f_lineno, co.co_name, sinfo)
            break

        # add to dict
        event_dict["caller"] = "{}:{}".format(rv[0], rv[1])
        # event_dict["fn"] = rv[2]  # function name
        return event_dict

    return processor


def processor_oneline_on_exception(src):
    def processor(logger, name, event_dict):
        exc = event_dict.pop(src, None)
        if exc:
            event_dict[src] = repr(traceback.format_exc(chain=False, limit=1))
        return event_dict

    return processor


def processor_stack_on_exception(src, dst):
    def processor(logger, name, event_dict):
        exc = event_dict.pop(src, None) or event_dict.get("exc_info")
        exc_info = structlog.processors._figure_out_exc_info(exc)
        if exc_info:
            exc = structlog.processors._format_exception(exc_info)
        if exc:
            event_dict[dst] = str(exc).splitlines()
        return event_dict

    return processor


def processor_rename_key_value(src, dst):
    def processor(logger, name, event_dict):
        if src in event_dict:
            event_dict[dst] = event_dict.pop(src, None)
        return event_dict

    return processor


_loggers = []
_level = logging.INFO


def get_logger(name, *args, **kwargs):
    logger = structlog.get_logger(name, source=name)
    _loggers.append(logger)
    return logger


def processor_filter_by_level(logger, name, event_dict):
    global _level
    level = NAME_TO_LEVEL.get(name.upper()) or 0
    if level >= _level:
        return event_dict
    else:
        raise structlog.DropEvent


def _get_default_renderer():
    if os.environ.get("AIA_LOG_FORMAT", "").lower() == "text":
        return _ConsoleRenderer()
    else:
        return structlog.processors.JSONRenderer()


class _ConsoleRenderer(structlog.dev.ConsoleRenderer):
    def __call__(self, _, __, event_dict):
        from io import StringIO

        sio = StringIO()

        # suppress verbose
        event_dict.pop("caller", None)

        ts = event_dict.pop("timestamp", None)
        if ts is not None:
            sio.write(
                # can be a number if timestamp is UNIXy
                self._styles.timestamp
                + str(ts)
                + self._styles.reset
                + " "
            )
        level = event_dict.pop("level", None)
        if level is not None:
            sio.write(
                "["
                + self._level_to_color[level]
                + _pad(level, self._longest_level)
                + self._styles.reset
                + "] "
            )

        event = event_dict.pop("event", None) or event_dict.pop("msg")
        if event_dict:
            event = _pad(event, self._pad_event) + self._styles.reset + " "
        else:
            event += self._styles.reset
        sio.write(self._styles.bright + event)

        logger_name = event_dict.pop("logger", None)
        if logger_name is not None:
            sio.write(
                "["
                + self._styles.logger_name
                + self._styles.bright
                + logger_name
                + self._styles.reset
                + "] "
            )

        stack = event_dict.pop("stack", None)
        exc = event_dict.pop("exception", None)
        sio.write(
            " ".join(
                self._styles.kv_key
                + key
                + self._styles.reset
                + "="
                + self._styles.kv_value
                + self._repr(event_dict[key])
                + self._styles.reset
                for key in sorted(event_dict.keys())
            )
        )

        if stack is not None:
            sio.write("\n" + stack)
            if exc is not None:
                sio.write("\n\n" + "=" * 79 + "\n")
        if exc is not None:
            sio.write("\n" + exc)

        return sio.getvalue()


def _pad(s, l):
    """
    Pads *s* to length *l*.
    """
    missing = l - len(s)
    return s + " " * (missing if missing > 0 else 0)


# yapf: disable
DEFAULT_PROCESSORS = [
    processor_filter_by_level,
    processor_find_caller_information(depth=3, homedir=os.environ.get("HOME", None)),
    processor_basic_information,
    processor_oneline_on_exception("oneline_exception"),
    processor_stack_on_exception("exception", "stack"),
    processor_rename_key_value("event", "msg"),
    structlog.processors.StackInfoRenderer(),
    _get_default_renderer(),
]
# yapf: enable


def make_ordered_context(*args, **kwargs):
    d = OrderedDict()
    d["time"] = ""
    d["level"] = ""
    d["msg"] = ""
    d["caller"] = ""
    d["source"] = ""
    if args or kwargs:
        d.update(dict(*args, **kwargs))
    return d


def suppress_logging():
    for logger in _loggers:
        if logger._logger is not None:
            logger._logger.__class__ = structlog.ReturnLogger
    structlog.configure(logger_factory=lambda *args, **kwargs: structlog.ReturnLogger())


def setup(level=None, context_class=None, processors=None, **kwargs):
    if level is None:
        level = os.environ.get("AIA_LOG_LEVEL")
    if level is not None:
        level = level.upper()

    kwargs["context_class"] = context_class or make_ordered_context
    kwargs["processors"] = processors or DEFAULT_PROCESSORS
    structlog.configure(**kwargs)

    if level is not None:
        logging.basicConfig(level=level)
        set_loglevel(level)

    # setup sys hooks
    from ._exception_hooks import (
        except_logging,
        unraisable_logging,
        threading_except_logging,
    )

    # log uncaught exceptions using this logger configuration. This way we can
    # have every important python output in JSON format without the need for
    # multiline parsing afterwards
    sys.excepthook = except_logging
    sys.unraisablehook = unraisable_logging

    # Note: threading.excepthook is only supported since Python 3.8
    if sys.version_info >= (3, 8, 0):
        import threading

        threading.excepthook = threading_except_logging

    # Note: multiprocessing.Process still doesn't use sys.excepthook, so in
    # order to make it work, you need to implement a custom Process and
    # override Process.run method to make the old stdio output obsolete, catch
    # all exceptions and call sys.excepthook on them
    return None


def set_loglevel(level):
    global _level
    if isinstance(level, str):
        level = NAME_TO_LEVEL[level.upper()]
    _level = level


stdout_logger_factory = structlog.PrintLoggerFactory(sys.stdout)
stderr_logger_factory = structlog.PrintLoggerFactory(sys.stderr)
