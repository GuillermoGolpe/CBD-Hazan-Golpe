import pandas as pd
from extract import extraer_excel, extraer_word

def transformar_datos():
    print("Obteniendo datos en bruto...")
    datos_excel = extraer_excel()
    datos_word = extraer_word()
    
    print("Limpiando el Catalogo de Cepas...")
    df_catalogo = datos_excel['Catálogo 50 cepas'].copy()
    
    # filas sin cepa no sirven
    df_catalogo = df_catalogo.dropna(subset=['Cepa']).reset_index(drop=True)
    
    # a veces vienen con espacios de mas en el excel
    columnas_texto = ['Tier', 'Cepa', 'Género', 'Especie', 'Fabricante/Titular']
    for col in columnas_texto:
        if col in df_catalogo.columns:
            df_catalogo[col] = df_catalogo[col].astype(str).str.strip()
            
    # por si algun score viene como texto, lo forzamos a numero
    if 'Score estimado' in df_catalogo.columns:
        df_catalogo['Score estimado'] = pd.to_numeric(df_catalogo['Score estimado'], errors='coerce').fillna(0)

    print("Construyendo diccionario de sinonimos (aliases)...")
    lista_aliases = []
    
    for idx, fila in df_catalogo.iterrows():
        cepa_id = fila['#']
        nombre_oficial = fila['Cepa']
        nombres_comerciales = str(fila['Nombres comerciales (España)'])
        
        lista_aliases.append({'cepa_id': cepa_id, 'nombre_alias': nombre_oficial, 'tipo': 'oficial'})
        
        if nombres_comerciales and nombres_comerciales.lower() != 'nan':
            comerciales = [n.strip() for n in nombres_comerciales.split(',')]
            for nombre in comerciales:
                if nombre:
                    lista_aliases.append({'cepa_id': cepa_id, 'nombre_alias': nombre, 'tipo': 'comercial'})
                    
    df_aliases = pd.DataFrame(lista_aliases)

    print("Procesando reglas de negocio y checklist...")
    
    df_scoring = pd.DataFrame()
    for matriz_tabla in datos_word['tablas']:
        if len(matriz_tabla) > 0:
            encabezados = [str(e).strip() for e in matriz_tabla[0]]
            if "Indicador" in encabezados or "Fórmula" in encabezados:
                df_scoring = pd.DataFrame(matriz_tabla[1:], columns=encabezados)
                break
    
    # si no la encontro por nombre, asumimos que es la 6ta tabla
    if df_scoring.empty and len(datos_word['tablas']) >= 6:
        tabla_fallback = datos_word['tablas'][6]
        df_scoring = pd.DataFrame(tabla_fallback[1:], columns=tabla_fallback[0])

    df_checklist = datos_excel.get('Checklist curación', pd.DataFrame())

    print("Transformacion completada.")
    print(f"  Cepas procesadas:            {len(df_catalogo)}")
    print(f"  Aliases generados:           {len(df_aliases)}")
    print(f"  Reglas de scoring extraidas: {len(df_scoring)}")
    
    return {
        "cepas": df_catalogo,
        "aliases": df_aliases,
        "reglas_scoring": df_scoring,
        "checklist": df_checklist
    }

if __name__ == "__main__":
    print("--- Iniciando prueba de transformacion ---")
    datos_limpios = transformar_datos()
    
    print("\n--- Vista previa de la tabla ALIAS ---")
    print(datos_limpios["aliases"].head(7))
    
    print("\n--- Vista previa de REGLAS DE SCORING ---")
    print(datos_limpios["reglas_scoring"].head(3))