import logging as lg

def getLogger(name: str, level: str = 'WARNING') -> lg.Logger:
    """
    Returns a logger with the given name and level.

    Args:
        name (str): The name of the logger.
        level (str): The logging level. Defaults to 'WARNING'.

    Returns:
        logging.Logger: The logger object.
    """
    logger = lg.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(lg.StreamHandler())
    return logger
