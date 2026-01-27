import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def analizar_cruce_dorado(ticket):
    # Bajamos datos de los últimos 2 años para tener suficiente historial para la SMA 200
    df = yf.download(ticket, start='2024-01-01', interval='1d')
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df.dropna(inplace=True)

    # Calculamos las dos medias
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # Lógica de detección:
    # Golden Cross: SMA_20 cruza por encima de SMA_50
    # Death Cross: SMA_20 cruza por debajo de SMA_50
    df['Señal'] = 0.0
    # Usamos np.where para vectorizar (es mucho más rápido que un loop)
    import numpy as np
    df['Señal'] = np.where(df['SMA_20'] > df['SMA_50'], 1.0, 0.0)
    
    # El cruce ocurre cuando la señal de hoy es diferente a la de ayer
    df['Cruce'] = df['Señal'].diff()
    
    return df

def imprimir_estado(df):
    ultimo_cierre = df['Close'].iloc[-1]
    sma20 = df['SMA_20'].iloc[-1]
    sma50 = df['SMA_50'].iloc[-1]
    ultimo_cruce = df['Cruce'].iloc[-1]

    print("\n" + "="*40)
    print(f"ANÁLISIS DE CRUCES - BTC/USD")
    print(f"Cierre: {ultimo_cierre:.2f} | SMA20: {sma20:.2f} | SMA50: {sma50:.2f}")
    
    if ultimo_cruce == 1.0:
        print("🚀 ¡ALERTA! Se acaba de producir un GOLDEN CROSS hoy.")
    elif ultimo_cruce == -1.0:
        print("⚠️ ¡ALERTA! Se acaba de producir un DEATH CROSS hoy.")
    elif sma20 > sma50:
        print("Estado: Tendencia ALCISTA (SMA20 arriba de SMA50)")
    else:
        print("Estado: Tendencia BAJISTA (SMA20 debajo de SMA50)")
    print("="*40 + "\n")

def generar_grafico_cruces(df, ticket):
    fig = go.Figure()

    # Velas
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Precio'))

    # Media Rápida
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='cyan', width=1), name='SMA 20 (Rápida)'))

    # Media Lenta
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='orange', width=2), name='SMA 50 (Lenta)'))

    # Marcar los cruces en el gráfico
    cruces_alcistas = df[df['Cruce'] == 1.0]
    fig.add_trace(go.Scatter(x=cruces_alcistas.index, y=cruces_alcistas['SMA_20'], mode='markers', marker=dict(symbol='triangle-up', size=15, color='green'), name='Cruce Dorado'))

    fig.update_layout(title=f'Detección de Cruces: {ticket}', template='plotly_dark', xaxis_rangeslider_visible=False)
    fig.write_html("cruces_trading.html")

if __name__ == "__main__":
    simbolo = 'BTC-USD'
    datos = analizar_cruce_dorado(simbolo)
    imprimir_estado(datos)
    generar_grafico_cruces(datos, simbolo)