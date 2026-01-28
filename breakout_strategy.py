
import yfinance as yf
import pandas as pd
import numpy as np
import argparse

def backtest_breakout(df, initial_capital=100.0):
    capital = initial_capital
    position = 0.0
    entry_price = 0.0
    
    trades = []
    in_trade = False
    
    print("\n" + "="*60)
    print(f"💥 BREAKOUT BACKTEST (Donchian Channel) - Capital: ${initial_capital}")
    print("-" * 60)
    print(f"{'FECHA':<25} {'ACCIÓN':<10} {'PRECIO':<10} {'BALANCE':<10} {'P&L'}")
    print("-" * 60)

    # Donchian Channels (20 High, 10 Low)
    # Note: We must use shift(1) because we trade based on the PREVIOUS closed candle's range.
    # We can't use the current candle's high/low to determine the range we are breaking out of *during* the current candle,
    # technically we react when price exceeds the *previous* N candles' high.
    
    df['Donchian_High'] = df['High'].rolling(window=20).max().shift(1)
    df['Donchian_Low'] = df['Low'].rolling(window=10).min().shift(1)
    
    for i in range(21, len(df)):
        curr = df.iloc[i]
        date = df.index[i]
        price = curr['Close']
        
        upper = curr['Donchian_High']
        lower = curr['Donchian_Low']
        
        # ------------------------
        # TRADE MANAGEMENT (Exit)
        # ------------------------
        if in_trade:
            # EXIT Condition: Price closes below the 10-period Low (Trailing Stop)
            if price < lower:
                revenue = position * price
                pnl_pct = ((price / entry_price) - 1) * 100
                capital = revenue
                position = 0
                in_trade = False
                print(f"{str(date):<25} 🔴 SELL (Exit) ${price:.2f}     ${capital:.2f}     {pnl_pct:+.2f}%")
                trades.append({'date': date, 'type': 'SELL', 'price': price, 'pnl': pnl_pct})

        # ------------------------
        # TRADE ENTRY (Signal)
        # ------------------------
        else: # Not in trade
            # ENTRY Condition: Price closes above the 20-period High
            if price > upper:
                position = capital / price
                entry_price = price
                capital = 0
                in_trade = True
                print(f"{str(date):<25} 🟢 BUY (Break) ${price:.2f}     en haberes   -")
                trades.append({'date': date, 'type': 'BUY', 'price': price})

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

def run_breakout(ticker, interval='1h'):
    print(f"🔍 Analizando Estrategia Breakout para {ticker} en {interval}...")
    
    # We need significant data, say 60 days for 1h chart
    df = yf.download(ticker, period='60d', interval=interval, progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df.columns = df.columns.get_level_values(0)
        except:
            pass
            
    df.dropna(inplace=True)
    backtest_breakout(df, 100.0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", nargs="?", default="BTC-USD", help="Ticker")
    parser.add_argument("--interval", default="1h", help="Timeframe (1h, 4h)")
    args = parser.parse_args()
    
    run_breakout(args.ticker, args.interval)
