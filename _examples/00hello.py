from wlog import setup
from wlog import get_logger

setup()

logger = get_logger(__name__)
logger.bind(xxx="yyy").info("hello")
