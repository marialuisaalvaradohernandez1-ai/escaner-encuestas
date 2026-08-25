import base64
import json
import requests

API_KEY = "TU_GEMINI_API_KEY"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

def extraer_datos_encuesta(ruta_imagen):
    # 1. Leer imagen y convertir a Base64
    with open(ruta_imagen, "rb") as image_file:
        imagen_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    # 2. Prompt estructurado para forzar JSON
    prompt = """
    Analiza esta imagen de una encuesta manuscrita o impresa.
    Extrae todas las preguntas y respuestas.
    Devuelve ÚNICAMENTE un objeto JSON con los pares clave-valor de la encuesta.
    No agregues texto explicativo ni bloques markdown de código.
    """

    # 3. Payload
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": imagen_base64
                    }
                }
            ]
        }]
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(URL, headers=headers, json=payload)
    datos_json = response.json()

    # 4. Manejo seguro de la respuesta
    try:
        texto_respuesta = datos_json['candidates'][0]['content']['parts'][0]['text']
        # Limpiar posibles delimitadores markdown
        texto_limpio = texto_respuesta.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)
    except Exception as e:
        print("Error procesando la respuesta:", e)
        print("Respuesta raw de la API:", datos_json)
        return None
