
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import argparse

def calculate_ema(df, period=50):
    return df['Close'].ewm(span=period, adjust=False).mean()

def find_swings(df, window=20):
    # Simple Local Min/Max detection
    df['Swing_High'] = df['High'].rolling(window=window, center=True).max()
    df['Swing_Low'] = df['Low'].rolling(window=window, center=True).min()
    return df

def backtest_fib_strategy(df, initial_capital=100.0):
    capital = initial_capital
    position = 0.0
    entry_price = 0.0
    stop_loss = 0.0
    take_profit = 0.0
    
    trades = []
    
    # State variables
    in_trade = False
    last_high = 0.0
    last_low = 0.0
    
    print("\n" + "="*60)
    print(f"💰 FIBONACCI BACKTEST (Capital Inicial: ${initial_capital})")
    print("-" * 60)
    print(f"{'FECHA':<25} {'ACCIÓN':<10} {'PRECIO':<10} {'BALANCE':<10} {'P&L'}")
    print("-" * 60)

    # We need to iterate carefully. 
    # Logic:
    # 1. Identify valid Swing High -> Low move (or Low -> High for uptrend).
    # 2. Wait for Retracement to 0.618.
    
    # Simplified approach for "Golden Pocket" in UPTREND:
    # 1. Price > EMA 50
    # 2. Find recent significant High (Swing High).
    # 3. Find the Low that started that move (Swing Low).
    # 4. Fib Levels: (High - Low). 
    # 5. Buy Zone: Low + 0.618 * (High - Low)  <- Actually Retracement is from High down.
    #    Retracement 0% = High, 100% = Low.
    #    Level 0.618 Retracement = High - 0.618 * (High - Low).
    
    # Iterate candle by candle
    
    # Dynamic swing detection is tricky in a simple loop without looking ahead.
    # We will use a trailing window max/min to define "Recent High" and "Recent Low".
    
    local_max = 0.0
    local_min = 0.0
    
    for i in range(50, len(df)):
        curr = df.iloc[i]
        date = df.index[i]
        price = curr['Close']
        ema = curr['EMA_50']
        
        # ------------------------
        # TRADE MANAGEMENT (Exit)
        # ------------------------
        if in_trade:
            # Check Take Profit
            if price >= take_profit:
                revenue = position * price
                pnl_pct = ((price / entry_price) - 1) * 100
                capital = revenue
                position = 0
                in_trade = False
                print(f"{str(date):<25} 🟢 TP HIT    ${price:.2f}     ${capital:.2f}     {pnl_pct:+.2f}%")
                trades.append({'date': date, 'type': 'SELL', 'price': price, 'pnl': pnl_pct})
                continue
            
            # Check Stop Loss
            elif price <= stop_loss:
                revenue = position * price
                pnl_pct = ((price / entry_price) - 1) * 100
                capital = revenue
                position = 0
                in_trade = False
                print(f"{str(date):<25} 🔴 SL HIT    ${price:.2f}     ${capital:.2f}     {pnl_pct:+.2f}%")
                trades.append({'date': date, 'type': 'SELL', 'price': price, 'pnl': pnl_pct})
                continue

        # ------------------------
        # TRADE ENTRY (Signal)
        # ------------------------
        if not in_trade:
            # Only trade Uptrends for now (Price > EMA)
            if price > ema:
                # Lookback 50 periods for High/Low
                window_data = df.iloc[i-50:i]
                recent_high = window_data['High'].max()
                recent_low = window_data['Low'].min()
                
                # Check if we are "pulling back".
                # Current price should be significantly below recent high.
                
                # Definition of Fib 0.618 Level (Golden Pocket) from the High
                fib_618 = recent_high - 0.618 * (recent_high - recent_low)
                fib_050 = recent_high - 0.500 * (recent_high - recent_low)
                
                # Entry Condition:
                # 1. Price is inside the Golden Pocket (between 0.5 and 0.618 retracement)
                # 2. But we need to make sure we didn't just crash through it.
                #    Let's buy if Low touches the zone.
                
                if curr['Low'] <= fib_050 and curr['Low'] >= (fib_618 * 0.99): 
                    # *0.99 tolerance below 618 to catch wicks slightly breaking it
                    
                    # Risk Management
                    stop_loss_price = recent_low # SL below the swing low
                    take_profit_price = recent_high # TP at the swing high
                    
                    # Risk/Reward Filter: TP distance must be > SL distance * 1.5
                    risk = price - stop_loss_price
                    reward = take_profit_price - price
                    
                    if risk > 0 and (reward / risk) > 1.5:
                        position = capital / price
                        entry_price = price
                        capital = 0
                        stop_loss = stop_loss_price
                        take_profit = take_profit_price
                        in_trade = True
                        print(f"{str(date):<25} ⚡ BUY (Fib) ${price:.2f}     SL:${stop_loss:.2f} TP:${take_profit:.2f}")

    # Close Position at End
    if in_trade:
        final_price = df['Close'].iloc[-1]
        revenue = position * final_price
        pnl_pct = ((final_price / entry_price) - 1) * 100
        capital = revenue
        print(f"{'CIERRE FINAL':<25} ⚠️ CLOSE    ${final_price:.2f}     ${capital:.2f}     {pnl_pct:+.2f}%")

    profit_total = capital - initial_capital
    profit_pct = (profit_total / initial_capital) * 100
    
    print("-" * 60)
    print(f"RESULTADO FINAL: ${capital:.2f} ({profit_pct:+.2f}%)")
    print("="*60 + "\n")
    return df

def run_fib(ticker, interval='1h'):
    print(f"🔍 Analizando Swing Trading (Fibonacci) para {ticker} en {interval}...")
    
    # We need more data for Swing trading, maybe 1 month or 60 days
    df = yf.download(ticker, period='60d', interval=interval, progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df.columns = df.columns.get_level_values(0)
        except:
            pass
            
    df.dropna(inplace=True)
    df['EMA_50'] = calculate_ema(df, 50)
    
    backtest_fib_strategy(df, 100.0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", nargs="?", default="SOL-USD", help="Ticker")
    parser.add_argument("--interval", default="1h", help="Timeframe (15m, 1h, 4h)")
    args = parser.parse_args()
    
    run_fib(args.ticker, args.interval)
