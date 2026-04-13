# Guía de instalación

Se asume que la computadora tiene Python 3.8 o superior.

---

**Paso 1 —** Abrir la terminal en la carpeta del proyecto. La terminal debe estar situada en la carpeta raíz del proyecto.

**Paso 2 —** Crear un entorno virtual:

| Sistema | Comando |
|---|---|
| Mac / Linux | `python3 -m venv .venv` |
| Windows | `python -m venv .venv` |

**Paso 3 —** Activar el entorno virtual:

| Sistema | Comando |
|---|---|
| Mac / Linux | `source .venv/bin/activate` |
| Windows | `.venv\Scripts\activate` |

> **Nota (Windows):** Si da un error de "scripts deshabilitados", abrir PowerShell como administrador y ejecutar `Set-ExecutionPolicy Unrestricted -Scope CurrentUser`, y luego reintentar.

**Paso 4 —** Instalar las dependencias:

```bash
pip install -r requirements.txt
```

> **Nota:** Si da error de instalación, se recomienda instalar una por una, por ejemplo: `pip install streamlit`

**Paso 5 —** Ejecutar la aplicación:

```bash
streamlit run app.py
```

---

## Consideraciones

1. Por fines educativos, la clave de la API de Groq se encuentra en el archivo `config.py`. Si se quisiera llevar a producción, esta clave deberá ser manejada de forma privada y por cada usuario en su computadora. Como el repositorio es público para poder evaluarlo, en caso de que la clave se vea comprometida basta con cambiar la clave (sin subirla al repositorio), puede obtener su clave en: https://console.groq.com/keys


2. La base de datos ya viene creada a partir de los documentos que se encuentran en la carpeta `data/`. Si se quisiera actualizar la base de datos, se deben actualizar los documentos y ejecutar el archivo `load.py` con el siguiente comando:
   ```bash
   python load.py
   ```
