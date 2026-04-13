API_KEY = "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"

ESQUEMA_DB = """
BASE DE DATOS: SQLite. VISTA: 'vista_maestra'

COLUMNAS Y SIGNIFICADO:
- "#"                       : ID numérico de la cepa (INTEGER)
- Tier                      : Nivel de evidencia. Valores posibles (mayúsculas exactas): GOLD, SILVER, BRONZE, EMERGENTE, WARNING
- Nombre_Oficial            : Nombre científico canónico de la cepa (ej. "Lactobacillus rhamnosus GG")
- Termino_Busqueda          : Alias por el que se busca la cepa (nombre oficial o marca comercial)
- Tipo_Termino              : 'oficial' (nombre científico) o 'comercial' (marca, producto)
- Género                    : Género taxonómico (ej. Lacticaseibacillus)
- Especie                   : Especie taxonómica (ej. rhamnosus)
- "Fabricante/Titular"      : Empresa propietaria o distribuidora
- "Indicaciones principales": Cadena de texto con indicaciones separadas por comas (ej. "Diarrea ATB, SII, inmunidad")
- "Score estimado"          : Puntuación de evidencia de 0.0 a 4.7 almacenada como TEXT; usa CAST("Score estimado" AS REAL) para ordenar o comparar numéricamente

REGLAS DE CONSTRUCCIÓN SQL:
1. Usa siempre SELECT DISTINCT para evitar duplicados por alias.
2. Usa comillas dobles para columnas con espacios o caracteres especiales.
3. Para buscar síntomas/indicaciones: LIKE '%termino%' sobre "Indicaciones principales".
4. Para buscar marca o cepa por nombre: LIKE '%termino%' sobre Termino_Busqueda.
5. Para buscar por nivel de calidad: WHERE Tier = 'GOLD'  (mayúsculas exactas).
6. Para rankings o "el mejor/más": ORDER BY CAST("Score estimado" AS REAL) DESC con LIMIT 10.
7. Si la pregunta menciona una marca comercial: filtra también por Tipo_Termino = 'comercial'.
8. Devuelve SOLO el código SQL plano, sin markdown, sin explicaciones.
"""

CRITERIOS_SCORING = """
CRITERIOS DE SELECCIÓN Y PUNTUACIÓN DE CEPAS (metodología interna):

Los criterios que determinan el Tier y Score de cada cepa son, por orden de importancia:

[Peso ALTO]
- Volumen de evidencia clínica: cantidad de RCTs y meta-análisis publicados. Prioridad a cepas presentes en análisis globales (>1.600 estudios en ClinicalTrials.gov/ICTRP). Satisfecho principalmente por GOLD y SILVER.
- Presencia en guías clínicas: mención en WGO 2023, ESPGHAN, AGA, SEFAC-SEMERGEN 2024 u otras guías internacionales. Casi exclusivo de GOLD.
- Disponibilidad en España: presencia en productos de farmacia o alimentación accesibles en el mercado español. Satisfecho por GOLD, SILVER y algunos BRONZE.
- Microbiofakes representativos: se incluyeron deliberadamente 5 anti-ejemplos (productos sin cepa identificada) como WARNING para calibrar el scoring. Su Score es 0.0 por definición.

[Peso MEDIO]
- Diversidad de indicaciones: cobertura de áreas GI, inmunidad, alergia, salud mental, salud vaginal, oral, metabólica y pediátrica. Presente en todas las categorías.
- Diversidad de géneros microbianos: representación de Lactobacillus s.l., Bifidobacterium, Saccharomyces, Bacillus, E. coli Nissle, Akkermansia, Faecalibacterium, Pediococcus, Streptococcus, Clostridium. (aprox. 40 de 50 cepas).
- Equilibrio farmacia/alimentación: ~45% farmacia, ~40% mixto, ~15% alimentario.
- Cepas españolas: L. fermentum CECT 5716 (Biosearch Life, Granada) y mezclas de AB-Biotics (Barcelona). Solo 3 cepas.
- Psicobióticos: cepas con evidencia en el eje intestino-cerebro (L. helveticus R0052 + B. longum R0175, B. longum 1714, L. plantarum PS128).

[Peso BAJO]
- Next-generation probiotics: cepas emergentes que representan el futuro del campo (Akkermansia, Faecalibacterium, Christensenella, Roseburia). Corresponden a BRONZE y EMERGENTE.
"""