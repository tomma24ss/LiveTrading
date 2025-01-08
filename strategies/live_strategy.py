import pandas as pd
from utils.logger import logger
from enum import Enum


class Signal(Enum):
    BUY_LONG = "BUY_LONG"
    SELL_LONG = "SELL_LONG"
    BUY_SHORT = "BUY_SHORT"
    SELL_SHORT = "SELL_SHORT"
    STOP_LOSS_LONG = "STOP_LOSS_LONG"
    STOP_LOSS_SHORT = "STOP_LOSS_SHORT"
    HOLD = "HOLD"


class LiveStrategy:
    def __init__(self, stop_loss, profit_target, short_window, long_window, enable_longing=True, enable_shorting=True):
        self.stop_loss = stop_loss
        self.profit_target = profit_target
        self.short_window = short_window
        self.long_window = long_window
        self.enable_longing = enable_longing
        self.enable_shorting = enable_shorting

        # State Tracking
        self.position = None  # 'long', 'short', None
        self.entry_price = None
        self.data = pd.DataFrame()

        logger.info("✅ Live Strategy Initialized.")
        
        self.uptrend_triggered = False
        self.downtrend_triggered = False


    def prefill_data(self, historical_data):
        """
        Prefill the strategy data with historical data and calculate indicators.
        """
        logger.info("📥 Prefilling strategy with historical data...")
        try:
            df = pd.DataFrame(historical_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['close'] = df['close'].astype(float)

            # Copy data into strategy
            self.data = df[['timestamp', 'close']].copy()
            # Calculate indicators
            self.data['FAST_IND'] = self.data['close'].ewm(span=self.short_window, min_periods=1).mean()
            self.data['SLOW_IND'] = self.data['close'].ewm(span=self.long_window, min_periods=1).mean()
            logger.info("✅ Historical data successfully prefilled with indicators.")
        except Exception as e:
            logger.error(f"❌ Failed to prefill strategy data: {e}")
            raise



    def update_data(self, price):
        """
        Update live data with new price.
        Calculate indicators on the fly.
        """
        new_row = {
            'timestamp': pd.Timestamp.now(),  # Add current timestamp
            'close': price,
            'FAST_IND': None,  # Placeholder until calculated
            'SLOW_IND': None   # Placeholder until calculated
        }

        new_row_df = pd.DataFrame([new_row])

        # Ensure self.data is properly initialized
        if self.data.empty:
            self.data = new_row_df.copy()
        else:
            # Align columns explicitly to avoid warnings
            new_row_df = new_row_df.reindex(columns=self.data.columns)
            self.data = pd.concat([self.data, new_row_df], ignore_index=True).copy()

        # Calculate indicators if enough data is available
        if len(self.data) >= self.long_window:
            self.data['FAST_IND'] = self.data['close'].ewm(span=self.short_window, min_periods=1).mean()
            self.data['SLOW_IND'] = self.data['close'].ewm(span=self.long_window, min_periods=1).mean()
            logger.info("📊 Indicators updated.")
        else:
            logger.warning("⚠️ Not enough data points for indicator calculation.")


    def get_signal(self):
        """
        Generate trading signals based on strategy logic.
        Returns: Signal Enum (BUY, SELL, HOLD)
        """
        if len(self.data) < self.long_window:
            logger.warning("⚠️ Not enough data for strategy evaluation.")
            return Signal.HOLD

        current_price = self.data['close'].iloc[-1]
        fast_ind = self.data['FAST_IND'].iloc[-1]
        slow_ind = self.data['SLOW_IND'].iloc[-1]

        logger.info(f"📈 Current Price: {current_price}, FAST_IND: {fast_ind}, SLOW_IND: {slow_ind}")

        # Stop-Loss Logic
        if self.position == 'long' and current_price <= self.entry_price * (1 - self.stop_loss):
            logger.warning("🛑 Stop-Loss triggered for LONG.")
            self.position = None
            self.uptrend_triggered = False
            return Signal.STOP_LOSS_LONG

        if self.position == 'short' and current_price >= self.entry_price * (1 + self.stop_loss):
            logger.warning("🛑 Stop-Loss triggered for SHORT.")
            self.position = None
            self.downtrend_triggered = False
            return Signal.STOP_LOSS_SHORT

        # Profit Target Logic
        if self.position == 'long' and current_price >= self.entry_price * (1 + self.profit_target):
            logger.info("🏆 Profit Target hit for LONG.")
            self.position = None
            self.uptrend_triggered = False
            return Signal.SELL_LONG

        if self.position == 'short' and current_price <= self.entry_price * (1 - self.profit_target):
            logger.info("🏆 Profit Target hit for SHORT.")
            self.position = None
            self.downtrend_triggered = False
            return Signal.BUY_SHORT

        # Entry Logic (Evaluate if no active position and trend trigger)
        if self.position is None:
            if self.enable_longing and fast_ind > slow_ind and not self.uptrend_triggered:
                self.position = 'long'
                self.entry_price = current_price
                self.uptrend_triggered = True
                self.downtrend_triggered = False
                logger.info("🟢 Long Entry Signal Detected.")
                return Signal.BUY_LONG

            if self.enable_shorting and fast_ind < slow_ind and not self.downtrend_triggered:
                self.position = 'short'
                self.entry_price = current_price
                self.downtrend_triggered = True
                self.uptrend_triggered = False
                logger.info("🔴 Short Entry Signal Detected.")
                return Signal.SELL_SHORT

        return Signal.HOLD


    def reset_position(self):
        """
        Reset the strategy state after closing a position.
        """
        self.position = None
        self.entry_price = None
        logger.info("🔄 Position reset.")
