import yfinance as yf
import pandas as pd
import numpy as np
import psycopg2

def test_strategy(df, fast_ma, slow_ma):
    df_temp = df.copy()
    df_temp['fast'] = df_temp['Close'].rolling(window=fast_ma).mean()
    df_temp['slow'] = df_temp['Close'].rolling(window=slow_ma).mean()
    df_temp['pos'] = np.where(df_temp['fast'] > df_temp['slow'], 1, 0)
    df_temp['ret'] = df_temp['pos'].shift(1) * df_temp['Close'].pct_change()
    return (1 + df_temp['ret']).prod()

def guardar_mejor_resultado(simbolo, fast, slow, retorno):
    try:
        conn = psycopg2.connect(
            dbname="trading_data",
            user="postgres", # Tu usuario de Linux
            password="postgres", 
            host="localhost"
        )
        cur = conn.cursor()
        query = """
        INSERT INTO optimization_logs (symbol, best_fast, best_slow, final_return)
        VALUES (%s, %s, %s, %s)
        """
        cur.execute(query, (simbolo, fast, slow, float(retorno)))
        conn.commit()
        cur.close()
        conn.close()
        print(f"📊 Resultado guardado: SMA {fast}/{slow} con {retorno:.2f}x")
    except Exception as e:
        print(f"❌ Error DB: {e}")

if __name__ == "__main__":
    simbolo = 'BTC-USD'
    df = yf.download(simbolo, start='2024-01-01', progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df.dropna(inplace=True)

    mejor_ret = 0
    mejores_p = (0, 0)

    for corta in range(5, 30, 5):
        for larga in range(40, 100, 10):
            res = test_strategy(df, corta, larga)
            if res > mejor_ret:
                mejor_ret = res
                mejores_p = (corta, larga)

    guardar_mejor_resultado(simbolo, mejores_p[0], mejores_p[1], mejor_ret)