import sqlite3
from groq import Groq
from config import API_KEY, ESQUEMA_DB

client = Groq(api_key=API_KEY)

def ejecutar_sql(query):
    """Ejecuta una consulta SQL en nuestra base de datos SQLite y retorna los resultados."""
    try:
        conexion = sqlite3.connect('data/probiocheck.db')
        cursor = conexion.cursor()
        cursor.execute(query)
        resultados = cursor.fetchall()
        conexion.close()
        return resultados
    except Exception as e:
        return f"Error en la base de datos: {e}"

def preguntar_al_bot(pregunta_usuario):
    print(f"\nHumano: {pregunta_usuario}")
    print("Bot generando consulta SQL con Llama 3.3...")
    
    respuesta = client.chat.completions.create(
        messages=[
            {"role": "system", "content": ESQUEMA_DB},
            {"role": "user", "content": f"Pregunta: {pregunta_usuario}\nSQL:"}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0
    )
    
    query_sql = respuesta.choices[0].message.content.strip().replace("```sql", "").replace("```", "")
    print(f"SQL generado: {query_sql}")
    
    datos = ejecutar_sql(query_sql)
    print(f"Resultados: {datos}")
    
    return datos

if __name__ == "__main__":
    preguntar_al_bot("¿Qué probiótico de categoría GOLD sirve para la diarrea y qué score tiene?")