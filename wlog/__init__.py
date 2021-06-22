from wlog._logger import get_logger
from wlog._logger import setup  # noqa: F401
from wlog._logger import suppress_logging  # noqa: F401

getLogger = get_logger  # backward comapatibility of python stdlib

# sample output is here
# AIA_LOG_FORMART=text python <file.py>
# AIA_LOG_LEVEL=debug AIA_LOG_FORMAT=text python <file.py>
# python <file.py>
