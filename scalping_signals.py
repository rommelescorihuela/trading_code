
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import argparse

def calculate_indicators(df):
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Bollinger Bands (20, 2)
    df['BB_Mid'] = df['Close'].rolling(window=20).mean()
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Mid'] + (2 * df['BB_Std'])
    df['BB_Lower'] = df['BB_Mid'] - (2 * df['BB_Std'])
    
    return df

def detect_patterns(df):
    # Detect Candle Patterns Manually
    # Hammer / Shooting Star / Engulfing
    
    signals = []
    
    for i in range(2, len(df)):
        curr = df.iloc[i]
        prev = df.iloc[i-1]
        
        # Candle properties
        body_size = abs(curr['Close'] - curr['Open'])
        full_range = curr['High'] - curr['Low']
        lower_wick = min(curr['Open'], curr['Close']) - curr['Low']
        upper_wick = curr['High'] - max(curr['Open'], curr['Close'])
        
        is_bullish = curr['Close'] > curr['Open']
        is_bearish = curr['Close'] < curr['Open']
        prev_bearish = prev['Close'] < prev['Open']
        prev_bullish = prev['Close'] > prev['Open']

        signal = None
        pattern_name = ""

        # --- BULLISH PATTERNS (Strong Buy if at Low Band) ---
        
        # 1. Hammer (Long lower wick, small body at top)
        if lower_wick > 2 * body_size and upper_wick < body_size:
            pattern_name = "Hammer"
        
        # 2. Bullish Engulfing (Current bullish body engulfs previous bearish body)
        elif is_bullish and prev_bearish and curr['Close'] > prev['Open'] and curr['Open'] < prev['Close']:
            pattern_name = "Bullish Engulfing"

        # Check Context: Price <= Lower Band AND RSI < 35
        if pattern_name and curr['Low'] <= curr['BB_Lower'] * 1.002 and curr['RSI'] < 35:
             signal = "BUY"

        # --- BEARISH PATTERNS (Strong Sell if at High Band) ---
        
        if not signal:
            pattern_name = ""
            # 1. Shooting Star (Long upper wick, small body at bottom)
            if upper_wick > 2 * body_size and lower_wick < body_size:
                 pattern_name = "Shooting Star"
            
            # 2. Bearish Engulfing
            elif is_bearish and prev_bullish and curr['Close'] < prev['Open'] and curr['Open'] > prev['Close']:
                pattern_name = "Bearish Engulfing"

            # Check Context: Price >= Upper Band AND RSI > 65
            if pattern_name and curr['High'] >= curr['BB_Upper'] * 0.998 and curr['RSI'] > 65:
                signal = "SELL"
        
        signals.append((df.index[i], signal, pattern_name, curr['Close']))

    return signals

