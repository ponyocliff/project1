"""
Crypto Screener - Phase 3: Multi-Coin Screening with Alerts
This script screens multiple cryptocurrencies and flags coins matching specific conditions.
"""

import ccxt
import time
from datetime import datetime

def calculate_sma(prices, period):
    """
    Calculate Simple Moving Average (SMA)
    
    SMA is the average price over a specific number of days.
    Example: 20-day SMA = average of last 20 closing prices
    
    Args:
        prices: List of price values
        period: Number of days to average (e.g., 20 or 50)
    
    Returns:
        The SMA value (float)
    """
    if len(prices) < period:
        return None  # Not enough data
    # Take the last 'period' prices and calculate their average
    return sum(prices[-period:]) / period


def calculate_ema(prices, period):
    """
    Calculate Exponential Moving Average (EMA)
    
    EMA gives more weight to recent prices than SMA.
    Used for MACD calculation.
    
    Args:
        prices: List of price values
        period: Number of periods to use
    
    Returns:
        The EMA value (float)
    """
    if len(prices) < period:
        return None
    
    # Start with SMA for the first EMA value
    ema = sum(prices[:period]) / period
    
    # Multiplier for EMA calculation (2 / (period + 1))
    multiplier = 2 / (period + 1)
    
    # Calculate EMA for remaining prices
    for price in prices[period:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema


def calculate_rsi(prices, period=14):
    """
    Calculate Relative Strength Index (RSI)
    
    RSI measures if a cryptocurrency is overbought (>70) or oversold (<30).
    It ranges from 0 to 100.
    
    Args:
        prices: List of price values
        period: Number of periods to use (default 14)
    
    Returns:
        The RSI value (float between 0-100)
    """
    if len(prices) < period + 1:
        return None  # Not enough data
    
    # Calculate price changes (gains and losses)
    deltas = []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        deltas.append(change)
    
    # Separate gains (positive changes) and losses (negative changes)
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]
    
    # Calculate average gain and average loss
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    # Avoid division by zero
    if avg_loss == 0:
        return 100
    
    # Calculate RS (Relative Strength) and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    MACD shows the relationship between two moving averages.
    - MACD Line = 12-day EMA - 26-day EMA
    - Signal Line = 9-day EMA of the MACD line
    - Histogram = MACD Line - Signal Line
    
    Args:
        prices: List of price values
        fast: Fast EMA period (default 12)
        slow: Slow EMA period (default 26)
        signal: Signal line EMA period (default 9)
    
    Returns:
        Dictionary with 'macd_line', 'signal_line', 'histogram', and 'trend'
    """
    if len(prices) < slow + signal:
        return None
    
    # Calculate all EMAs progressively to build MACD line history
    # We need MACD values for at least 'signal' periods to calculate signal line
    macd_values = []
    
    # Start from 'slow' period to ensure we have enough data for both EMAs
    for i in range(slow - 1, len(prices)):
        # Get prices up to current point
        price_window = prices[:i+1]
        
        # Calculate fast and slow EMAs for this window
        fast_ema_val = calculate_ema(price_window, fast)
        slow_ema_val = calculate_ema(price_window, slow)
        
        if fast_ema_val is not None and slow_ema_val is not None:
            # MACD value = fast EMA - slow EMA
            macd_values.append(fast_ema_val - slow_ema_val)
    
    # Need at least 'signal' periods of MACD values
    if len(macd_values) < signal:
        return None
    
    # Current MACD line (most recent value)
    macd_line = macd_values[-1]
    
    # Signal line = EMA of MACD values
    signal_line = calculate_ema(macd_values, signal)
    
    if signal_line is None:
        return None
    
    # Histogram = MACD line - Signal line
    histogram = macd_line - signal_line
    
    # Determine trend: bullish if MACD > Signal, bearish if MACD < Signal
    trend = "🟢 BULLISH" if macd_line > signal_line else "🔴 BEARISH"
    
    return {
        'macd_line': macd_line,
        'signal_line': signal_line,
        'histogram': histogram,
        'trend': trend
    }


def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """
    Calculate Bollinger Bands
    
    Bollinger Bands show volatility and potential support/resistance levels.
    - Middle Band = SMA(period)
    - Upper Band = Middle + (std_dev * standard deviation)
    - Lower Band = Middle - (std_dev * standard deviation)
    
    Args:
        prices: List of price values
        period: Number of periods for SMA (default 20)
        std_dev: Number of standard deviations (default 2)
    
    Returns:
        Dictionary with 'upper', 'middle', 'lower', and 'position'
    """
    if len(prices) < period:
        return None
    
    # Calculate middle band (SMA)
    middle = calculate_sma(prices, period)
    
    # Calculate standard deviation
    recent_prices = prices[-period:]
    mean = middle
    variance = sum((p - mean) ** 2 for p in recent_prices) / period
    std = variance ** 0.5
    
    # Calculate upper and lower bands
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    
    # Determine price position relative to bands
    current_price = prices[-1]
    band_width = upper - lower
    distance_from_upper = (upper - current_price) / band_width if band_width > 0 else 0
    distance_from_lower = (current_price - lower) / band_width if band_width > 0 else 0
    
    if distance_from_upper < 0.05:  # Within 5% of upper band
        position = "🔴 NEAR UPPER BAND (potentially overbought)"
    elif distance_from_lower < 0.05:  # Within 5% of lower band
        position = "🟢 NEAR LOWER BAND (potentially oversold)"
    elif current_price > upper:
        position = "🔴 ABOVE UPPER BAND (strongly overbought)"
    elif current_price < lower:
        position = "🟢 BELOW LOWER BAND (strongly oversold)"
    else:
        position = "⚪ BETWEEN BANDS (normal range)"
    
    return {
        'upper': upper,
        'middle': middle,
        'lower': lower,
        'position': position
    }


def calculate_atr(ohlcv_data, period=14):
    """
    Calculate Average True Range (ATR)
    
    ATR measures market volatility by looking at price ranges.
    Higher ATR = more volatility, Lower ATR = less volatility.
    
    Args:
        ohlcv_data: List of OHLCV candles [open, high, low, close, volume]
        period: Number of periods to use (default 14)
    
    Returns:
        The ATR value (float)
    """
    if len(ohlcv_data) < period + 1:
        return None
    
    # Calculate True Range for each period
    true_ranges = []
    for i in range(1, len(ohlcv_data)):
        high = ohlcv_data[i][2]  # High price
        low = ohlcv_data[i][3]   # Low price
        prev_close = ohlcv_data[i-1][4]  # Previous close
        
        # True Range = max of:
        # 1. Current High - Current Low
        # 2. |Current High - Previous Close|
        # 3. |Current Low - Previous Close|
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        true_range = max(tr1, tr2, tr3)
        true_ranges.append(true_range)
    
    # ATR = Average of True Ranges over the period
    if len(true_ranges) < period:
        return None
    
    atr = sum(true_ranges[-period:]) / period
    return atr


def format_number(num, decimals=2):
    """
    Format numbers nicely for display
    """
    if num is None:
        return "N/A"
    if num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num/1_000:.2f}K"
    else:
        return f"${num:.{decimals}f}"


def format_price(price):
    """
    Format price for table display
    """
    if price is None:
        return "N/A"
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.2f}"
    else:
        return f"${price:.4f}"


def analyze_coin(exchange, symbol):
    """
    Analyze a single cryptocurrency and return all relevant data
    
    Args:
        exchange: ccxt exchange instance
        symbol: Trading pair (e.g., 'BTC/USDT')
    
    Returns:
        Dictionary with all analysis data, or None if error
    """
    try:
        # Fetch current ticker data
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        change_24h = ticker['percentage']
        volume_24h = ticker['quoteVolume']
        
        # Fetch historical data
        ohlcv = exchange.fetch_ohlcv(symbol, '1d', limit=60)
        
        if len(ohlcv) < 50:  # Need enough data
            return None
        
        # Extract data
        closing_prices = [candle[4] for candle in ohlcv]
        volumes = [candle[5] for candle in ohlcv]
        
        # Calculate indicators
        sma_20 = calculate_sma(closing_prices, 20)
        sma_50 = calculate_sma(closing_prices, 50)
        rsi_14 = calculate_rsi(closing_prices, 14)
        macd = calculate_macd(closing_prices, fast=12, slow=26, signal=9)
        avg_volume_20d = calculate_sma(volumes, 20) if len(volumes) >= 20 else None
        volume_ratio = (volume_24h / avg_volume_20d) if avg_volume_20d and avg_volume_20d > 0 else None
        
        # Calculate RSI trend (compare current RSI to previous RSI)
        rsi_trend = None
        if len(closing_prices) >= 15:
            rsi_prev = calculate_rsi(closing_prices[:-1], 14)
            if rsi_prev is not None and rsi_14 is not None:
                if rsi_14 < rsi_prev:
                    rsi_trend = "DOWN"
                elif rsi_14 > rsi_prev:
                    rsi_trend = "UP"
                else:
                    rsi_trend = "FLAT"
        
        return {
            'symbol': symbol.replace('/USDT', ''),
            'price': current_price,
            'change_24h': change_24h,
            'volume_24h': volume_24h,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'rsi': rsi_14,
            'rsi_trend': rsi_trend,
            'macd': macd,
            'volume_ratio': volume_ratio,
            'avg_volume_20d': avg_volume_20d
        }
    except Exception as e:
        print(f"   ⚠️  Error analyzing {symbol}: {str(e)[:50]}")
        return None


def screen_coin(coin_data):
    """
    Screen a coin against all conditions and return alerts
    
    Args:
        coin_data: Dictionary from analyze_coin()
    
    Returns:
        List of alert strings (empty if no alerts)
    """
    alerts = []
    
    if coin_data is None:
        return alerts
    
    rsi = coin_data.get('rsi')
    price = coin_data.get('price')
    sma_20 = coin_data.get('sma_20')
    sma_50 = coin_data.get('sma_50')
    macd = coin_data.get('macd')
    volume_ratio = coin_data.get('volume_ratio')
    rsi_trend = coin_data.get('rsi_trend')
    
    # Condition 1: OVERSOLD
    if rsi is not None and rsi < 30:
        alerts.append("🟢 OVERSOLD")
    
    # Condition 2: OVERBOUGHT
    if rsi is not None and rsi > 70:
        alerts.append("🔴 OVERBOUGHT")
    
    # Condition 3: VOLUME SPIKE
    if volume_ratio is not None and volume_ratio > 2.0:
        alerts.append("📊 VOLUME SPIKE")
    
    # Condition 4: BULLISH SETUP
    if (price and sma_20 and sma_50 and macd and rsi is not None and
        price > sma_20 and price > sma_50 and
        macd.get('trend', '').startswith('🟢') and
        40 <= rsi <= 60):
        alerts.append("🚀 BULLISH SETUP")
    
    # Condition 5: BREAKDOWN RISK
    if (price and sma_20 and sma_50 and macd and rsi is not None and rsi_trend and
        price < sma_20 and price < sma_50 and
        macd.get('trend', '').startswith('🔴') and
        rsi_trend == "DOWN"):
        alerts.append("⚠️  BREAKDOWN RISK")
    
    return alerts


def print_summary_table(all_coins):
    """
    Print a formatted summary table of all coins
    """
    print("\n" + "=" * 120)
    print("  COIN SCREENER SUMMARY")
    print("=" * 120)
    print(f"{'Coin':<8} {'Price':<12} {'24h %':<8} {'RSI':<8} {'MACD':<12} {'Vol Ratio':<12} {'Status':<20}")
    print("-" * 120)
    
    for coin in all_coins:
        if coin is None:
            continue
        
        symbol = coin['symbol']
        price = format_price(coin['price'])
        change = f"{coin['change_24h']:+.2f}%" if coin['change_24h'] is not None else "N/A"
        
        rsi_str = f"{coin['rsi']:.1f}" if coin['rsi'] is not None else "N/A"
        
        macd_status = "N/A"
        if coin['macd']:
            if coin['macd'].get('trend', '').startswith('🟢'):
                macd_status = "🟢 Bullish"
            elif coin['macd'].get('trend', '').startswith('🔴'):
                macd_status = "🔴 Bearish"
        
        vol_ratio_str = f"{coin['volume_ratio']:.2f}x" if coin['volume_ratio'] is not None else "N/A"
        
        # Status: show key indicator
        status = ""
        if coin['rsi'] is not None:
            if coin['rsi'] < 30:
                status = "🟢 Oversold"
            elif coin['rsi'] > 70:
                status = "🔴 Overbought"
            else:
                status = "⚪ Normal"
        
        print(f"{symbol:<8} {price:<12} {change:<8} {rsi_str:<8} {macd_status:<12} {vol_ratio_str:<12} {status:<20}")
    
    print("=" * 120)


def print_alerts(all_coins, all_alerts):
    """
    Print alerts section showing only coins that triggered conditions
    """
    print("\n" + "=" * 120)
    print("  ⚠️  ALERTS - COINS MATCHING SCREENING CONDITIONS")
    print("=" * 120)
    
    has_alerts = False
    for coin, alerts in zip(all_coins, all_alerts):
        if alerts:  # Only show coins with alerts
            has_alerts = True
            symbol = coin['symbol'] if coin else "Unknown"
            price = format_price(coin['price']) if coin else "N/A"
            change = f"{coin['change_24h']:+.2f}%" if coin and coin['change_24h'] is not None else "N/A"
            rsi = f"{coin['rsi']:.1f}" if coin and coin['rsi'] is not None else "N/A"
            
            print(f"\n{symbol} ({price}, {change}, RSI: {rsi})")
            for alert in alerts:
                print(f"  → {alert}")
    
    if not has_alerts:
        print("\n✅ No coins matching screening conditions at this time.")
        print("   All coins are within normal parameters.")
    
    print("\n" + "=" * 120)


def run_multi_coin_screener(coin_list):
    """
    Main function that screens multiple cryptocurrencies
    
    Args:
        coin_list: List of coin symbols (e.g., ['BTC', 'ETH', 'SOL'])
    """
    print("=" * 120)
    print("  CRYPTO SCREENER - MULTI-COIN ANALYSIS")
    print("=" * 120)
    print(f"Analyzing {len(coin_list)} coins from Binance...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Connect to Binance exchange (no API key needed for public data)
        exchange = ccxt.binance({
            'enableRateLimit': True,  # Respect rate limits
        })
        
        all_coins = []
        all_alerts = []
        
        # Analyze each coin
        for i, coin in enumerate(coin_list, 1):
            symbol = f"{coin}/USDT"
            print(f"[{i}/{len(coin_list)}] Analyzing {coin}...", end=" ", flush=True)
            
            coin_data = analyze_coin(exchange, symbol)
            all_coins.append(coin_data)
            
            # Screen for alerts
            alerts = screen_coin(coin_data) if coin_data else []
            all_alerts.append(alerts)
            
            if coin_data:
                print(f"✅ Done")
            else:
                print(f"❌ Failed")
            
            # Add delay between API calls to avoid rate limiting (except for last coin)
            if i < len(coin_list):
                time.sleep(0.5)  # 500ms delay between requests
        
        # Display results
        print_summary_table(all_coins)
        print_alerts(all_coins, all_alerts)
        
        print(f"\n✅ Screening completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 120)
        
    except ccxt.NetworkError as e:
        print(f"\n❌ Network error: Could not connect to Binance. Check your internet connection.")
        print(f"   Error details: {e}")
    except ccxt.ExchangeError as e:
        print(f"\n❌ Exchange error: Binance returned an error.")
        print(f"   Error details: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"   Error type: {type(e).__name__}")


# This is the entry point - the script starts here when you run it
if __name__ == "__main__":
    # List of coins to screen (all paired with USDT)
    coins_to_screen = ['BTC', 'ETH', 'SOL', 'XRP', 'HYPE', 'AAVE', 'PUMP', 'STABLE', 'ENA', 'BNB']
    
    # Run the multi-coin screener
    run_multi_coin_screener(coins_to_screen)
    print()
