# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
TESTNET = os.getenv('TESTNET') == 'True'

# Trading Parameters
LIVE_SYMBOL = os.getenv('LIVE_SYMBOL')
STOP_LOSS = float(os.getenv('STOP_LOSS'))
PROFIT_TARGET = float(os.getenv('PROFIT_TARGET'))
SHORT_WINDOW = int(os.getenv('SHORT_WINDOW'))
LONG_WINDOW = int(os.getenv('LONG_WINDOW'))
ENABLE_LONGING = os.getenv('ENABLE_LONGING') == 'True'
ENABLE_SHORTING = os.getenv('ENABLE_SHORTING') == 'True'
LEVERAGE = int(os.getenv('LEVERAGE'))

# Logging Configuration
LOG_FOLDER = os.getenv('LOG_FOLDER')
LOG_FILE = os.getenv('LOG_FILE')
LOG_LEVEL = os.getenv('LOG_LEVEL')
