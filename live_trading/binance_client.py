import sys
import os

# Dynamically adjust the path to include the utils directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger import logger
import ccxt


class BinanceClient:
    def __init__(self, api_key, secret_key):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            # 'enableRateLimit': True,
            # 'options': {
            #     'defaultType': 'future'  # Enable Futures Trading
            # }
        })
        self.exchange.load_markets()
        # self.exchange.verbose = True  # uncomment this line if it doesn't work
        
        logger.info("✅ Binance Futures Client initialized.")


    def set_leverage(self, symbol: str, leverage: int):
        """
        Set leverage for a trading pair in Binance Futures.
        """
        try:
            response = self.exchange.set_leverage(
                leverage=leverage,
                symbol=symbol.replace('/', '')
            )
            logger.info(f"✅ Leverage set to {leverage}x for {symbol}.")
            return response
        except Exception as e:
            logger.error(f"❌ Failed to set leverage: {e}")
            raise

    def get_ticker(self, symbol: str):
        """Get the latest market data for a symbol."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            logger.info(f"📊 Fetched ticker for {symbol}: {ticker['last']}")
            return ticker
        except Exception as e:
            logger.error(f"❌ Failed to fetch ticker: {e}")
            raise

    def create_order(self, symbol: str, order_type: str, side: str, amount: float, price: float = None):
        """
        Place an order on Binance Futures.
        """
        try:
            params = {
                # 'test': True
            }

            if order_type == 'LIMIT' and price:
                order = self.exchange.create_order(
                    symbol=symbol,
                    type=order_type,
                    side=side,
                    amount=amount,
                    price=price,
                    params=params
                )
            else:
                order = self.exchange.create_order(
                    symbol=symbol,
                    type='market',
                    side=side,
                    amount=amount,
                    params=params
                )

            logger.info(f"✅ Order successfully placed: {order}")
            return order
        except Exception as e:
            logger.error(f"❌ Failed to place order: {e}")
            raise
        
    def get_balance(self, symbol):
        """Fetch and print all wallet balances where the total is greater than 0."""
        try:
            # Fetch balance from the exchange
            balance = self.exchange.fetch_balance()
            
            extrected_balance = balance.get(symbol, {}).get('free', 0)
            return extrected_balance
    
        except Exception as e:
            logger.error(f"❌ Failed to fetch wallet balances: {e}")
            raise


    def get_historical_klines(self, symbol: str, interval: str = '1m', limit: int = 1200):
        """
        Fetch historical OHLCV data.
        """
        try:
            logger.info(f"📥 Fetching historical data for {symbol}, interval {interval}, limit {limit}...")
            ohlcv = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=interval,
                limit=limit
            )

            historical_data = []
            for entry in ohlcv:
                historical_data.append({
                    'timestamp': entry[0],
                    'open': entry[1],
                    'high': entry[2],
                    'low': entry[3],
                    'close': entry[4],
                    'volume': entry[5]
                })

            logger.info("✅ Successfully fetched historical data.")
            return historical_data
        except Exception as e:
            logger.error(f"❌ Failed to fetch historical data: {e}")
            raise

    def get_server_time(self):
        """
        Fetch the server time from Binance.
        """
        try:
            server_time = self.exchange.fetch_time()
            logger.info(f"🕒 Binance server time: {server_time}")
            return server_time
        except Exception as e:
            logger.error(f"❌ Failed to fetch server time: {e}")
            raise


# 🔗 Boilerplate code to test API connectivity
if __name__ == "__main__":
    from config import API_KEY, SECRET_KEY
    
    if not API_KEY or not SECRET_KEY:
        raise ValueError("❌ API_KEY and SECRET_KEY environment variables must be set.")
    
    try:
        client = BinanceClient(api_key=API_KEY, secret_key=SECRET_KEY)

        # Test Connectivity
        logger.info("🔗 Testing Binance API connectivity...")
        server_time = client.get_server_time()
        balance = client.get_balance()
        ticker = client.get_ticker('BTC/USDT')

        print("\n✅ Binance API Test Successful:")
        print(f"🕒 Server Time: {server_time}")
        print(f"💰 Balance: {balance} EUR")
        print(f"📊 BTC/USDT Ticker Last Price: {ticker['last']}")

    except Exception as e:
        logger.error(f"❌ API Test failed: {e}")