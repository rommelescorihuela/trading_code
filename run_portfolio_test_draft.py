
import smart_trend_strategy
import pandas as pd

def run_portfolio():
    # Portfolio definition
    cryptos = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD', 'XRP-USD', 'ADA-USD', 'PEPE-USD', 'LINK-USD']
    stocks = ['NVDA', 'TSLA', 'AAPL', 'AMD', 'MSFT', 'AMZN', 'META', 'MSTR', 'COIN', 'SPY']
    
    all_assets = cryptos + stocks
    results = []

    print("🚀 INICIANDO TEST DE PORTAFOLIO (3 MESES - SMART TREND)")
    print("="*60)

    for ticker in all_assets:
        try:
            # Running with interval='1h' to get 3 months (90d) of data
            # Using leverage=5 as per strategy definition
            profit = smart_trend_strategy.run_smart_trend(ticker, interval='1h', leverage=5)
            
            # Use 'smart_trend_strategy' uses period='30d' by default inside.
            # We need to hack it or pass arguments if possible. 
            # Looking at the code, run_smart_trend calls yf.download(period='30d'...) HARDCODED?
            # Let's check smart_trend_strategy.py again.
            # Ah, I need to patch it or just import the backtest function and download here.
            pass 
            
        except Exception as e:
            print(f"Error en {ticker}: {e}")
            profit = -999.0 # Error flag

    # ... wait, I need to fix the period hardcoding in smart_trend_strategy first or handle data here.
    # It's better to modify smart_trend_strategy to accept 'period'.
    
if __name__ == "__main__":
    pass
