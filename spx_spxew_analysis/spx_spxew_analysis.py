import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

# Define the ticker symbols
spx_ticker = "^GSPC"  # S&P 500 Index
spxew_ticker = "^SP500EW"  # S&P 500 Equal Weight Index

# Download data
start_date = "2007-01-01"
end_date = pd.to_datetime('today')

spx_data = yf.download(spx_ticker, start=start_date, end=end_date)
spxew_data = yf.download(spxew_ticker, start=start_date, end=end_date)

# Combine the closing prices
df = pd.DataFrame({
    'SPX': spx_data['Close'],
    'SPXEW': spxew_data['Close']
})

# Normalize closing prices
df['SPX_Normalized'] = df['SPX'] / df['SPX'].iloc[0]
df['SPXEW_Normalized'] = df['SPXEW'] / df['SPXEW'].iloc[0]

# Calculate daily returns
df['SPX_Return'] = df['SPX'].pct_change()
df['SPXEW_Return'] = df['SPXEW'].pct_change()

# Calculate the return spread
df['Return_Spread'] = df['SPXEW_Return'] - df['SPX_Return']

# Calculate outlier bounds (3 standard deviations)
mean_spread = df['Return_Spread'].mean()
std_spread = df['Return_Spread'].std()
upper_bound = mean_spread + 3 * std_spread
lower_bound = mean_spread - 3 * std_spread

# Calculate cumulative return spread
df['Cumulative_Return_Spread'] = (1 + df['Return_Spread']).cumprod() - 1

# Calculate rolling volatility (252 trading days ≈ 1 year)
df['SPX_Volatility'] = df['SPX_Return'].rolling(window=252).std() * np.sqrt(252)
df['SPXEW_Volatility'] = df['SPXEW_Return'].rolling(window=252).std() * np.sqrt(252)

# Calculate drawdowns
def calculate_drawdown(prices):
    return (prices - prices.cummax()) / prices.cummax()

df['SPX_Drawdown'] = calculate_drawdown(df['SPX'])
df['SPXEW_Drawdown'] = calculate_drawdown(df['SPXEW'])

# Create subplots
fig, axs = plt.subplots(5, 1, figsize=(12, 25), dpi=300)
plt.subplots_adjust(hspace=0.3)
colors = {'SPX': '#1f77b4', 'SPXEW': '#ff7f0e'}

# Helper function for formatting y-axis as percentage
def percentage_formatter(x, pos):
    return f'{100*x:.0f}%'

# Plot 1: Normalized closing prices
axs[0].plot(df.index, df['SPX_Normalized'], label='SPX', color=colors['SPX'])
axs[0].plot(df.index, df['SPXEW_Normalized'], label='SPXEW', color=colors['SPXEW'])
axs[0].set_title('Normalized Closing Prices: SPXEW vs SPX')
axs[0].set_ylabel('Normalized Price')
axs[0].legend()
axs[0].grid(visible=True, alpha=0.4, linestyle='--')

# Plot 2: Daily return spread
axs[1].plot(df.index, df['Return_Spread'], linewidth=0.8, color='#2ca02c')
axs[1].axhline(y=upper_bound, color='r', linestyle='--')
axs[1].axhline(y=lower_bound, color='r', linestyle='--')
axs[1].set_title('Daily Return Spread: SPXEW vs SPX (with 3σ bounds)')
axs[1].set_ylabel('Return Spread')
axs[1].grid(visible=True, alpha=0.4, linestyle='--')
axs[1].yaxis.set_major_formatter(FuncFormatter(percentage_formatter))
axs[1].text(0.02, 0.95, 'Positive: SPXEW outperforms SPX', transform=axs[1].transAxes, 
         verticalalignment='top', fontsize=10, alpha=1)
axs[1].text(0.02, 0.90, 'Negative: SPX outperforms SPXEW', transform=axs[1].transAxes, 
         verticalalignment='top', fontsize=10, alpha=1)

# Plot 3: Cumulative return spread
axs[2].plot(df.index, df['Cumulative_Return_Spread'], color='#9467bd')
axs[2].set_title('Cumulative Return Spread: SPXEW vs SPX')
axs[2].set_ylabel('Cumulative Return Spread')
axs[2].grid(visible=True, alpha=0.4, linestyle='--')
axs[2].axhline(y=0, color='red', linestyle='--', alpha=0.5)
axs[2].yaxis.set_major_formatter(FuncFormatter(percentage_formatter))
axs[2].text(0.02, 0.95, 'Positive: SPXEW outperforms SPX', transform=axs[2].transAxes, 
         verticalalignment='top', fontsize=9, alpha=1)
axs[2].text(0.02, 0.90, 'Negative: SPX outperforms SPXEW', transform=axs[2].transAxes, 
         verticalalignment='top', fontsize=9, alpha=1)

# Plot 4: Rolling Volatility
axs[3].plot(df.index, df['SPX_Volatility'], label='SPX', color=colors['SPX'])
axs[3].plot(df.index, df['SPXEW_Volatility'], label='SPXEW', color=colors['SPXEW'])
axs[3].set_title('1-Year Rolling Volatility')
axs[3].set_ylabel('Annualized Volatility')
axs[3].legend()
axs[3].grid(visible=True, alpha=0.4, linestyle='--')
axs[3].yaxis.set_major_formatter(FuncFormatter(percentage_formatter))

# Plot 5: Underwater plot (Drawdowns)
axs[4].fill_between(df.index, df['SPX_Drawdown'], 0, alpha=0.4, label='SPX', color=colors['SPX'])
axs[4].fill_between(df.index, df['SPXEW_Drawdown'], 0, alpha=0.4, label='SPXEW', color=colors['SPXEW'])
axs[4].set_title('Underwater Plot (Drawdowns)')
axs[4].set_ylabel('Drawdown')
axs[4].legend()
axs[4].grid(visible=True, alpha=0.4, linestyle='--')
axs[4].set_ylim(df[['SPX_Drawdown', 'SPXEW_Drawdown']].min().min() * 1.1, 0.05)
axs[4].yaxis.set_major_formatter(FuncFormatter(percentage_formatter))

# Format x-axis for all subplots
for ax in axs:
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.tick_params(axis='x', rotation=0)

# Adjust layout
plt.tight_layout()
plt.show()