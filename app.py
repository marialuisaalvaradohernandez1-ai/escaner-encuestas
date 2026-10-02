import base64
import hashlib
import io
import json
import random
import re
import sqlite3
import time
from io import BytesIO
from typing import Any, Dict, List, Optional
 
import pandas as pd
import requests
import streamlit as st
from PIL import Image, ImageOps
 
from estilos import aplicar_estilos, encabezado, panel_resumen
 
# =========================================================
# CONFIGURACIÓN
# =========================================================
st.set_page_config(page_title="Escáner Inteligente de Encuestas", page_icon="📷", layout="wide")
aplicar_estilos()

# Solo corregimos la visibilidad del texto de los campos.
# No modifica la lógica, base de datos ni el diseño general.
st.markdown("""
<style>
section[data-testid="stSidebar"] input {
    color: #172554 !important;
    -webkit-text-fill-color: #172554 !important;
    caret-color: #172554 !important;
}
section[data-testid="stSidebar"] input::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
}
</style>
""", unsafe_allow_html=True)

encabezado()
 
DB_NAME = "encuestas.db"
MODELOS_GEMINI_DEFECTO = "gemini-3.8-flash, gemini-3.7-flash, gemini-3.6-flash"
OLLAMA_HOST_DEFECTO = "http://localhost:11434"
OLLAMA_MODELO_DEFECTO = "qwen2.5vl:7b"
MAX_IMAGE_SIDE = 2000
JPEG_QUALITY = 88
MAX_REINTENTOS = 5
PAUSA_ENTRE_IMAGENES = 2  # segundos
 
T1 = "Encuesta 1 - Inglés / Programación"
T2 = "Encuesta 2 - Plática STEM"
 
PLANTILLAS = {
    T1: {"id": "encuesta_ingles_programacion", "descripcion": "Inglés (8 preguntas) y Programación (7 preguntas). Opciones: a, b, c."},
    T2: {"id": "encuesta_platica_stem", "descripcion": "Encuesta de plática STEM."},
}
PREGUNTAS_ESPERADAS = {"Inglés": 8, "Programación": 7}
 
COLS_E1 = ["Materia", "Nombre", "Grupo", "Fecha"] + [f"Pregunta {i}" for i in range(1, 9)]
COLS_E2 = ["Nombre", "Escuela", "Grado y grupo", "Fecha", "Pregunta 1", "Pregunta 2",
           "Pregunta 3a", "Pregunta 3b", "Pregunta 3c", "Pregunta 3d", "Pregunta 4", "Pregunta 5"]
 
 
def secreto(nombre: str, defecto: str = "") -> str:
    try:
        return str(st.secrets[nombre]).strip()
    except Exception:
        return defecto
 
 
# =========================================================
# AUTENTICACIÓN
# =========================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
 
if not st.session_state.authenticated:
    st.sidebar.title("🔐 Acceso")
    ADMIN_PASS = secreto("APP_PASSWORD")
    if not ADMIN_PASS:
        st.error("❌ Falta APP_PASSWORD en Secrets.")
        st.stop()
    password = st.sidebar.text_input("Contraseña de acceso:", type="default")
    if st.sidebar.button("Ingresar"):
        if password == ADMIN_PASS:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.sidebar.error("❌ Contraseña incorrecta")
    st.info("Ingresa la contraseña en el panel lateral para continuar.")
    st.stop()
 
API_KEY = secreto("GEMINI_API_KEY")
 
for clave, valor in {"pendientes": [], "hashes_pend": set(), "cache_gemini": {}}.items():
    if clave not in st.session_state:
        st.session_state[clave] = valor
 
# =========================================================
# BASE DE DATOS
# =========================================================
def init_db() -> None:
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            datos_json TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS imagenes_procesadas (
            clave TEXT PRIMARY KEY,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        conn.commit()
 
 
init_db()
 
 
def guardar_registro(datos: Dict[str, Any]) -> None:
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO resultados (datos_json) VALUES (?)",
                     (json.dumps(datos, ensure_ascii=False),))
        conn.commit()
 
 
def leer_base_datos() -> pd.DataFrame:
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query(
            "SELECT id, fecha_registro, datos_json FROM resultados ORDER BY id DESC", conn)
 
 
