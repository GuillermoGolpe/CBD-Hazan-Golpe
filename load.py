import sqlite3
import pandas as pd
from transform import transformar_datos

def cargar_base_datos():
    print("Iniciando carga en base de datos SQLite...")
    
    datos_limpios = transformar_datos()
    df_cepas = datos_limpios["cepas"]
    df_aliases = datos_limpios["aliases"]
    df_reglas = datos_limpios["reglas_scoring"]
    
    # crea el archivo .db si no existe
    conexion = sqlite3.connect('data/probiocheck.db')
    cursor = conexion.cursor()
    
    print("Guardando tablas en la base de datos...")
    # if_exists='replace' para que cada vez que se corra quede actualizado
    df_cepas.to_sql('cepas', conexion, if_exists='replace', index=False)
    df_aliases.to_sql('cepas_aliases', conexion, if_exists='replace', index=False)
    df_reglas.to_sql('reglas_scoring', conexion, if_exists='replace', index=False)
    
    # vista que une cepas con sus aliases, para busquedas desde el bot
    print("Creando la vista maestra unificada...")
    
    consulta_vista = """
    CREATE VIEW IF NOT EXISTS vista_maestra AS
    SELECT 
        c."#",
        c.Tier,
        c.Cepa AS Nombre_Oficial,
        a.nombre_alias AS Termino_Busqueda,
        a.tipo AS Tipo_Termino,
        c.Género,
        c.Especie,
        c."Fabricante/Titular",
        c."Indicaciones principales",
        c."Score estimado"
    FROM cepas c
    LEFT JOIN cepas_aliases a ON c."#" = a.cepa_id;
    """
    
    # la borramos primero para evitar conflictos si ya existia
    cursor.execute("DROP VIEW IF EXISTS vista_maestra")
    cursor.execute(consulta_vista)
    conexion.commit()
    
    cursor.execute("SELECT COUNT(*) FROM vista_maestra")
    total_filas = cursor.fetchone()[0]
    
    conexion.close()
    
    print("Carga finalizada.")
    print(f"  Base de datos:    data/probiocheck.db")
    print(f"  Registros en vista maestra: {total_filas}")

if __name__ == "__main__":
    cargar_base_datos()