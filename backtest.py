import yfinance as yf
import pandas as pd
import numpy as np

def ejecutar_backtest(ticket):
    # Descargamos historial amplio
    df = yf.download(ticket, start='2024-01-01', interval='1d')
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df.dropna(inplace=True)

    # 1. Calculamos indicadores
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()

    # 2. Definimos la Estrategia (1 = Comprado, 0 = Fuera del mercado)
    df['Posicion'] = np.where(df['SMA_20'] > df['SMA_50'], 1, 0)

    # 3. Calculamos Retornos
    # Retorno diario del mercado (cambio porcentual del precio de cierre)
    df['Retorno_Mercado'] = df['Close'].pct_change()

    # Retorno de la estrategia (el retorno de mañana depende de mi posición de hoy)
    df['Retorno_Estrategia'] = df['Posicion'].shift(1) * df['Retorno_Mercado']

    # 4. Calculamos Rendimiento Acumulado (Compound returns)
    df['Cum_Mercado'] = (1 + df['Retorno_Mercado']).cumprod()
    df['Cum_Estrategia'] = (1 + df['Retorno_Estrategia']).cumprod()

    return df

def mostrar_resultados(df, capital_inicial=10000):
    final_mercado = capital_inicial * df['Cum_Mercado'].iloc[-1]
    final_estrategia = capital_inicial * df['Cum_Estrategia'].iloc[-1]
    
    rendimiento_est = (df['Cum_Estrategia'].iloc[-1] - 1) * 100

    print("\n" + "="*45)
    print(f"RESULTADOS DEL BACKTEST (Desde 2024)")
    print(f"Capital Inicial: ${capital_inicial:,}")
    print("-" * 45)
    print(f"HOLD (Solo comprar):  ${final_mercado:,.2f}")
    print(f"ESTRATEGIA CRUCE:    ${final_estrategia:,.2f}")
    print("-" * 45)
    print(f"Rendimiento Total:    {rendimiento_est:.2f}%")
    
    if final_estrategia > final_mercado:
        print("RESULTADO: La estrategia SUPERÓ al mercado. ✅")
    else:
        print("RESULTADO: El mercado ganó. Necesitamos optimizar. ❌")
    print("="*45 + "\n")

if __name__ == "__main__":
    datos = ejecutar_backtest('BTC-USD')
    mostrar_resultados(datos)