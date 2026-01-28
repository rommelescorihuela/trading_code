
import yfinance as yf
import pandas as pd
import numpy as np
import argparse

def calculate_indicators(df):
    # EMA 50
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    # RSI 14
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df

def backtest_smart_trend(df, initial_capital=100.0, leverage=5):
    capital = initial_capital
    position = 0.0
    entry_price = 0.0
    stop_loss = 0.0
    take_profit = 0.0
    
    trades = []
    in_trade = False
    
    print("\n" + "="*75)
    print(f"🧠 SMART TREND STRATEGY (Leverage {leverage}x) - Capital: ${initial_capital}")
    print(f"Goal: Trend Following (EMA 50) + Dip Buying (RSI 40-50)")
    print("-" * 75)
    print(f"{'FECHA':<25} {'ACCIÓN':<10} {'PRECIO':<10} {'BALANCE':<10} {'P&L (REAL)'}")
    print("-" * 75)

    # Strategy Parameters
    # Buy Dip: Price > EMA 50 AND RSI < 50 AND RSI > 40
    # TP: 1.5% asset move
    # SL: 0.75% asset move
    
    tp_pct = 0.015
    sl_pct = 0.0075
    
    for i in range(50, len(df)):
        curr = df.iloc[i]
        date = df.index[i]
        price = curr['Close']
        ema = curr['EMA_50']
        rsi = curr['RSI']
        
        # ------------------------
        # TRADE MANAGEMENT (Exit)
        # ------------------------
        if in_trade:
            # Check Take Profit
            if price >= take_profit:
                # Calculate PnL
                asset_pnl = (price - entry_price) / entry_price
                real_pnl = asset_pnl * leverage
                
                capital = capital * (1 + real_pnl)
                position = 0
                in_trade = False
                print(f"{str(date):<25} 🟢 TAKE PROFIT ${price:.2f}     ${capital:.2f}     {real_pnl*100:+.2f}%")
                trades.append({'date': date, 'type': 'SELL', 'price': price, 'pnl': real_pnl*100})
            
            # Check Stop Loss
            elif price <= stop_loss:
                asset_pnl = (price - entry_price) / entry_price
                real_pnl = asset_pnl * leverage
                
                capital = capital * (1 + real_pnl)
                position = 0
                in_trade = False
                print(f"{str(date):<25} 🔴 STOP LOSS  ${price:.2f}     ${capital:.2f}     {real_pnl*100:+.2f}%")
                trades.append({'date': date, 'type': 'SELL', 'price': price, 'pnl': real_pnl*100})

            if capital <= 10:
                print(f"\n❌ CUENTA LIQUIDADA (Balance < $10).")
                break

        # ------------------------
        # TRADE ENTRY (Signal)
        # ------------------------
        else:
            # ENTRY Condition: UPTREND (Price > EMA) + PULLBACK (40 < RSI < 55)
            # We widen the range slightly to 55 to catch shallow dips incase trend is strong
            if price > ema and rsi < 55 and rsi > 35:
                entry_price = price
                # Calculate dynamic TP/SL
                take_profit = entry_price * (1 + tp_pct)
                stop_loss = entry_price * (1 - sl_pct)
                
                position = 1 
                in_trade = True
                
                print(f"{str(date):<25} ⚡ BUY (Dip)  ${price:.2f}     SL:${stop_loss:.2f} TP:${take_profit:.2f}")
                trades.append({'date': date, 'type': 'BUY', 'price': price})

    # Close Position at End
    if in_trade:
        final_price = df['Close'].iloc[-1]
        asset_pnl = (final_price - entry_price) / entry_price
        real_pnl = asset_pnl * leverage
        capital = capital * (1 + real_pnl)
        print(f"{'CIERRE FINAL':<25} ⚠️ CLOSE      ${final_price:.2f}     ${capital:.2f}     {real_pnl*100:+.2f}%")

    profit_total = capital - initial_capital
    profit_pct = (profit_total / initial_capital) * 100
    
    print("-" * 75)
    print(f"RESULTADO FINAL: ${capital:.2f} ({profit_pct:+.2f}%)")
    
    # Annualized projection
    days = (df.index[-1] - df.index[0]).days
    if days > 0:
        daily_avg = profit_pct / days
        print(f"Promedio Diario: {daily_avg:+.2f}%")
        print(f"Proyección Mensual: ~{daily_avg * 30:.2f}%")
    else:
        print("Periodo demasiado corto para calcular promedio diario.")
        
    print("="*75 + "\n")
    return profit_pct

def run_smart_trend(ticker, interval='15m', leverage=5, period='30d'):
    print(f"🔍 Analizando Estrategia SMART TREND para {ticker} en {interval} ({period}) con {leverage}x Apalancamiento...")
    
    # 60 days of 15m data is heavy, yfinance allows max 60 days for 15m.
    # Let's try 30 days to be safe and fast.
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df.columns = df.columns.get_level_values(0)
        except:
            pass
            
    df.dropna(inplace=True)
    df = calculate_indicators(df)
    return backtest_smart_trend(df, 100.0, leverage)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", nargs="?", default="BTC-USD", help="Ticker")
    parser.add_argument("--interval", default="15m", help="Timeframe (15m, 1h)")
    parser.add_argument("--leverage", type=int, default=5, help="Leverage multiplier")
    args = parser.parse_args()
    
    run_smart_trend(args.ticker, args.interval, args.leverage)
