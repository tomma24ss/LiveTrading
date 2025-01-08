# utils/logger.py
import logging
import os
from config import LOG_FOLDER, LOG_FILE, LOG_LEVEL

# Ensure the log folder exists
os.makedirs(LOG_FOLDER, exist_ok=True)

# Map LOG_LEVEL string to actual logging level
LOG_LEVEL_MAPPING = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Default to DEBUG if LOG_LEVEL is not valid
log_level = LOG_LEVEL_MAPPING.get(LOG_LEVEL, logging.DEBUG)

# Create the logger
logger = logging.getLogger('TradingBotLogger')
logger.setLevel(logging.DEBUG)  # Set the base level to DEBUG

# File Handler (DEBUG logs written to file, overwrites each run)
file_handler = logging.FileHandler(LOG_FILE, mode='w')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)

# Console Handler (INFO logs shown on console)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(console_formatter)

# Add Handlers to Logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Initial Log Message
logger.info(f"Logger initialized with file level: DEBUG and console level: INFO")
