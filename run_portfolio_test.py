
import smart_trend_strategy
import pandas as pd
import sys

def run_portfolio():
    # Portfolio definition (Most Liquid & Volatile)
    cryptos = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD', 'DOGE-USD', 'PEPE-USD', 'LINK-USD']
    stocks = ['NVDA', 'TSLA', 'AAPL', 'AMD', 'MSFT', 'AMZN', 'META', 'MSTR', 'COIN', 'SPY']
    
    all_assets = cryptos + stocks
    results = []

    print("\n" + "🚀"*10 + " INICIANDO TEST DE PORTAFOLIO (3 MESES - SMART TREND) " + "🚀"*10)
    print("="*80)

    for ticker in all_assets:
        try:
            # Using interval='1h' to allow >60 days history (yfinance restriction on 15m)
            # period='90d' for 3 months
            profit = smart_trend_strategy.run_smart_trend(ticker, interval='1h', leverage=5, period='90d')
            
            # Categorize
            asset_type = 'CRYPTO' if '-USD' in ticker else 'STOCK'
            
            results.append({
                'Ticker': ticker,
                'Type': asset_type,
                'Profit %': profit
            })
            
        except Exception as e:
            print(f"❌ Error en {ticker}: {e}")
            results.append({'Ticker': ticker, 'Type': 'ERROR', 'Profit %': -999})

    # Create DF and Sort
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values(by='Profit %', ascending=False).reset_index(drop=True)
    
    print("\n" + "="*80)
    print("🏆 RESULTADOS FINALES DEL PORTAFOLIO (3 MESES)")
    print("="*80)
    print(df_results.to_string(index=False))
    print("="*80 + "\n")

if __name__ == "__main__":
    run_portfolio()