def imagenes_ya_procesadas() -> set:
    with sqlite3.connect(DB_NAME) as conn:
        return {r[0] for r in conn.execute("SELECT clave FROM imagenes_procesadas")}
 
 
def marcar_imagenes(claves: set) -> None:
    with sqlite3.connect(DB_NAME) as conn:
        conn.executemany("INSERT OR IGNORE INTO imagenes_procesadas (clave) VALUES (?)",
                         [(c,) for c in claves])
        conn.commit()
 
 
def clave_registro(r: Dict[str, Any]) -> tuple:
    return tuple(str(r.get(k) or "").strip().lower()
                 for k in ("Tipo Encuesta", "Nombre", "Grupo", "Grado y grupo", "Materia", "Fecha"))
 
 
def claves_existentes() -> set:
    claves = set()
    for _, fila in leer_base_datos().iterrows():
        try:
            d = json.loads(fila["datos_json"])
            if isinstance(d, dict):
                claves.add(clave_registro(d))
        except Exception:
            pass
    return claves
 
 
# =========================================================
# LIMPIEZA Y NORMALIZACIÓN (no corrige ortografía)
# =========================================================
def limpiar_texto(valor: Any) -> Optional[str]:
    if valor is None:
        return None
    valor = str(valor).strip()
    return valor or None
 
 
def normalizar_nombre(n: Optional[str]) -> Optional[str]:
    return " ".join(n.split()).title() if n else n
 
 
def normalizar_grupo(g: Optional[str]) -> Optional[str]:
    return re.sub(r"[\s\-]+", "", g).upper() if g else g
 
 
def limpiar_materia(m: Any) -> Optional[str]:
    t = str(m or "").strip().lower()
    if "ingl" in t:
        return "Inglés"
    if "program" in t or "stem" in t:
        return "Programación"
    return None
 
 
def limpiar_inciso(valor: Any, permitidos: set) -> Optional[str]:
    if valor is None:
        return None
    v = str(valor).strip().lower()
    return v if v in permitidos else None
 
 
def extraer_json(texto: str) -> Dict[str, Any]:
    texto = texto.strip()
    if texto.startswith("```"):
        lineas = texto.splitlines()[1:]
        if lineas and lineas[-1].strip() == "```":
            lineas = lineas[:-1]
        texto = "\n".join(lineas).strip()
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError:
        i, f = texto.find("{"), texto.rfind("}")
        if i == -1 or f <= i:
            raise ValueError("El modelo no devolvió un objeto JSON válido.")
        datos = json.loads(texto[i:f + 1])
    if not isinstance(datos, dict):
        raise ValueError("El modelo no devolvió un objeto JSON.")
    return datos
 
 
# =========================================================
# ESQUEMAS
# =========================================================
def esquema_encuesta_1() -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "Nombre": {"type": ["string", "null"]},
            "Grupo": {"type": ["string", "null"]},
            "Fecha": {"type": ["string", "null"]},
            "Secciones": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Materia": {"type": "string", "enum": ["Inglés", "Programación"]},
                        "Respuestas": {"type": "array",
                                       "items": {"type": ["string", "null"], "enum": ["a", "b", "c", None]}},
                    },
                    "required": ["Materia", "Respuestas"],
                },
            },
        },
        "required": ["Nombre", "Grupo", "Fecha", "Secciones"],
    }
 
 
def esquema_encuesta_2() -> Dict[str, Any]:
    ab = {"type": ["string", "null"], "enum": ["a", "b", None]}
    abc = {"type": ["string", "null"], "enum": ["a", "b", "c", None]}
    props = {
        "Nombre": {"type": ["string", "null"]},
        "Escuela": {"type": ["string", "null"]},
        "Grupo": {"type": ["string", "null"]},
        "Fecha": {"type": ["string", "null"]},
        "P1": ab, "P2": abc, "P3a": ab, "P3b": ab, "P3c": ab, "P3d": ab, "P4": abc,
        "P5": {"type": ["string", "null"]},
    }
    return {"type": "object", "properties": props, "required": list(props)}
 
 
