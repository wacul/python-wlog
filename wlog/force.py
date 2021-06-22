from ._logger import setup, get_logger

setup()
get_logger(__name__).debug("setup logging")
