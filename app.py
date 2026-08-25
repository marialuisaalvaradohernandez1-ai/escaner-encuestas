import streamlit as st
import requests
import json
import pandas as pd
import sqlite3
import base64

# Configuración de página
st.set_page_config(page_title="Escáner de Encuestas", layout="centered")
st.title("📄 Escáner Inteligente de Encuestas")

# 1. Configurar API Key de Gemini
API_KEY = "TU_GEMINI_API_KEY"  # Reemplaza con tu API Key de Google AI Studio
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# Base de datos local SQLite
conn = sqlite3.connect("encuestas.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS resultados (id INTEGER PRIMARY KEY AUTOINCREMENT, datos TEXT)")
conn.commit()

# Función para procesar imagen con Gemini
def procesar_encuesta(bytes_imagen):
    imagen_b64 = base64.b64encode(bytes_imagen).decode("utf-8")
    
    prompt = """
    Analiza la imagen de esta encuesta. Extrae las preguntas y respuestas escritas a mano o marcadas.
    Devuelve ÚNICAMENTE un objeto JSON válido con los pares clave-valor de las respuestas.
    Ejemplo de formato: {"Nombre": "Juan", "Edad": 25, "Pregunta_1": "Excelente"}
    No agregues texto adicional ni delimitadores markdown.
    """
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": imagen_b64}}
            ]
        }]
    }
    
    try:
        response = requests.post(URL, json=payload, headers={'Content-Type': 'application/json'})
        res_json = response.json()
        texto_generado = res_json['candidates'][0]['content']['parts'][0]['text']
        texto_limpio = texto_generado.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)
    except Exception as e:
        st.error(f"Error procesando la imagen: {e}")
        return None

# 2. Captura de Imagen (Cámara o Subida de Archivo)
st.subheader("1. Capturar o Subir Encuesta")
opcion = st.radio("Selecciona origen de la imagen:", ["Usar Cámara", "Subir Imagen"])

imagen_bytes = None
if opcion == "Usar Cámara":
    foto = st.camera_input("Toma una foto a la encuesta")
    if foto:
        imagen_bytes = foto.getvalue()
else:
    archivo = st.file_uploader("Sube un archivo de imagen", type=["jpg", "png", "jpeg"])
    if archivo:
        imagen_bytes = archivo.getvalue()

# 3. Procesar y Guardar
if imagen_bytes:
    if st.button("🔍 Extraer Datos e Insertar en la Base de Datos"):
        with st.spinner("Procesando con IA..."):
            datos = procesar_encuesta(imagen_bytes)
            if datos:
                # Guardar en SQLite
                cursor.execute("INSERT INTO resultados (datos) VALUES (?)", (json.dumps(datos),))
                conn.commit()
                st.success("¡Encuesta procesada e insertada con éxito!")
                st.json(datos)

# 4. Visualizar y Exportar la Base de Datos
st.divider()
st.subheader("📊 Base de Datos de Encuestas Processadas")

cursor.execute("SELECT datos FROM resultados")
filas = cursor.fetchall()

if filas:
    registros = [json.loads(f[0]) for f in filas]
    df = pd.DataFrame(registros)
    st.dataframe(df)
    
    # Exportar a CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Base de Datos (CSV)", csv, "encuestas.csv", "text/csv")
else:
    st.info("Aún no hay registros en la base de datos.")