def convertir_esquema_gemini(s: Any) -> Any:
    """JSON Schema estándar -> subconjunto que acepta Gemini."""
    if isinstance(s, list):
        return [convertir_esquema_gemini(x) for x in s]
    if not isinstance(s, dict):
        return s
    nuevo = {}
    for k, v in s.items():
        if k == "type" and isinstance(v, list):
            tipos = [t for t in v if t != "null"]
            nuevo["type"] = tipos[0] if tipos else "string"
            if "null" in v:
                nuevo["nullable"] = True
        elif k == "enum" and isinstance(v, list):
            nuevo["enum"] = [x for x in v if x is not None]
            if None in v:
                nuevo["nullable"] = True
        elif k == "properties":
            nuevo[k] = {p: convertir_esquema_gemini(d) for p, d in v.items()}
        else:
            nuevo[k] = convertir_esquema_gemini(v)
    return nuevo
 
 
# =========================================================
# PROMPTS
# =========================================================
PROMPT_ENCUESTA_1 = """
Analiza esta imagen de una encuesta escolar: ENCUESTA 1, INGLÉS / PROGRAMACIÓN.
La foto puede estar inclinada, recortada o tener sombras. Puede contener una o las dos secciones.
 
DATOS GENERALES (escritos a mano arriba, junto a "Nombre", "Grupo" y "Fecha"):
- Transcribe lo escrito tal cual, sin corregir. Si no se lee con seguridad, usa null.
 
OPCIONES (iguales en TODAS las preguntas):
a) No, para nada
b) Un poco
c) Sí, mucho
Solo existen a, b y c. NUNCA devuelvas "d".
 
MARCA: el alumno encierra con un óvalo (o subraya/rodea) la opción elegida.
Identifica VISUALMENTE cuál opción está marcada. No supongas la respuesta por el texto.
Si no hay una marca suficientemente clara, usa null.
 
DISTRIBUCIÓN: cada sección tiene dos columnas. Se lee primero la columna izquierda y luego la derecha.
- Inglés = 8 preguntas: izquierda 1 a 4, derecha 5 a 8.
- Programación (STEM/PROGRAMACIÓN) = 7 preguntas: izquierda 1 a 4, derecha 5 a 7.
 
REGLAS:
- Cada materia es independiente; la numeración se reinicia en cada sección.
- No combines secciones, no agregues ni elimines preguntas.
- Si una sección no aparece en la imagen, no la incluyas.
- El arreglo "Respuestas" debe tener exactamente 8 elementos para Inglés y 7 para Programación.
 
Devuelve únicamente el JSON con las claves: Nombre, Grupo, Fecha, Secciones
(cada sección: Materia y Respuestas).
"""
 
PROMPT_ENCUESTA_2 = """
Analiza esta imagen de una encuesta escolar infantil: ENCUESTA 2, PLÁTICA STEM.
 
Los niños marcan de muchas formas: círculo completo o irregular, subrayado, relleno, línea o tachón.
No exijas un círculo perfecto. Determina qué opción fue marcada VISUALMENTE; no elijas por ser la primera
ni porque parezca más lógica.
 
TEXTO LIBRE (transcribe lo escrito, SIN corregir ortografía ni normalizar; si no se lee, null):
- Nombre completo, Escuela, Grado y grupo (clave "Grupo"), Fecha si aparece.
- P5 (carrera): cualquier palabra o profesión.
 
PREGUNTA 1 (antes de la plática ¿tenías interés en áreas STEM?): a = Sí, b = No
PREGUNTA 2 (después de la plática ¿te interesa estudiar una de estas áreas?):
  a = Sí, b = No, c = No estoy segur@ todavía
PREGUNTA 3 (cuatro puntos independientes, claves P3a, P3b, P3c, P3d). La hoja dice
"Subraya o encierra una opción de cada punto": acepta SUBRAYADO o ENCERRADO (círculo/óvalo) de una opción.
Ignora manchas o líneas que no pertenezcan claramente a una opción. Sin marca clara: null.
  P3a: a = Divertida, b = Aburrida
  P3b: a = Provechosa, b = No provechosa
  P3c: a = Interesante, b = No interesante
  P3d: a = Clara, b = Confusa
PREGUNTA 4 (familiar con carrera STEM): a = Sí, b = No, c = No sé
PREGUNTA 5: texto libre.
 
No confundas marcas con letras impresas. No inventes respuestas.
 
Devuelve únicamente el JSON con EXACTAMENTE estas claves:
Nombre, Escuela, Grupo, Fecha, P1, P2, P3a, P3b, P3c, P3d, P4, P5.
"""
 
