import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured JSON logging for the application."""
    logger = logging.getLogger("write_flow")
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times if initialization is called repeatedly
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            timestamp=True
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