def backtest_strategy(signals, initial_capital=100.0, df=None):
    capital = initial_capital
    position = 0.0 # Amount of asset
    entry_price = 0.0
    trades = []
    
    print("\n" + "="*60)
    print(f"💰 BACKTEST (Capital Inicial: ${initial_capital})")
    print("-" * 60)
    print(f"{'FECHA':<25} {'ACCIÓN':<10} {'PRECIO':<10} {'BALANCE':<10} {'P&L'}")
    print("-" * 60)
    
    for date, signal, pattern, price in signals:
        current_price = price
        
        # BUY Logic: If no position, Buy All
        if signal == "BUY" and position == 0:
            position = capital / current_price
            entry_price = current_price
            capital = 0 # All in asset
            print(f"{str(date):<25} 🟢 COMPRA   ${current_price:.2f}     en haberes   -")
            trades.append({'date': date, 'type': 'BUY', 'price': current_price})
            
        # SELL Logic: If position, Sell All
        elif signal == "SELL" and position > 0:
            revenue = position * current_price
            pnl_pct = ((current_price / entry_price) - 1) * 100
            pnl_str = f"{pnl_pct:+.2f}%"
            capital = revenue
            position = 0
            print(f"{str(date):<25} 🔴 VENTA    ${current_price:.2f}     ${capital:.2f}     {pnl_str}")
            trades.append({'date': date, 'type': 'SELL', 'price': current_price, 'pnl': pnl_pct})

    # Close Position at End if still holding
    if position > 0:
        # Use last available price from signals or dataframe if passed
        # Since signals list has prices, we can use the last processed price or fetch simple last
        final_price = signals[-1][3] if signals else df['Close'].iloc[-1]
        
        # If passed df, better use the very last candle of the period
        if df is not None:
             final_price = df['Close'].iloc[-1]
             
        revenue = position * final_price
        pnl_pct = ((final_price / entry_price) - 1) * 100
        pnl_str = f"{pnl_pct:+.2f}%"
        capital = revenue
        print(f"{'CIERRE FINAL':<25} ⚠️ CLOSE    ${final_price:.2f}     ${capital:.2f}     {pnl_str}")
    
    profit_total = capital - initial_capital
    profit_pct = (profit_total / initial_capital) * 100
    
    print("-" * 60)
    print(f"RESULTADO FINAL: ${capital:.2f} ({profit_pct:+.2f}%)")
    print("="*60 + "\n")

def run_scalping_tool(ticker, interval='15m'):
    print(f"🔍 Analizando {ticker} en {interval}...")
    
    # Download extra data for indicators
    df = yf.download(ticker, period='5d', interval=interval, progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        # Flatten MultiIndex if necessary, keeping just the ticker level or dropping it
        try:
            df.columns = df.columns.get_level_values(0)
        except:
            pass
            
    if len(df) < 50:
        print("❌ No hay suficientes datos.")
        return

    df = calculate_indicators(df)
    signals = detect_patterns(df)
    
    # Plotting
    fig = go.Figure()

    # Price & Bands
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Precio'))
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='gray', width=1, dash='dash'), name='BB Upper'))
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='gray', width=1, dash='dash'), name='BB Lower'))

    # Plot Signals
    found_any = False
    print("\n⚡ SEÑALES DETECTADAS (Últimos dias):")
    print("-" * 60)
    print(f"{'FECHA':<25} {'TIPO':<10} {'PATRÓN':<20} {'PRECIO'}")
    print("-" * 60)

    for date, signal, pattern, price in signals:
        if signal:
            found_any = True
            marker_symbol = 'triangle-up' if signal == 'BUY' else 'triangle-down'
            color = 'lime' if signal == 'BUY' else 'red'
            
            fig.add_trace(go.Scatter(
                x=[date], y=[price],
                mode='markers+text',
                marker=dict(symbol=marker_symbol, size=15, color=color),
                text=[f"{signal}"],
                textposition="bottom center" if signal == 'BUY' else "top center",
                name=f"{signal} ({pattern})"
            ))
            
            emoji = "🟢" if signal == "BUY" else "🔴"
            print(f"{str(date):<25} {emoji} {signal:<6} {pattern:<20} {price:.2f}")

    if not found_any:
        print("No se encontraron señales de alta probabilidad en el periodo analizado.")
    
    fig.update_layout(title=f'Estrategia Scalping: {ticker} ({interval})', template='plotly_dark', height=800)
    
    output_file = f"scalping_{ticker}_{interval}.html"
    fig.write_html(output_file)
    print("\n" + "=" * 60)
    print(f"📈 Gráfico guardado en: {output_file}")
    print("=" * 60 + "\n")
    
    # Run Backtest
    backtest_strategy(signals, 100.0, df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", nargs="?", default="BTC-USD", help="Ticker symbol (e.g. BTC-USD, AMD)")
    parser.add_argument("--interval", default="15m", help="Timeframe (1m, 5m, 15m, 1h)")
    args = parser.parse_args()
    
    run_scalping_tool(args.ticker, args.interval)