# =========================================================
# IMAGEN
# =========================================================
def optimizar_imagen(datos: bytes, mime: str) -> tuple:
    try:
        with Image.open(io.BytesIO(datos)) as original:
            img = ImageOps.exif_transpose(original).convert("RGB")
            escala = min(1.0, MAX_IMAGE_SIDE / max(img.size))
            if escala < 1.0:
                img = img.resize((max(1, round(img.width * escala)), max(1, round(img.height * escala))),
                                 Image.Resampling.LANCZOS)
            salida = io.BytesIO()
            img.save(salida, format="JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
            opt = salida.getvalue()
            return (opt, "image/jpeg") if len(opt) < len(datos) else (datos, mime)
    except Exception:
        return datos, mime
 
 
# =========================================================
# MOTORES: GEMINI y OLLAMA
# =========================================================
class CuotaAgotada(Exception):
    pass
 
 
def _mensaje_error(r: requests.Response) -> str:
    try:
        return r.json().get("error", {}).get("message", r.text)
    except Exception:
        return r.text
 
 
def llamar_gemini(prompt: str, img_b64: str, mime: str, esquema: dict, modelos: List[str]) -> str:
    if not API_KEY:
        raise RuntimeError("Falta GEMINI_API_KEY en Secrets.")
 
    cfg = {"responseMimeType": "application/json", "temperature": 0}
    cfg_esquema = dict(cfg, responseSchema=convertir_esquema_gemini(esquema))
    ultimo, ultimo_status = "sin detalle", None
 
    for modelo in modelos:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
        usar_esquema = True
 
        for intento in range(1, MAX_REINTENTOS + 1):
            payload = {
                "contents": [{"parts": [{"text": prompt},
                                        {"inline_data": {"mime_type": mime, "data": img_b64}}]}],
                "generationConfig": cfg_esquema if usar_esquema else cfg,
            }
            try:
                r = requests.post(url, headers={"Content-Type": "application/json",
                                                "x-goog-api-key": API_KEY},
                                  json=payload, timeout=120)
            except requests.exceptions.RequestException as exc:
                ultimo, ultimo_status = f"Conexión: {exc}", None
                if intento < MAX_REINTENTOS:
                    time.sleep(min(60, 5 * 2 ** (intento - 1)) + random.uniform(0, 1.5))
                    continue
                break
 
            ultimo_status = r.status_code
 
            if r.status_code == 200:
                try:
                    partes = r.json()["candidates"][0]["content"]["parts"]
                    texto = "\n".join(p["text"] for p in partes if isinstance(p.get("text"), str)).strip()
                except Exception:
                    texto = ""
                if texto:
                    return texto
                ultimo = "Respuesta vacía o bloqueada."
                break
 
            msg = _mensaje_error(r)
            ultimo = f"HTTP {r.status_code}: {msg[:300]}"
 
            if r.status_code == 400 and usar_esquema:
                usar_esquema = False  # el modelo no aceptó el esquema: reintenta sin él
                continue
 
            if r.status_code == 429:
                if "perday" in msg.lower().replace(" ", "").replace("_", ""):
                    break  # cuota diaria: reintentar no sirve
                m = re.search(r"retry in ([\d.]+)s", msg)
                espera = float(m.group(1)) + 1 if m else 20
                if intento < MAX_REINTENTOS and espera <= 70:
                    st.caption(f"⏳ Límite por minuto en {modelo}. Esperando {espera:.0f} s...")
                    time.sleep(espera)
                    continue
                break
 
            if r.status_code in {500, 502, 503, 504} and intento < MAX_REINTENTOS:
                espera = min(60, 5 * 2 ** (intento - 1)) + random.uniform(0, 1.5)
                st.caption(f"⏳ {modelo} ocupado (HTTP {r.status_code}). Reintento en {espera:.0f} s...")
                time.sleep(espera)
                continue
 
            break  # 401/403/404 u otros: pasar al siguiente modelo
 
        st.caption(f"↪️ {modelo} no respondió. Probando el siguiente modelo...")
 
    if ultimo_status == 429:
        raise CuotaAgotada(ultimo)
    raise RuntimeError(f"Gemini no pudo procesar la imagen. {ultimo}")
 
 
def llamar_ollama(prompt: str, img_b64: str, esquema: dict, modelo: str, host: str) -> str:
    try:
        r = requests.post(
            f"{host.rstrip('/')}/api/chat",
            json={"model": modelo, "stream": False, "format": esquema,
                  "options": {"temperature": 0},
                  "messages": [{"role": "user", "content": prompt, "images": [img_b64]}]},
            timeout=600,
        )
        r.raise_for_status()
        return r.json()["message"]["content"]
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"No se pudo conectar con Ollama en {host}. ¿Está corriendo (ollama serve)?")
    except Exception as exc:
        raise RuntimeError(f"Error con Ollama: {exc}")
 
 
