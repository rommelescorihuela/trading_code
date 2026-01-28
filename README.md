# Trading Bot & Backtesting Framework

Este repositorio contiene un conjunto de herramientas y estrategias de trading algorítmico desarrolladas en Python. Incluye scripts para escaneo de mercado, backtesting de estrategias (Scalping, Swing, Trend Following) y utilidades para obtener datos financieros.

## Estructura del Proyecto

### 1. Estrategias de Trading
Scripts independientes que implementan y prueban diferentes lógicas de trading:

*   **`aggressive_strategy.py`**: Estrategia de reversión a la media "Kamikaze" de alto riesgo. Usa "Connors RSI" (RSI de 2 periodos) para entrar en sobreventa profunda (<10) y salir en sobrecompra (>90). Incluye Stop Loss fijo. Apalancamiento configurable.
*   **`breakout_strategy.py`**: Estrategia de ruptura de Canales de Donchian. Compra cuando el precio rompe el máximo de 20 periodos y vende cuando cae por debajo del mínimo de 10 periodos (Trailing Stop).
*   **`fib_strategy.py`**: Estrategia de Swing Trading basada en retrocesos de Fibonacci. Busca entradas en el "Golden Pocket" (retracción 0.618) durante tendencias alcistas confirmadas por EMA 50.
*   **`smart_trend_strategy.py`**: Estrategia de seguimiento de tendencia inteligente. Combina EMA 50 para identificar la tendencia y RSI (rangos 40-55) para comprar en retrocesos (dips). Gestiona TP y SL dinámicos.
*   **`scalping_signals.py`**: Herramienta para Scalping. Detecta patrones de velas (Martillo, Envolvente, Estrella Fugaz) combinados con Bandas de Bollinger y RSI. Genera un reporte visual en HTML (`scalping_TICKER.html`).

### 2. Herramientas y Utilidades
*   **`scan_assets.py`**: Escáner de mercado versátil (Cripto y Acciones). Calcula volatilidad (ATR) y volumen promedio para recomendar activos:
    *   *Modo Scalping*: Prioriza alta volatilidad en 15m.
    *   *Modo DayTrading*: Prioriza alto volumen y liquidez.
*   **`fetch_data.py`**: Utilidad para descargar datos y analizar Cruces de Medias (SMA 20 vs SMA 50). Detecta "Golden Cross" y "Death Cross".
*   **`api.py`**: API REST básica (usando FastAPI) para consultar logs de optimización almacenados en una base de datos PostgreSQL.
*   **`optimizer_db.py`**: Script para optimizar parámetros de estrategias (cruce de medias) mediante fuerza bruta y guardar resultados en PostgreSQL.

### 3. Ejecución y Backtesting
*   **`run_portfolio_test.py`**: Script maestro para ejecutar la estrategia `Smart Trend` sobre un portafolio diversificado de activos (BTC, ETH, SOL, NVDA, TSLA, etc.) y comparar rendimientos a 3 meses.
*   **`backtest.py`**: Motor de backtesting simple para probar estrategias de cruce de medias (SMA).
*   **`backtest_pro.py`**: Versión mejorada del motor de backtesting que incluye lógica de Stop Loss.
*   **`run_portfolio_test_draft.py`**: Borrador/versión anterior del runner de portafolio.

## Requisitos

El proyecto utiliza las siguientes librerías de Python:

*   **`yfinance`**: Descarga de datos históricos de Yahoo Finance.
*   **`pandas` & `numpy`**: Procesamiento y análisis de series temporales.
*   **`plotly`**: Generación de gráficos interactivos (HTML).
*   **`fastapi` & `uvicorn`**: Servidor de API (para `api.py`).
*   **`psycopg2`**: Driver de base de datos PostgreSQL (para `optimizer_db.py` y `api.py`).

Para instalar las dependencias:
```bash
pip install yfinance pandas numpy plotly fastapi uvicorn psycopg2-binary
```

## Ejemplos de Uso

### 1. Escanear el Mercado
Encuentra las criptomonedas más volátiles para operar ahora mismo:
```bash
python scan_assets.py
```
O busca acciones (Stocks) con mayor volumen:
```bash
python scan_assets.py stocks
```

### 2. Probar una Estrategia (Backtest)
Ejecuta la estrategia "Smart Trend" en Bitcoin con apalancamiento 5x:
```bash
python smart_trend_strategy.py BTC-USD --interval 15m --leverage 5
```
Prueba la estrategia "Aggressive" en Solana:
```bash
python aggressive_strategy.py SOL-USD --interval 5m --leverage 10
```

### 3. Generar Señales de Scalping
Analiza Ethereum en 15 minutos y genera un gráfico con las señales detectadas:
```bash
python scalping_signals.py ETH-USD --interval 15m
```
Esto creará un archivo `scalping_ETH-USD_15m.html` que puedes abrir en tu navegador.

### 4. Simulación de Portafolio
Corre una simulación de rendimiento de los últimos 3 meses para una cesta de activos:
```bash
python run_portfolio_test.py
```
