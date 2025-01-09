import matplotlib.pyplot as plt
import pandas as pd
from utils.logger import logger


def plot_results(df, output_file='trading_results.png'):
    """
    Plot the trading results, including all Long and Short transactions, for any strategy.
    """
    try:
        # Ensure DataFrame has a datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("❌ DataFrame index is not a DatetimeIndex.")

        # Plot Close Price
        plt.figure(figsize=(16, 8))
        plt.plot(df.index, df['close'], label='Close Price', linewidth=1, color='gray')

        # Plot Indicators
        indicators = {
            'FAST_IND': {'label': 'Fast Indicator', 'style': '--', 'color': 'blue'},
            'SLOW_IND': {'label': 'Slow Indicator', 'style': '--', 'color': 'orange'}
        }
        for col, params in indicators.items():
            if col in df.columns:
                plt.plot(df.index, df[col], label=params['label'], linestyle=params['style'], linewidth=1, color=params['color'])
        
        # Plot Actions
        actions = [
            # ('PREFILL', 'o', 'black', 'Prefill'),
            ('BUY', '^', 'green', 'Buy'),
            ('SELL', 'v', 'red', 'Sell'),
            ('STOP_LOSS', 'x', 'purple', 'Stop-Loss')
        ]
        for action, marker, color, label in actions:
            subset = df[df['action'] == action]
            if not subset.empty:
                plt.scatter(subset.index, subset['close'], marker=marker, color=color, s=50, label=label)
        
        plt.title('Trading Strategy Performance')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.legend(loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(output_file)
        logger.info(f"✅ Plot saved as {output_file}")
        plt.close()
    except Exception as e:
        logger.error(f"❌ Failed to generate plot: {e}")