def obtener_texto(prompt, img_b64, mime, esquema, cfg) -> str:
    if cfg["motor"] == "Ollama local":
        return llamar_ollama(prompt, img_b64, esquema, cfg["ollama_modelo"], cfg["ollama_host"])
    try:
        return llamar_gemini(prompt, img_b64, mime, esquema, cfg["modelos"])
    except (CuotaAgotada, RuntimeError) as exc:
        if cfg["motor"] == "Gemini → Ollama si falla":
            st.warning(f"⚠️ Gemini falló ({str(exc)[:150]}). Usando Ollama local...")
            return llamar_ollama(prompt, img_b64, esquema, cfg["ollama_modelo"], cfg["ollama_host"])
        raise
 
 
# =========================================================
# VALIDACIÓN
# =========================================================
def validar_encuesta_1(datos: Dict[str, Any]) -> List[Dict[str, Any]]:
    secciones = datos.get("Secciones")
    if not isinstance(secciones, list) or not secciones:
        raise ValueError("No se encontró ninguna sección válida.")
 
    base = {
        "Tipo Encuesta": T1,
        "Nombre": normalizar_nombre(limpiar_texto(datos.get("Nombre"))),
        "Grupo": normalizar_grupo(limpiar_texto(datos.get("Grupo"))),
        "Fecha": limpiar_texto(datos.get("Fecha")),
    }
    registros, vistas = [], set()
 
    for sec in secciones:
        materia = limpiar_materia(sec.get("Materia")) if isinstance(sec, dict) else None
        if materia is None or materia in vistas:
            continue
        vistas.add(materia)
 
        esperadas = PREGUNTAS_ESPERADAS[materia]
        crudas = sec.get("Respuestas") if isinstance(sec.get("Respuestas"), list) else []
        respuestas = [limpiar_inciso(x, {"a", "b", "c"}) for x in crudas]
        if len(respuestas) != esperadas:
            st.warning(f"⚠️ {materia}: el modelo devolvió {len(respuestas)} respuestas y se esperaban "
                       f"{esperadas}. Se ajustó; revisa esa fila antes de guardar.")
            respuestas = (respuestas + [None] * esperadas)[:esperadas]
 
        reg = dict(base, Materia=materia)
        reg.update({f"Pregunta {i}": r for i, r in enumerate(respuestas, start=1)})
        registros.append(reg)
 
    if not registros:
        raise ValueError("No se pudo identificar la materia de ninguna sección.")
    return registros
 
 
def validar_encuesta_2(datos: Dict[str, Any]) -> Dict[str, Any]:
    ab, abc = {"a", "b"}, {"a", "b", "c"}
    return {
        "Tipo Encuesta": T2,
        "Nombre": normalizar_nombre(limpiar_texto(datos.get("Nombre"))),
        "Escuela": limpiar_texto(datos.get("Escuela")),
        "Grado y grupo": normalizar_grupo(limpiar_texto(datos.get("Grupo"))),
        "Fecha": limpiar_texto(datos.get("Fecha")),
        "Pregunta 1": limpiar_inciso(datos.get("P1"), ab),
        "Pregunta 2": limpiar_inciso(datos.get("P2"), abc),
        "Pregunta 3a": limpiar_inciso(datos.get("P3a"), ab),
        "Pregunta 3b": limpiar_inciso(datos.get("P3b"), ab),
        "Pregunta 3c": limpiar_inciso(datos.get("P3c"), ab),
        "Pregunta 3d": limpiar_inciso(datos.get("P3d"), ab),
        "Pregunta 4": limpiar_inciso(datos.get("P4"), abc),
        "Pregunta 5": limpiar_texto(datos.get("P5")),
    }
 
 
