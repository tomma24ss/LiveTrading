from utils.logger import logger
from binance.exceptions import BinanceAPIException, BinanceOrderException


class OrderManager:
    def __init__(self, client):
        """
        OrderManager to handle Futures orders via BinanceClient.
        :param client: BinanceClient instance.
        """
        self.client = client

    def set_leverage(self, symbol: str, leverage: int):
        """
        Set leverage for a given trading pair.
        """
        try:
            self.client.set_leverage(symbol, leverage)
            logger.info(f"✅ Leverage set to {leverage}x for {symbol}.")
        except BinanceAPIException as e:
            logger.error(f"❌ Failed to set leverage: {e}")
            raise

    def place_order(self, symbol: str, side: str, quantity: float, order_type: str = 'MARKET', price: float = None, leverage: int = 1):
        """
        Place an order on Binance Futures.
        
        :param symbol: Trading pair (e.g., 'BTC/USDT')
        :param side: BUY (Long) or SELL (Short)
        :param quantity: Quantity to trade
        :param order_type: MARKET or LIMIT
        :param price: Price for LIMIT orders
        :param leverage: Leverage level
        :return: Order details
        """
        try:
            # Set Leverage
            # self.set_leverage(symbol, leverage)
            
            # Place Order via BinanceClient
            order = self.client.create_order(
                symbol=symbol,
                order_type=order_type,
                side=side,
                amount=quantity,
                price=price,
                leverage=leverage
            )

            logger.info(f"✅ Order successfully placed: {order}")
            return order

        except (BinanceAPIException, BinanceOrderException) as e:
            logger.error(f"❌ Failed to place order: {e}")
            raise

    def close_position(self, symbol: str, side: str, quantity: float):
        """
        Close an open Futures position.
        
        :param symbol: Trading pair (e.g., 'BTC/USDT')
        :param side: Side to close position ('BUY' for SHORT, 'SELL' for LONG)
        :param quantity: Quantity to close
        """
        try:
            order = self.client.close_position(
                symbol=symbol,
                side=side,
                amount=quantity
            )
            logger.info(f"✅ Position closed successfully: {order}")
            return order
        except (BinanceAPIException, BinanceOrderException) as e:
            logger.error(f"❌ Failed to close position: {e}")
            raise

    def cancel_order(self, symbol: str, order_id: int):
        """
        Cancel an open order.
        
        :param symbol: Trading pair (e.g., 'BTC/USDT')
        :param order_id: ID of the order to cancel
        """
        try:
            self.client.cancel_order(symbol=symbol, order_id=order_id)
            logger.info(f"✅ Order {order_id} canceled successfully.")
        except BinanceAPIException as e:
            logger.error(f"❌ Failed to cancel order: {e}")
            raise

    def get_balance(self):
        """
        Fetch Futures wallet balance.
        :return: Free USDT balance
        """
        try:
            balance = self.client.get_balance()
            logger.info(f"💰 Futures wallet balance: {balance} USDT")
            return balance
        except BinanceAPIException as e:
            logger.error(f"❌ Failed to fetch balance: {e}")
            raise
