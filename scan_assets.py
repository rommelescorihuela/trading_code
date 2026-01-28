
import yfinance as yf
import pandas as pd
import numpy as np

def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(window=period).mean()

import sys

def scan_market():
    # Detectar modo por argumentos
    mode = 'CRYPTO'
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'stocks':
        mode = 'STOCKS'

    if mode == 'STOCKS':
        tickers = ['NVDA', 'TSLA', 'AAPL', 'AMD', 'MSFT', 'AMZN', 'GOOGL', 'META', 'SPY', 'QQQ']
        suffix = "" # Stocks no usan sufijo en yfinance por defecto
        print(f"📊 MODO: ACCIONES (Bolsa de Valores) - {len(tickers)} activos")
    else:
        tickers = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 
                   'ADA-USD', 'DOGE-USD', 'AVAX-USD', 'LINK-USD']
        suffix = ""
        print(f"🪙 MODO: CRIPTO - {len(tickers)} activos")
    
    print("⏳ Escaneando mercado (esto puede tardar unos segundos)...")
    
    # Download data for all tickers at once for efficiency
    try:
        data = yf.download(tickers, period='5d', interval='15m', progress=False)
    except Exception as e:
        print(f"Error descargando datos: {e}")
        return

    results = []

    for ticker in tickers:
        try:
            # Extract data for specific ticker
            # yfinance returns MultiIndex if multiple tickers. 
            # Structure: data['Close'][ticker] or data.xs(ticker, level=1, axis=1)
            
            if isinstance(data.columns, pd.MultiIndex):
                df = pd.DataFrame({
                    'Open': data['Open'][ticker],
                    'High': data['High'][ticker],
                    'Low': data['Low'][ticker],
                    'Close': data['Close'][ticker],
                    'Volume': data['Volume'][ticker]
                })
            else:
                # Should not happen with multiple tickers, but fallback
                df = data.copy()

            df.dropna(inplace=True)
            
            if len(df) < 50:
                continue

            # Calculate ATR (Volatility)
            df['ATR'] = calculate_atr(df)
            current_atr = df['ATR'].iloc[-1]
            current_price = df['Close'].iloc[-1]
            
            # Volatility in % (better for comparison)
            volatility_pct = (current_atr / current_price) * 100
            
            # Volume (Average last 24h ~ 96 periods of 15m)
            avg_volume = df['Volume'].rolling(window=96).mean().iloc[-1]
            
            # Trend (Price vs SMA 50)
            sma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
            trend = "ALCISTA" if current_price > sma_50 else "BAJISTA"
            
            results.append({
                'Ticker': ticker,
                'Precio': current_price,
                'Volatilidad_15m (%)': volatility_pct,
                'Volumen_24h': avg_volume,
                'Tendencia': trend
            })
            
        except Exception as e:
            print(f"Error procesando {ticker}: {e}")
            continue

    # Create DataFrame for results
    results_df = pd.DataFrame(results)
    
    # Ranking for Scalping (High Volatility is good)
    scalping_df = results_df.sort_values(by='Volatilidad_15m (%)', ascending=False).reset_index(drop=True)
    
    # Ranking for DayTrading (High Volume + Trend is good)
    # Simple heuristic: Volume is key for day trading liquidity.
    daytrading_df = results_df.sort_values(by='Volumen_24h', ascending=False).reset_index(drop=True)

    print("\n" + "="*60)
    print("🚀 MEJORES ACTIVOS PARA SCALPING (Mayor Volatilidad)")
    print("="*60)
    print(scalping_df[['Ticker', 'Precio', 'Volatilidad_15m (%)', 'Tendencia']].head(5).to_string(index=False))
    
    print("\n" + "="*60)
    print("💼 MEJORES ACTIVOS PARA DAYTRADING (Mayor Volumen/Liquidez)")
    print("="*60)
    print(daytrading_df[['Ticker', 'Precio', 'Volumen_24h', 'Tendencia']].head(5).to_string(index=False))
    print("="*60 + "\n")

if __name__ == "__main__":
    scan_market()