def procesar_imagen(img: Any, plantilla_id: str, cfg: dict) -> List[Dict[str, Any]]:
    datos_img = img.getvalue()
    mime = getattr(img, "type", "image/jpeg") or "image/jpeg"
 
    if plantilla_id == "encuesta_ingles_programacion":
        prompt, esquema = PROMPT_ENCUESTA_1, esquema_encuesta_1()
    else:
        prompt, esquema = PROMPT_ENCUESTA_2, esquema_encuesta_2()
 
    clave_cache = (hashlib.sha256(datos_img).hexdigest(), plantilla_id)
    crudo = st.session_state["cache_gemini"].get(clave_cache)
 
    if crudo is None:
        opt, mime_opt = optimizar_imagen(datos_img, mime)
        crudo = obtener_texto(prompt, base64.b64encode(opt).decode("utf-8"), mime_opt, esquema, cfg)
        st.session_state["cache_gemini"][clave_cache] = crudo  # evita gastar cuota si la validación falla
 
    try:
        datos = extraer_json(crudo)
        if plantilla_id == "encuesta_ingles_programacion":
            return validar_encuesta_1(datos)
        return [validar_encuesta_2(datos)]
    except Exception:
        with st.expander("Ver respuesta cruda del modelo"):
            st.code(crudo, language="json")
        raise
 
 
# =========================================================
# EXCEL
# =========================================================
def excel_bytes(hojas: Dict[str, pd.DataFrame]) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        for nombre, df in hojas.items():
            df.to_excel(w, index=False, sheet_name=nombre[:31])
    return buf.getvalue()
 
 
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
 
# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("⚙️ Motor de lectura")
motor = st.sidebar.radio("Motor:", ["Gemini", "Gemini → Ollama si falla", "Ollama local"])
modelos_txt = st.sidebar.text_input("Modelos Gemini (en orden de prioridad):", MODELOS_GEMINI_DEFECTO)
ollama_modelo = st.sidebar.text_input("Modelo Ollama:", OLLAMA_MODELO_DEFECTO)
ollama_host = st.sidebar.text_input("Servidor Ollama:", OLLAMA_HOST_DEFECTO)
CFG = {
    "motor": motor,
    "modelos": [m.strip() for m in modelos_txt.split(",") if m.strip()],
    "ollama_modelo": ollama_modelo.strip(),
    "ollama_host": ollama_host.strip(),
}
if st.sidebar.button("🧹 Limpiar caché de respuestas"):
    st.session_state["cache_gemini"] = {}
    st.sidebar.success("Caché limpia.")
 
st.sidebar.title("🗄️ Gestión de Base de Datos")
try:
    with open(DB_NAME, "rb") as f:
        st.sidebar.download_button("📥 Descargar Base de Datos (.db)", data=f.read(),
                                   file_name="respuestas_encuestas.db", mime="application/x-sqlite3")
except FileNotFoundError:
    pass
 
st.sidebar.subheader("⚠️ Zona de reinicio")
confirmar = st.sidebar.checkbox("Confirmar borrar datos actuales")
if st.sidebar.button("🗑️ Borrar y Reiniciar BD", key="btn_borrar"):
    if confirmar:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("DROP TABLE IF EXISTS resultados")
            conn.execute("DROP TABLE IF EXISTS imagenes_procesadas")
            conn.commit()
        init_db()
        st.session_state["pendientes"], st.session_state["hashes_pend"] = [], set()
        st.sidebar.success("✅ Base de datos reiniciada.")
        st.rerun()
    else:
        st.sidebar.warning("Marca la casilla de confirmación primero.")
 
# =========================================================
# SELECCIÓN Y CARGA
# =========================================================
st.subheader("📋 Tipo de encuesta")
nombre_plantilla = st.selectbox("Selecciona qué tipo de encuesta vas a procesar:", list(PLANTILLAS))
plantilla = PLANTILLAS[nombre_plantilla]
st.info(f"**{nombre_plantilla}** — {plantilla['descripcion']}")
 
