import logging

def get_logger(name):
    """
    """
    log = logging.getLogger(name)
    log.addHandler(logging.NullHandler())
    return log