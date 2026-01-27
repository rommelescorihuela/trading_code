from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

def get_db_connection():
    return psycopg2.connect(
        dbname="trading_db",
        user="innovacion2",
        password="tu_password",
        host="localhost"
    )

@app.get("/mejores-estrategias")
def leer_optimizaciones():
    conn = get_db_connection()
    # RealDictCursor nos devuelve los datos como JSON listo para la API
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM optimization_logs ORDER BY run_date DESC LIMIT 10")
    resultados = cur.fetchall()
    cur.close()
    conn.close()
    return resultados

# Para correrlo: uvicorn api:app --reload