import streamlit as st
import sqlite3
import pandas as pd
from groq import Groq
from config import API_KEY, ESQUEMA_DB, CRITERIOS_SCORING

st.set_page_config(page_title="ProbioCheck - Bot Intérprete", page_icon="🔬", layout="wide")
MODEL_NAME = "llama-3.3-70b-versatile"
client = Groq(api_key=API_KEY)

# FUNCIONES DE BACKEND 

def ejecutar_sql(query):
    """Ejecuta SQL en SQLite y devuelve un DataFrame."""
    try:
        with sqlite3.connect('data/probiocheck.db') as conexion:
            df = pd.read_sql_query(query, conexion)
        return df, None
    except Exception as e:
        return None, str(e)

def llamar_ia(system_prompt, user_prompt, temperature=0):
    """Función centralizada para peticiones a Groq."""
    respuesta = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model=MODEL_NAME,
        temperature=temperature
    )
    return respuesta.choices[0].message.content

@st.cache_data
def cargar_dataset_completo():
    """Carga todas las cepas únicas de la BD con sus aliases comerciales agrupados."""
    sql = """
        SELECT
            Nombre_Oficial, Tier, "Score estimado",
            "Indicaciones principales", "Fabricante/Titular", Género, Especie,
            GROUP_CONCAT(
                CASE WHEN Tipo_Termino = 'comercial' THEN Termino_Busqueda END, ', '
            ) AS Nombres_comerciales
        FROM vista_maestra
        GROUP BY Nombre_Oficial
        ORDER BY CAST("Score estimado" AS REAL) DESC
    """
    df_full, _ = ejecutar_sql(sql)
    return df_full if df_full is not None else pd.DataFrame()

def generar_sql_ia(pregunta):
    """Genera la consulta SQL basada en el esquema definido."""
    query = llamar_ia(ESQUEMA_DB, f"Pregunta: {pregunta}\nSQL:", temperature=0)
    return query.strip().replace("```sql", "").replace("```", "")

def generar_analisis_ia(pregunta):
    """Genera el análisis siempre desde el contexto completo de la BD.
    El SQL no condiciona esta función: el modelo razona sobre los 50 registros siempre.
    """
    df_completo = cargar_dataset_completo()
    contexto_global = df_completo.to_markdown(index=False) if not df_completo.empty else "(no disponible)"

    system_prompt = (
        "Eres un experto en probióticos con base en evidencia científica y analista de datos. "
        "El Score estimado va de 0 a 4.7: valores ≥ 4.0 indican alta evidencia (Tier GOLD), "
        "entre 2.5 y 3.9 evidencia moderada, y < 2.5 evidencia limitada. "
        f"La metodología de scoring es la siguiente: {CRITERIOS_SCORING} "
        "Razona como un analista: busca patrones, compara opciones y detecta lo que no es obvio. "
        "Al nombrar una cepa, usa su nombre comercial más conocido (columna Nombres_comerciales) "
        "seguido del nombre oficial entre paréntesis si aporta precisión; si no tiene nombre comercial, solo di el nombre oficial. "
        "Pon los nombres siempre entre comillas. "
        "NO inventes ni supongas información que no esté en los datos. Si la pregunta no tiene respuesta en la base de datos, dílo claramente. "
        "NO añadas consejos genéricos ni afirmaciones de sentido común. "
        "Responde siempre en español, de forma profesional y concisa."
    )
    user_prompt = f"""El usuario preguntó: "{pregunta}"

Base de datos completa — todas las cepas disponibles, ordenadas por Score ({len(df_completo)} en total):
{contexto_global}

No uses frases como "en la base de datos" o "en el conjunto": integra los datos directamente.
Redacta UN solo párrafo que:
1. Empieza directamente con el hallazgo más importante. Solo usa "Sí"/"No" al inicio si la pregunta es estrictamente binaria (¿existe exactamente esto? ¿hay alguno?) Y la respuesta es inequívoca. En cualquier otro caso —comparativas, rankings, patrones, análisis— empieza con el dato o conclusión clave, sin preámbulo.
2. Apoya la respuesta con los datos más relevantes (Tier, Score, indicaciones) y su posición relativa.
3. Señala diferencias o patrones clave si los hay.
4. Si los datos no contienen información relevante para responder, dilo claramente sin inventar ni rellenar.
No uses listas, markdown ni encabezados. Solo texto corrido en español."""
    return llamar_ia(system_prompt, user_prompt, temperature=0.2)

# UI

def renderizar_mensaje_asistente(contenido, df=None, sql=None):
    """Renderiza de forma consistente el contenido del bot."""
    st.write(contenido)
    if df is not None and not df.empty:
        st.write("**Datos extraidos:**")
        st.dataframe(df, width="stretch")
    if sql:
        with st.expander("Ver consulta SQL generada"):
            st.code(sql, language="sql")

# LOGICA PRINCIPAL

st.title("ProbioCheck: Bot Interprete de Datos")
st.subheader("Mineria de datos sobre evidencia cientifica de probioticos")

with st.sidebar:
    if st.button("Limpiar historial"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.write(msg["content"])
        else:
            renderizar_mensaje_asistente(msg["content"], msg.get("df"), msg.get("sql"))


if prompt := st.chat_input(""):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Consultando..."):
                query = generar_sql_ia(prompt)
                df_res, err = ejecutar_sql(query)

            # El análisis siempre corre desde el contexto completo.
            # El SQL solo decide si hay tabla para mostrar al usuario.
            df_para_mostrar = df_res if not err and df_res is not None and not df_res.empty else None

            with st.spinner("Analizando..."):
                analisis = generar_analisis_ia(prompt)
                renderizar_mensaje_asistente(analisis, df_para_mostrar, query)
                st.session_state.messages.append({
                    "role": "assistant", "content": analisis,
                    "df": df_para_mostrar, "sql": query
                })
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str:
                st.warning("Limite de la API alcanzado. Espera un momento.")
            else:
                st.error(f"Error: {e}")