origen = st.radio("Origen de las imágenes:", ["Subir Archivos (Múltiples)", "Usar Cámara (Individual)"],
                  horizontal=True)
imagenes: list = []
if origen == "Usar Cámara (Individual)":
    foto = st.camera_input("📷 Toma una foto de la encuesta")
    if foto:
        imagenes = [foto]
else:
    imagenes = st.file_uploader("📁 Sube una o varias imágenes", type=["jpg", "jpeg", "png", "webp"],
                                accept_multiple_files=True) or []
 
# =========================================================
# PROCESAMIENTO
# =========================================================
if imagenes:
    st.info(f"📁 {len(imagenes)} archivo(s) seleccionado(s).")
 
    if st.button("🚀 Procesar todas las encuestas", type="primary"):
        barra = st.progress(0)
        ok = err = omitidas = 0
        ya = imagenes_ya_procesadas()
 
        for i, img in enumerate(imagenes):
            nombre = getattr(img, "name", f"imagen_{i + 1}.jpg")
            clave_img = f"{plantilla['id']}:{hashlib.sha256(img.getvalue()).hexdigest()}"
            st.write(f"### 📷 {nombre}")
 
            if clave_img in ya or clave_img in st.session_state["hashes_pend"]:
                st.info("↩️ Esta imagen ya fue procesada (o está pendiente de revisión). Se omite.")
                omitidas += 1
                barra.progress((i + 1) / len(imagenes))
                continue
 
            try:
                registros = procesar_imagen(img, plantilla["id"], CFG)
                st.session_state["pendientes"].extend(registros)
                st.session_state["hashes_pend"].add(clave_img)
                ok += 1
                st.success(f"✅ Leída: {len(registros)} registro(s) pendiente(s) de revisión.")
            except CuotaAgotada as exc:
                err += 1
                st.error("⏸️ Se agotó la cuota de Gemini. Detuve el lote; las demás imágenes quedaron "
                         "sin procesar. Intenta mañana, activa facturación o usa Ollama local.")
                st.caption(str(exc)[:300])
                break
            except Exception as exc:
                err += 1
                st.error(f"❌ Error procesando {nombre}: {exc}")
 
            barra.progress((i + 1) / len(imagenes))
            if i < len(imagenes) - 1:
                time.sleep(PAUSA_ENTRE_IMAGENES)
 
        st.divider()
        st.info(f"Terminado. Leídas: {ok} | Errores: {err} | Omitidas: {omitidas}. "
                "Revisa y guarda abajo.")
 
# =========================================================
# REVISIÓN ANTES DE GUARDAR
# =========================================================
if st.session_state["pendientes"]:
    st.divider()
    st.subheader("✏️ Revisa y corrige antes de guardar")
    st.caption("Puedes editar celdas, agregar o borrar filas. Nada se guarda hasta pulsar «Guardar».")
 
    df_p = pd.DataFrame(st.session_state["pendientes"])
    editados: Dict[str, pd.DataFrame] = {}
 
    for tipo, grupo in df_p.groupby("Tipo Encuesta", sort=False):
        st.markdown(f"**{tipo}**")
        grupo = grupo.drop(columns=["Tipo Encuesta"]).reset_index(drop=True)
        cfg_cols = {}
        for c in grupo.columns:
            if c.startswith("Pregunta") and not (tipo == T2 and c == "Pregunta 5"):
                cfg_cols[c] = st.column_config.SelectboxColumn(c, options=["a", "b", "c"])
        editados[tipo] = st.data_editor(grupo, column_config=cfg_cols, num_rows="dynamic",
                                        use_container_width=True, key=f"ed_{tipo}")
 
    c1, c2 = st.columns(2)
    if c1.button("💾 Guardar revisados", type="primary"):
        existentes = claves_existentes()
        guardados = duplicados = 0
        for tipo, ed in editados.items():
            ed = ed.astype(object).where(ed.notna(), None)
            for fila in ed.to_dict("records"):
                reg = {"Tipo Encuesta": tipo, **{k: v for k, v in fila.items() if v is not None}}
                k = clave_registro(reg)
                if k in existentes:
                    duplicados += 1
                    continue
                guardar_registro(reg)
                existentes.add(k)
                guardados += 1
        marcar_imagenes(st.session_state["hashes_pend"])
        st.session_state["pendientes"], st.session_state["hashes_pend"] = [], set()
        st.session_state["flash"] = f"✅ Guardados: {guardados}. Duplicados omitidos: {duplicados}."
        st.rerun()
 
    if c2.button("🗑️ Descartar pendientes"):
        st.session_state["pendientes"], st.session_state["hashes_pend"] = [], set()
        st.rerun()
 
