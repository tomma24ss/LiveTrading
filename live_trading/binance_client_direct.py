import sys
import os

# Dynamically adjust the path to include the utils directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger import logger
from binance.cm_futures import CMFutures
from binance.error import ClientError


class BinanceClient:
    def __init__(self, api_key, secret_key, testnet=True):
        """
        Initialize Binance CM Futures Client.
        """
        base_url = "https://testnet.binancefuture.com" if testnet else "https://dapi.binance.com"
        self.client = CMFutures(key=api_key, secret=secret_key, base_url=base_url)
        logger.info("✅ Binance CM Futures Client initialized.")
        self.get_balance()

    def set_leverage(self, symbol: str, leverage: int):
        """
        Set leverage for a trading pair in Binance Futures.
        """
        try:
            response = self.client.change_leverage(symbol=symbol, leverage=leverage)
            logger.info(f"✅ Leverage set to {leverage}x for {symbol}. Response: {response}")
            return response
        except ClientError as e:
            logger.error(f"❌ Failed to set leverage: {e.error_message}")
            raise

    def get_ticker(self, symbol: str):
        """
        Get the latest market data for a symbol.
        """
        try:
            ticker = self.client.ticker_price(symbol=symbol)
            logger.info(f"📊 Fetched ticker for {symbol}: {ticker['price']}")
            return ticker
        except ClientError as e:
            logger.error(f"❌ Failed to fetch ticker: {e.error_message}")
            raise

    def create_order(self, symbol: str, order_type: str, side: str, amount: float, price: float = None, leverage: int = 1):
        """
        Place an order on Binance Futures.
        """
        try:
            self.set_leverage(symbol, leverage)

            order_params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': amount
            }

            if order_type.upper() == 'LIMIT' and price:
                order_params['price'] = price
                order_params['timeInForce'] = 'GTC'

            order = self.client.new_order(**order_params)
            logger.info(f"✅ Order successfully placed: {order}")
            return order
        except ClientError as e:
            logger.error(f"❌ Failed to place order: {e.error_message}")
            raise

    def close_position(self, symbol: str, side: str, amount: float):
        """
        Close an existing Futures position.
        """
        try:
            order = self.client.new_order(
                symbol=symbol,
                side=side.upper(),
                type='MARKET',
                quantity=amount
            )
            logger.info(f"✅ Position closed successfully: {order}")
            return order
        except ClientError as e:
            logger.error(f"❌ Failed to close position: {e.error_message}")
            raise

    def get_balance(self):
        """
        Fetch Futures wallet balance.
        """
        try:
            response = self.client.account()
            balance = next(
                (item for item in response['assets'] if item['asset'] == 'BTC'),
                {'availableBalance': 0}
            )
            futures_balance = balance.get('availableBalance', 0)
            logger.info(f"💰 Futures wallet balance: {futures_balance} BTC")
            return futures_balance
        except ClientError as e:
            logger.error(f"❌ Failed to fetch balance: {e.error_message}")
            raise

    def cancel_order(self, symbol: str, order_id: str):
        """
        Cancel an open order.
        """
        try:
            result = self.client.cancel_order(symbol=symbol, orderId=order_id)
            logger.info(f"✅ Order {order_id} canceled successfully: {result}")
            return result
        except ClientError as e:
            logger.error(f"❌ Failed to cancel order: {e.error_message}")
            raise

    def get_historical_klines(self, symbol: str, interval: str = '1m', limit: int = 1000):
        """
        Fetch historical OHLCV data.
        """
        try:
            logger.info(f"📥 Fetching historical data for {symbol}, interval {interval}, limit {limit}...")
            ohlcv = self.client.klines(
                symbol=symbol,
                interval=interval,
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
        except ClientError as e:
            logger.error(f"❌ Failed to fetch historical data: {e.error_message}")
            raise

    def get_server_time(self):
        """
        Fetch the server time from Binance.
        """
        try:
            server_time = self.client.time()
            logger.info(f"🕒 Binance server time: {server_time['serverTime']}")
            return server_time['serverTime']
        except ClientError as e:
            logger.error(f"❌ Failed to fetch server time: {e.error_message}")
            raise


# 🔗 Boilerplate code to test API connectivity
if __name__ == "__main__":
    from config import API_KEY, SECRET_KEY, LIVE_SYMBOL

    if not API_KEY or not SECRET_KEY:
        raise ValueError("❌ API_KEY and SECRET_KEY environment variables must be set.")
    
    if not LIVE_SYMBOL:
        raise ValueError("❌ LIVE_SYMBOL must be defined in the config.")

    try:
        client = BinanceClient(api_key=API_KEY, secret_key=SECRET_KEY, testnet=True)

        # Test Connectivity
        logger.info("🔗 Testing Binance CM Futures API connectivity...")
        server_time = client.get_server_time()
        balance = client.get_balance()
        ticker = client.get_ticker(LIVE_SYMBOL)

        print("\n✅ Binance API Test Successful:")
        print(f"🕒 Server Time: {server_time}")
        print(f"💰 Balance: {balance} BTC")
        print(f"📊 {LIVE_SYMBOL} Ticker Last Price: {ticker['price']}")

    except ClientError as e:
        logger.error(f"❌ API Test failed: {e.error_message}")
