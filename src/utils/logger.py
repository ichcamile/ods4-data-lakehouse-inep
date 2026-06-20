import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger configured with a standard console output format.
    """
    logger = logging.getLogger(name)
    
    # If logger already has handlers, return it to avoid duplicate logs
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
