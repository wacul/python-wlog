from wlog import setup
from wlog import get_logger

setup()

logger = get_logger(__name__)
logger.bind(xxx="yyy").debug("this is debug print message")
logger.bind(xxx="yyy").info("this is info print message")
logger.bind(xxx="yyy").warning("this is warning print message")
logger.bind(xxx="yyy").error("this is error print message")
logger.bind(xxx="yyy").critical("this is critical print message")  # not used
