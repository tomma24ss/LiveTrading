# main.py

from live_trading.live_trader import LiveTrader
from config import API_KEY, SECRET_KEY, TESTNET, LIVE_SYMBOL, STOP_LOSS, PROFIT_TARGET, SHORT_WINDOW, LONG_WINDOW, ENABLE_LONGING, ENABLE_SHORTING, LEVERAGE

if __name__ == '__main__':
    # Initialize and Start Live Trader
    trader = LiveTrader({
        'API_KEY': API_KEY,
        'SECRET_KEY': SECRET_KEY,
        'TESTNET': TESTNET,
        'STOP_LOSS': STOP_LOSS,
        'PROFIT_TARGET': PROFIT_TARGET,
        'SHORT_WINDOW': SHORT_WINDOW,
        'LONG_WINDOW': LONG_WINDOW,
        'ENABLE_LONGING': ENABLE_LONGING,
        'ENABLE_SHORTING': ENABLE_SHORTING,
        'LIVE_SYMBOL': LIVE_SYMBOL,
        'LEVERAGE': LEVERAGE
    })

    # Run the Trader
    trader.run()
