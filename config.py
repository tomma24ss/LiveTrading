# config.py

API_KEY = "W6ExGwLORN6bhkQGobceWZbs2blozgXG8oI5PAlJDmOV3gKg6Rx0LOdskBDb3EqV"
SECRET_KEY = "631UzythueU17d2GSuUc3KBPSRjnR9ADiRejkpm2KUBjkj6oA96V99VAe3GOLOJo"
TESTNET = False  # Set to False for live trading

# Trading Parameters
LIVE_SYMBOL = "BTCUSD"
STOP_LOSS = 0.02
PROFIT_TARGET = 0.05
SHORT_WINDOW = 100
LONG_WINDOW = 400
ENABLE_LONGING = True
ENABLE_SHORTING = True
LEVERAGE = 5

# Logging Configuration
LOG_FOLDER = './logs'
LOG_FILE = f"{LOG_FOLDER}/trading_bot.log"
LOG_LEVEL = 'DEBUG'
