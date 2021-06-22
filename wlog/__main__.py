# sample output is here
# AIA_LOG=text python <file.py>
# AIA_LOG_LEVEL=debug AIA_LOG=text python <file.py>
# python <file.py>

if __name__ == "__main__":
    from wlog._logger import get_logger
    from wlog._logger import setup

    setup()
    logger = get_logger(__name__)
    logger.bind(xxx="yyy").debug("this is debug print message")
    logger.bind(xxx="yyy").info("this is info print message")
    logger.bind(xxx="yyy").warning("this is warning print message")
    logger.bind(xxx="yyy").error("this is error print message")
    logger.bind(xxx="yyy").critical("this is critical print message")  # not used
