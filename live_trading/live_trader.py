from live_trading.binance_client import BinanceClient
from live_trading.order_manager import OrderManager
from strategies.live_strategy import LiveStrategy, Signal
from utils.logger import logger
from visualization.live_plot_results import plot_results

import pandas as pd
import os
import csv
import time
from datetime import datetime


class LiveTrader:
    def __init__(self, config):
        self.client = BinanceClient(config['API_KEY'], config['SECRET_KEY'], config['TESTNET'])
        self.order_manager = OrderManager(self.client)
        self.strategy = LiveStrategy(
            stop_loss=config['STOP_LOSS'],
            profit_target=config['PROFIT_TARGET'],
            short_window=config['SHORT_WINDOW'],
            long_window=config['LONG_WINDOW'],
            enable_longing=config['ENABLE_LONGING'],
            enable_shorting=config['ENABLE_SHORTING']
        )
        self.symbol = config['LIVE_SYMBOL']
        self.leverage = config['LEVERAGE']

        self.stop_reason = 'Unknown'
        self.error_message = ''
        self.run_folder = self.create_run_folder()
        self.csv_path = os.path.join(self.run_folder, 'data_trade.csv')
        self.plot_path = os.path.join(self.run_folder, 'plot.png')
        self.config_backup_path = os.path.join(self.run_folder, 'config_backup.py')
        self.save_config(config)

        # Initialize CSV with headers
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['timestamp', 'close', 'FAST_IND', 'SLOW_IND', 'action', 'position', 'stop_reason', 'error_message'])
                writer.writeheader()
            logger.info(f"📄 Created new CSV file: {self.csv_path}")

        # Fetch Historical Data
        self.prefill_historical_data()
    def create_run_folder(self):
        """Create a unique folder for each trading run."""
        base_path = './data/live_runs'
        os.makedirs(base_path, exist_ok=True)

        existing_runs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and d.startswith('run')]
        run_number = len(existing_runs) + 1
        run_folder = os.path.join(base_path, f'run{run_number}')
        os.makedirs(run_folder, exist_ok=True)
        logger.info(f"📁 Created run folder: {run_folder}")
        return run_folder

    def save_config(self, config):
        """Save a backup of the current configuration."""
        with open(self.config_backup_path, 'w') as f:
            for key, value in config.items():
                f.write(f"{key} = {repr(value)}\n")
        logger.info(f"💾 Configuration saved to {self.config_backup_path}")

    def record_trade(self, timestamp, price, action, position):
        """Record live trade details incrementally into the CSV."""
        trade_data = {
            'timestamp': pd.to_datetime(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'close': price,
            'FAST_IND': self.strategy.data['FAST_IND'].iloc[-1] if 'FAST_IND' in self.strategy.data.columns else None,
            'SLOW_IND': self.strategy.data['SLOW_IND'].iloc[-1] if 'SLOW_IND' in self.strategy.data.columns else None,
            'action': action,
            'position': position,
            'stop_reason': self.stop_reason,
            'error_message': self.error_message
        }
        logger.info(f"📝 Recorded trade: {trade_data}")

        # # Write to CSV incrementally
        # with open(self.csv_path, mode='a', newline='') as file:
        #     writer = csv.DictWriter(
        #         file,
        #         fieldnames=['timestamp', 'close', 'FAST_IND', 'SLOW_IND', 'action', 'position', 'stop_reason', 'error_message']
        #     )
        #     writer.writerow(trade_data)



    def prefill_historical_data(self):
        """Fetch 1000 minutes of historical data and prefill strategy."""
        logger.info("📥 Fetching 1000 minutes of historical data...")
        try:
            historical_data = self.client.get_historical_klines(
                symbol=self.symbol,
                interval='1m',
                limit=1000
            )
            self.strategy.prefill_data(historical_data)

            # Prepare CSV DataFrame
            prefilled_df = self.strategy.data.copy()
            # Add Metadata Columns
            prefilled_df['action'] = 'PREFILL'
            prefilled_df['position'] = 'NONE'
            prefilled_df['stop_reason'] = ''
            prefilled_df['error_message'] = ''

            # Ensure Indicator Columns are Included
            if 'FAST_IND' not in prefilled_df.columns:
                prefilled_df['FAST_IND'] = self.strategy.data['FAST_IND'].values
            if 'SLOW_IND' not in prefilled_df.columns:
                prefilled_df['SLOW_IND'] = self.strategy.data['SLOW_IND'].values

            # Ensure proper column order
            expected_columns = ['timestamp', 'close', 'FAST_IND', 'SLOW_IND', 'action', 'position', 'stop_reason', 'error_message']
            prefilled_df = prefilled_df[expected_columns]

            # Debug Validation
            logger.info(f"📊 Prefill Data Preview:\n{prefilled_df.head()}")

            prefilled_df.to_csv(
                self.csv_path,
                mode='a',
                header=not os.path.exists(self.csv_path),
                index=False
            )
            logger.info("✅ Prefilled data successfully written to CSV with indicators.")
        except Exception as e:
            logger.error(f"❌ Failed to prefill historical data: {e}")
            raise


    def run(self):
        logger.info(f"🚀 Starting live trading for {self.symbol} on Binance Futures...")
        try:
            while True:
                try:
                    # Fetch current ticker price
                    ticker = self.client.get_ticker(self.symbol)
                    price = ticker['last']
                    
                    order_quantity = 20
                    print(order_quantity)
                    position_value = order_quantity * self.leverage
                    order_quantity = 800 / price
                    print(order_quantity)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    logger.info(f"📊 Current Price: ${price:.2f}")

                    # Update strategy with the latest price
                    self.strategy.update_data(price)
                    signal = self.strategy.get_signal()

                    # Handle Signals
                    # if signal == Signal.BUY_LONG:  # Koop, uptrend
                    #     logger.info("🟢 Opening LONG position.")
                    #     self.order_manager.place_order(self.symbol, 'BUY', order_quantity, 'MARKET', price, self.leverage)
                    #     self.record_trade(timestamp, price, 'BUY', 'LONG')

                    # elif signal == Signal.SELL_LONG:
                    #     logger.info("🔴 Closing LONG position.")
                    #     self.order_manager.place_order(self.symbol, 'SELL', order_quantity, 'MARKET', price, self.leverage)
                    #     self.record_trade(timestamp, price, 'SELL', 'LONG')

                    # elif signal == Signal.BUY_SHORT:
                    #     logger.info("🔴 Closing SHORT position.")
                    #     self.order_manager.place_order(self.symbol, 'BUY', order_quantity, 'MARKET', price, self.leverage)
                    #     self.record_trade(timestamp, price, 'BUY', 'SHORT')

                    # elif signal == Signal.SELL_SHORT:
                    #     logger.info("🟢 Opening SHORT position.")
                    #     self.order_manager.place_order(self.symbol, 'SELL', order_quantity, 'MARKET', price, self.leverage)
                    #     self.record_trade(timestamp, price, 'SELL', 'SHORT')

                    # elif signal == Signal.STOP_LOSS_LONG:
                    #     logger.warning("🛑 Stop-Loss triggered for LONG. Closing LONG position.")
                    #     self.order_manager.place_order(self.symbol, 'SELL', order_quantity, 'MARKET', price, self.leverage)
                    #     self.record_trade(timestamp, price, 'STOP_LOSS', 'LONG')
                    #     # No new position opened here

                    # elif signal == Signal.STOP_LOSS_SHORT:
                    #     logger.warning("🛑 Stop-Loss triggered for SHORT. Closing SHORT position.")
                    #     self.order_manager.place_order(self.symbol, 'BUY', order_quantity, 'MARKET', price, self.leverage)
                    #     self.record_trade(timestamp, price, 'STOP_LOSS', 'SHORT')


                    # Update plot
                    try:
                        df = pd.read_csv(self.csv_path, parse_dates=['timestamp'])
                        plot_results(df, self.plot_path)
                    except Exception as plot_error:
                        logger.error(f"❌ Failed to generate plot: {plot_error}")
                    time.sleep(60)  # Wait 1 minute before the next cycle

                except Exception as e:
                    self.stop_reason = 'Error'
                    self.error_message = str(e)
                    logger.error(f"❌ Error in live trading: {e}")
                    break

        except KeyboardInterrupt:
            self.stop_reason = 'Manual Stop'
            logger.info("🛑 Live trading manually stopped by user.")

        finally:
            try:
                plot_results(pd.read_csv(self.csv_path, parse_dates=['timestamp']).set_index('timestamp'), self.plot_path)
                logger.info("✅ Final plot generated successfully.")
            except Exception as plot_error:
                logger.error(f"❌ Failed to generate final plot: {plot_error}")

            logger.info("✅ Live trading session completed.")
