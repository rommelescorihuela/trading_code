
import yfinance as yf
import pandas as pd
import numpy as np
import argparse

def backtest_aggressive(df, initial_capital=100.0, leverage=10):
    capital = initial_capital
    position = 0.0
    entry_price = 0.0
    
    trades = []
    in_trade = False
    
    print("\n" + "="*70)
    print(f"🔥 AGGRESSIVE KAMIKAZE BOT (Leverage {leverage}x) - Capital: ${initial_capital}")
    print(f"⚠️  ADVERTENCIA: El apalancamiento magnifica ganancias Y PÉRDIDAS.")
    print("-" * 70)
    print(f"{'FECHA':<25} {'ACCIÓN':<10} {'PRECIO':<10} {'BALANCE':<10} {'P&L (REAL)'}")
    print("-" * 70)

    # Strategy: Larry Connors RSI 2 Strategy (Mean Reversion extremely fast)
    # 1. RSI (2 periods)
    # 2. Buy when RSI < 10 (Oversold)
    # 3. Sell when RSI > 90 (Overbought)
    # 4. Stop Loss? No, we pray (or use a tight one). Let's use a fixed 1% movement stop (which is 10-20% equity loss).
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=2).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=2).mean()
    rs = gain / loss
    df['RSI_2'] = 100 - (100 / (1 + rs))
    
    for i in range(5, len(df)):
        curr = df.iloc[i]
        date = df.index[i]
        price = curr['Close']
        rsi = curr['RSI_2']
        
        # ------------------------
        # TRADE MANAGEMENT (Exit)
        # ------------------------
        if in_trade:
            # EXIT Condition: RSI > 90 (Mean reverted high) OR Stop Loss
            
            # Check Stop Loss (1% move against us = 10% loss at 10x leverage)
            pct_change = (price - entry_price) / entry_price
            leveraged_pnl = pct_change * leverage
            
            # Hard Stop at -1.5% price move (which is -15% equity at 10x)
            if pct_change < -0.015: 
                revenue = capital * (1 + leveraged_pnl)
                capital = revenue
                position = 0
                in_trade = False
                print(f"{str(date):<25} 💀 STOP LOSS  ${price:.2f}     ${capital:.2f}     {leveraged_pnl*100:+.2f}%")
                trades.append({'date': date, 'type': 'SELL', 'price': price, 'pnl': leveraged_pnl*100})
            
            elif rsi > 90:
                revenue = capital * (1 + leveraged_pnl)
                capital = revenue
                position = 0
                in_trade = False
                print(f"{str(date):<25} 🚀 TAKE PROFIT ${price:.2f}     ${capital:.2f}     {leveraged_pnl*100:+.2f}%")
                trades.append({'date': date, 'type': 'SELL', 'price': price, 'pnl': leveraged_pnl*100})

            if capital <= 10: # Rekt
                print(f"\n❌ CUENTA LIQUIDADA (Balance < $10). Game Over.")
                break

        # ------------------------
        # TRADE ENTRY (Signal)
        # ------------------------
        else: 
            # ENTRY Condition: RSI < 10 (Deep Oversold)
            if rsi < 10:
                entry_price = price
                position = 1 # Just a flag
                in_trade = True
                print(f"{str(date):<25} 🟢 BUY (Aggr)  ${price:.2f}     en haberes   -")
                trades.append({'date': date, 'type': 'BUY', 'price': price})

    # Close Position at End
    if in_trade:
        final_price = df['Close'].iloc[-1]
        pct_change = (final_price - entry_price) / entry_price
        leveraged_pnl = pct_change * leverage
        capital = capital * (1 + leveraged_pnl)
        print(f"{'CIERRE FINAL':<25} ⚠️ CLOSE      ${final_price:.2f}     ${capital:.2f}     {leveraged_pnl*100:+.2f}%")

    profit_total = capital - initial_capital
    profit_pct = (profit_total / initial_capital) * 100
    
    print("-" * 70)
    print(f"RESULTADO FINAL: ${capital:.2f} ({profit_pct:+.2f}%)")
    days = (df.index[-1] - df.index[0]).days
    if days > 0:
        daily_avg = profit_pct / days
        print(f"Promedio Diario: {daily_avg:+.2f}%")
    else:
        print("Periodo demasiado corto para calcular promedio diario.")
        
    print("="*70 + "\n")

def run_aggressive(ticker, interval='5m', leverage=10):
    print(f"🔍 Ejecutando Estrategia Agresiva para {ticker} en {interval} con {leverage}x Apalancamiento...")
    
    # 5 days of 5m data
    df = yf.download(ticker, period='5d', interval=interval, progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df.columns = df.columns.get_level_values(0)
        except:
            pass
            
    df.dropna(inplace=True)
    backtest_aggressive(df, 100.0, leverage)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", nargs="?", default="BTC-USD", help="Ticker")
    parser.add_argument("--interval", default="5m", help="Timeframe (1m, 5m)")
    parser.add_argument("--leverage", type=int, default=10, help="Leverage multiplier (e.g. 10, 20)")
    args = parser.parse_args()
    
    run_aggressive(args.ticker, args.interval, args.leverage)