if st.session_state.get("flash"):
    st.success(st.session_state.pop("flash"))
 
# =========================================================
# RESULTADOS
# =========================================================
st.divider()
st.subheader("📊 Resultados")
 
df_raw = leer_base_datos()
filas = []
for _, row in df_raw.iterrows():
    try:
        d = json.loads(row["datos_json"])
        if isinstance(d, dict):
            d["ID"], d["Fecha Registro"] = row["id"], row["fecha_registro"]
            filas.append(d)
    except Exception:
        continue
 
if not filas:
    st.info("📭 No hay registros en la base de datos actual.")
else:
    df = pd.DataFrame(filas)
    if "Tipo Encuesta" not in df.columns:
        df["Tipo Encuesta"] = None
    if "Materia" in df.columns:  # compatibilidad con registros antiguos
        df.loc[df["Tipo Encuesta"].isna() & df["Materia"].notna(), "Tipo Encuesta"] = T1
 
    panel_resumen(df)
 
    tipos = sorted(str(x) for x in df["Tipo Encuesta"].dropna().unique())
    filtro = st.selectbox("🔎 Mostrar:", ["Todas"] + tipos)
 
    def subtabla(tipo: str, cols: List[str]) -> pd.DataFrame:
        t = df[df["Tipo Encuesta"] == tipo]
        return t[[c for c in cols if c in t.columns]].copy()
 
    hojas = {}
    if filtro in ("Todas", T1) and T1 in tipos:
        hojas["Encuesta 1"] = subtabla(T1, COLS_E1)
    if filtro in ("Todas", T2) and T2 in tipos:
        hojas["Encuesta 2"] = subtabla(T2, COLS_E2)
 
    for nombre_hoja, tabla in hojas.items():
        st.markdown(f"### {nombre_hoja}")
        if nombre_hoja == "Encuesta 1":
            st.caption("Inglés tiene 8 preguntas y Programación 7; cada fila es una sección.")
        st.dataframe(tabla, use_container_width=True, hide_index=True)
        st.download_button(f"📄 CSV — {nombre_hoja}", tabla.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"{nombre_hoja.lower().replace(' ', '_')}.csv", mime="text/csv",
                           key=f"csv_{nombre_hoja}")
 
    if hojas:
        try:
            st.download_button("📊 Exportar a Excel", excel_bytes(hojas),
                               file_name="encuestas.xlsx", mime=XLSX_MIME, key="xlsx_all")
        except ModuleNotFoundError:
            st.warning("Falta instalar `openpyxl` para exportar a Excel (`pip install openpyxl`).")
 
    if T2 in hojas or filtro == T2:
        with st.expander("🔤 Equivalencia de incisos — Encuesta 2"):
            st.dataframe(pd.DataFrame([
                ["Pregunta 1", "a", "Sí"], ["Pregunta 1", "b", "No"],
                ["Pregunta 2", "a", "Sí"], ["Pregunta 2", "b", "No"],
                ["Pregunta 2", "c", "No estoy segur@ todavía"],
                ["Pregunta 3a", "a / b", "Divertida / Aburrida"],
                ["Pregunta 3b", "a / b", "Provechosa / No provechosa"],
                ["Pregunta 3c", "a / b", "Interesante / No interesante"],
                ["Pregunta 3d", "a / b", "Clara / Confusa"],
                ["Pregunta 4", "a / b / c", "Sí / No / No sé"],
                ["Pregunta 5", "—", "Respuesta abierta"],
            ], columns=["Pregunta", "Inciso", "Respuesta impresa"]), use_container_width=True, hide_index=True)
 