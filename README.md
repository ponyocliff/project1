# Crypto Screener & Analyzer

A Python tool for analyzing cryptocurrency prices and technical indicators with automated screening alerts.

## Phase 3: Multi-Coin Screening with Alerts

This script screens multiple cryptocurrencies simultaneously and flags coins matching specific trading conditions:

**Screened Coins:** BTC, ETH, SOL, XRP, HYPE, AAVE, PUMP, STABLE, ENA, BNB (all paired with USDT)

**Screening Conditions:**
- 🟢 **OVERSOLD**: RSI below 30 (potential bounce opportunity)
- 🔴 **OVERBOUGHT**: RSI above 70 (potential pullback risk)
- 📊 **VOLUME SPIKE**: 24h volume more than 2x the 20-day average (unusual activity)
- 🚀 **BULLISH SETUP**: Price above both SMAs + MACD bullish + RSI 40-60 (strong uptrend)
- ⚠️ **BREAKDOWN RISK**: Price below both SMAs + MACD bearish + RSI trending down (potential decline)

---

## 📦 Installation (Step-by-Step)

### Step 1: Check if Python is installed

Open your terminal (Terminal on Mac, Command Prompt on Windows) and type:

```bash
python3 --version
```

If you see a version number (like `Python 3.9.7`), you're good! If not, download Python from [python.org](https://www.python.org/downloads/).

### Step 2: Install required packages

Navigate to this project folder in your terminal, then run:

```bash
pip3 install -r requirements.txt
```

**What this does:** This installs the `ccxt` library, which connects to cryptocurrency exchanges (we use Binance).

**If you get an error:** Try using `pip` instead of `pip3`:
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

### Option 1: Using Python 3 (Recommended)

```bash
python3 bitcoin_price.py
```

### Option 2: Using Python

```bash
python bitcoin_price.py
```

**What happens:** The script will:
1. Connect to Binance (no API key needed for public data)
2. Analyze all 10 cryptocurrencies one by one (with delays to avoid rate limiting)
3. Calculate technical indicators for each coin (SMA, RSI, MACD, Volume)
4. Screen each coin against 5 trading conditions
5. Display a summary table with all coins and their key stats
6. Show an ALERTS section highlighting only coins that match screening conditions

---

## 📊 Understanding the Output

### Summary Table
Shows all analyzed coins with:
- **Coin**: Symbol (BTC, ETH, etc.)
- **Price**: Current price in USDT
- **24h %**: 24-hour price change percentage
- **RSI**: Relative Strength Index (0-100)
- **MACD**: MACD trend (Bullish/Bearish)
- **Vol Ratio**: Current volume vs 20-day average (e.g., 1.5x = 50% above average)
- **Status**: Quick indicator status (Oversold/Overbought/Normal)

### Alerts Section
Only shows coins that triggered one or more screening conditions:
- **🟢 OVERSOLD**: RSI < 30 - Coin may be due for a bounce
- **🔴 OVERBOUGHT**: RSI > 70 - Coin may be due for a pullback
- **📊 VOLUME SPIKE**: Volume > 2x average - Unusual trading activity
- **🚀 BULLISH SETUP**: Strong uptrend conditions met
- **⚠️ BREAKDOWN RISK**: Potential decline conditions met

### Technical Indicators Explained

**SMA (Simple Moving Average)**
- **20-Day SMA**: Average price over the last 20 days
- **50-Day SMA**: Average price over the last 50 days
- **What it means**: Price above SMAs = bullish, below = bearish

**RSI (Relative Strength Index)**
- **Range**: 0 to 100
- **Above 70**: Overbought (may drop)
- **Below 30**: Oversold (may rise)
- **30-70**: Neutral zone

**MACD (Moving Average Convergence Divergence)**
- Shows relationship between two moving averages
- **Bullish**: MACD line above signal line
- **Bearish**: MACD line below signal line

---

## 🔧 Troubleshooting

**Problem**: "ModuleNotFoundError: No module named 'ccxt'"
- **Solution**: Run `pip3 install -r requirements.txt` again

**Problem**: "Network error" or "Could not connect"
- **Solution**: Check your internet connection and try again

**Problem**: "Command not found: python3"
- **Solution**: Try using `python` instead of `python3`

---

## ⚙️ How It Works

1. **Rate Limiting**: The script adds a 0.5 second delay between each coin analysis to avoid hitting Binance's rate limits
2. **Error Handling**: If a coin doesn't exist or has insufficient data, it will show "Failed" and continue with the next coin
3. **Real-Time Data**: All data is fetched live from Binance at the time you run the script

## 📝 What's Next?

Future phases will include:
- Price forecasting
- Historical backtesting
- Web interface
- Custom screening conditions
- Email/SMS alerts

---

## 💡 Tips for Beginners

1. **No API Key Needed**: This script only reads public data, so you don't need to create a Binance account.

2. **Rate Limits**: Binance limits how many requests you can make. The script automatically respects these limits.

3. **Data Freshness**: The data is live from Binance, so prices update in real-time.

4. **Understanding Indicators**: 
   - Moving averages help identify trends
   - RSI helps identify overbought/oversold conditions
   - Use multiple indicators together for better analysis
