import yfinance as yf
import pandas as pd
import numpy as np

def ejecutar_backtest_con_stoploss(ticket, fast_ma, slow_ma, stop_loss_pct=0.05):
    df = yf.download(ticket, start='2024-01-01', progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df.dropna(inplace=True)

    # Indicadores
    df['SMA_fast'] = df['Close'].rolling(window=fast_ma).mean()
    df['SMA_slow'] = df['Close'].rolling(window=slow_ma).mean()

    # Variables de estado
    en_posicion = False
    precio_entrada = 0
    retornos = []

    for i in range(len(df)):
        precio_actual = df['Close'].iloc[i]
        sma_f = df['SMA_fast'].iloc[i]
        sma_s = df['SMA_slow'].iloc[i]

        # Lógica de Entrada (Cruce Dorado)
        if not en_posicion and sma_f > sma_s:
            en_posicion = True
            precio_entrada = precio_actual
            retornos.append(0) # Primer día de entrada no hay retorno

        # Lógica de Salida por Stop-Loss
        elif en_posicion and precio_actual < precio_entrada * (1 - stop_loss_pct):
            en_posicion = False
            retorno_operacion = (precio_actual / precio_entrada) - 1
            retornos.append(retorno_operacion)
            print(f"🛑 STOP-LOSS ACTIVADO en {df.index[i].date()} | Precio: {precio_actual:.2f}")

        # Lógica de Salida por Cruce (Muerte)
        elif en_posicion and sma_f < sma_s:
            en_posicion = False
            retorno_operacion = (precio_actual / precio_entrada) - 1
            retornos.append(retorno_operacion)
        
        else:
            # Si estamos dentro, calculamos el retorno diario; si no, 0
            if en_posicion:
                retornos.append(df['Close'].pct_change().iloc[i])
            else:
                retornos.append(0)

    df['Retorno_Estrategia'] = retornos
    df['Cum_Estrategia'] = (1 + df['Retorno_Estrategia']).cumprod()
    
    return df

if __name__ == "__main__":
    # Probamos con tus parámetros optimizados (5/40)
    resultado = ejecutar_backtest_con_stoploss('BTC-USD', 5, 40)
    final_val = resultado['Cum_Estrategia'].iloc[-1]
    print(f"\nResultado Final con Stop-Loss: {final_val:.2f}x")