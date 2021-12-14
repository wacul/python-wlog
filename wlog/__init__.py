from wlog._logger import get_logger
from wlog._logger import setup
from wlog._logger import suppress_logging

getLogger = get_logger  # backward comapatibility of python stdlib

# sample output is here
# AIA_LOG_FORMART=text python <file.py>
# AIA_LOG_LEVEL=debug AIA_LOG_FORMAT=text AIA_LOG_STREAM=stderr python <file.py>
# python <file.py>

__all__ = ["setup", "get_logger", "suppress_logging"]
