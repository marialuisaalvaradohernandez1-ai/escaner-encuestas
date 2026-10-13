"""Diseño visual del Escáner Inteligente de Encuestas.
 
Uso en app.py:
    from estilos import aplicar_estilos, encabezado, panel_resumen
"""
import pandas as pd
import streamlit as st
 
COLOR_A, COLOR_B, COLOR_C = "#3B6CF6", "#12B886", "#FF922B"
OPCIONES = ("a", "b", "c")
COLORES = {"a": COLOR_A, "b": COLOR_B, "c": COLOR_C}
ESPERADAS = {"Inglés": 8, "Programación": 7}
ABREV = {"Inglés": "In", "Programación": "Pr"}
COLS_T2 = ["Pregunta 1", "Pregunta 2", "Pregunta 3a", "Pregunta 3b",
           "Pregunta 3c", "Pregunta 3d", "Pregunta 4"]
 
ICONO_NUBE = (
    "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64' "
    "fill='none' stroke='%233B6CF6' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'>"
    "<path d='M18 42a10 10 0 0 1-1-19.9A15 15 0 0 1 46 20a11 11 0 0 1 2 22'/>"
    "<path d='M32 52V30M24 37l8-8 8 8'/></svg>\")"
)
 
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
 
:root {
  --azul: #3B6CF6; --violeta: #6D4CFF; --tinta: #0F1B4D; --suave: #5B6B9A;
  --fondo: #F2F6FF; --borde: #DCE5FA; --marino: #0B1646; --marino2: #14246B;
}
html, body, [class*="st-"], .stApp { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: linear-gradient(160deg, #F7FAFF 0%, #EAF0FF 100%); color: var(--tinta); }
.block-container { padding-top: 2rem; max-width: 1200px; }
h1, h2, h3 { color: var(--tinta); letter-spacing: -0.01em; font-weight: 700; }
 
/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--marino) 0%, var(--marino2) 100%);
  border-right: none;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] span, [data-testid="stSidebar"] div { color: #E6ECFF; }
 
/* Campos de texto: el contenedor de BaseWeb pintaba fondo blanco y el texto claro no se veía */
[data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-baseweb="base-input"] {
  background: rgba(255,255,255,.08) !important;
  border: 1px solid rgba(255,255,255,.14) !important; border-radius: 10px !important;
}
[data-testid="stSidebar"] input {
  background: transparent !important; color: #fff !important;
  -webkit-text-fill-color: #fff !important; caret-color: #fff;
}
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stDownloadButton > button {
  background: rgba(255,255,255,.08); color: #fff; width: 100%;
  border: 1px solid rgba(255,255,255,.14); border-radius: 12px;
}
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] .stDownloadButton > button:hover {
  background: rgba(255,255,255,.16); border-color: rgba(255,255,255,.3);
}
/* Botón de borrado (usa key="btn_borrar") */
[data-testid="stSidebar"] .st-key-btn_borrar button {
  background: transparent; color: #FF8FA3; border: 1px solid #FF5C7A;
}
[data-testid="stSidebar"] .st-key-btn_borrar button:hover { background: rgba(255,92,122,.15); }
 
/* ---------- Encabezado ---------- */
.hero {
  display: flex; align-items: center; gap: 1.2rem; background: #fff;
  border: 1px solid var(--borde); border-radius: 22px; padding: 1.4rem 1.6rem;
  box-shadow: 0 10px 30px rgba(59,108,246,.08); margin-bottom: 1.2rem;
}
.hero .icono {
  font-size: 2.2rem; width: 4rem; height: 4rem; display: grid; place-items: center;
  border-radius: 18px; background: linear-gradient(135deg, #E4ECFF, #F1EBFF);
}
.hero h1 { margin: 0; font-size: 1.9rem; font-weight: 800; padding: 0; }
.hero p { margin: .2rem 0 0; color: var(--suave); }
.estado {
  margin-left: auto; font-size: .8rem; font-weight: 600; color: #0B7A5A;
  background: #E6FAF2; border-radius: 999px; padding: .3rem .8rem; white-space: nowrap;
}
 
/* ---------- Tarjetas (st.container(border=True)) ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: #fff; border: 1px solid var(--borde) !important; border-radius: 20px;
  box-shadow: 0 10px 30px rgba(59,108,246,.06);
}
 
/* ---------- Radio horizontal como tarjetas ---------- */
div[role="radiogroup"][aria-orientation="horizontal"],
.main div[role="radiogroup"] { gap: .8rem; }
.main div[role="radiogroup"] > label {
  background: #fff; border: 1.5px solid var(--borde); border-radius: 14px;
  padding: .8rem 1.1rem; transition: border-color .15s, box-shadow .15s;
}
.main div[role="radiogroup"] > label:has(input:checked) {
  border-color: var(--azul); box-shadow: 0 0 0 3px rgba(59,108,246,.15);
  background: #F5F8FF;
}
 
/* ---------- Zona de carga (estilo con brillo) ---------- */
[data-testid="stFileUploaderDropzone"] {
  display: flex; align-items: center; gap: 1.2rem; padding: 1.3rem 1.6rem;
  border: 1.5px solid #8CC5FF; border-radius: 20px;
  background: linear-gradient(135deg, #F8FBFF 0%, #EAF4FF 100%);
  box-shadow: 0 0 0 4px rgba(56,160,255,.10), 0 0 30px rgba(45,190,240,.30);
  transition: box-shadow .2s, border-color .2s;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: #4DA3FF;
  box-shadow: 0 0 0 5px rgba(56,160,255,.16), 0 0 38px rgba(45,190,240,.45);
}
/* Oculta el icono y textos originales (en inglés) y los reemplaza */
[data-testid="stFileUploaderDropzone"] svg { display: none; }
[data-testid="stFileUploaderDropzone"]::before {
  content: ""; flex: 0 0 4rem; height: 4rem; border-radius: 18px;
  background: #fff var(--nube) center / 60% no-repeat;
  box-shadow: 0 6px 16px rgba(59,108,246,.15);
}
[data-testid="stFileUploaderDropzoneInstructions"] > div > *,
[data-testid="stFileUploaderDropzoneInstructions"] > span,
[data-testid="stFileUploaderDropzoneInstructions"] > small { display: none; }
[data-testid="stFileUploaderDropzoneInstructions"] > div { display: flex; flex-direction: column; gap: .15rem; }
[data-testid="stFileUploaderDropzoneInstructions"] > div::before {
  content: "Arrastra tus imágenes aquí o haz clic para seleccionar";
  font-size: 1rem; font-weight: 700; color: var(--tinta);
}
[data-testid="stFileUploaderDropzoneInstructions"] > div::after {
  content: "Formatos: JPG, PNG, WEBP  |  Máx. 200MB por archivo";
  font-size: .8rem; color: var(--suave);
}
[data-testid="stFileUploaderDropzone"] button {
  margin-left: auto; font-size: 0; border: none; border-radius: 12px; padding: .65rem 1.3rem;
  background: linear-gradient(135deg, var(--azul), #4C86FF); color: #fff;
  box-shadow: 0 8px 18px rgba(59,108,246,.30);
}
[data-testid="stFileUploaderDropzone"] button > * { display: none; }
[data-testid="stFileUploaderDropzone"] button::after {
  content: "Seleccionar Archivos"; font-size: .9rem; font-weight: 600; color: #fff;
}
 
/* ---------- Botones principales ---------- */
.main button[kind="primary"] {
  background: linear-gradient(135deg, var(--azul), var(--violeta)); border: none;
  border-radius: 12px; font-weight: 700; color: #fff;
  box-shadow: 0 8px 20px rgba(59,108,246,.3);
}
.main .stDownloadButton > button, .main .stButton > button:not([kind="primary"]) {
  border-radius: 12px; border: 1px solid var(--borde); font-weight: 600;
}
 
/* ---------- Métricas del resumen ---------- */
.metrica { display: flex; align-items: center; gap: .8rem; padding: .45rem 0; }
.metrica .chip { width: 2.4rem; height: 2.4rem; border-radius: 12px; display: grid; place-items: center; }
.metrica .txt { color: var(--suave); font-size: .92rem; flex: 1; }
.metrica .num { font-size: 1.7rem; font-weight: 800; color: var(--tinta); }
 
/* ---------- Análisis por pregunta ---------- */
.an-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: .9rem; }
.an-head h4 { margin: 0; font-size: 1.15rem; font-weight: 700; color: var(--tinta); }
.leyenda { display: flex; gap: 1rem; font-size: .85rem; font-weight: 600; color: var(--suave); }
.leyenda i, .hops i { display: inline-block; width: .6rem; height: .6rem; border-radius: 50%; margin-right: .3rem; }
.an-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.8rem; align-items: start; }
 
.vwrap { display: grid; grid-template-columns: 2rem 1fr; column-gap: .5rem; }
.vy { display: flex; flex-direction: column; justify-content: space-between; height: 190px;
      font-size: .75rem; color: var(--suave); text-align: right; }
.vplot { height: 190px; display: flex; gap: .4rem; align-items: flex-end; padding: 0 .3rem;
         border-bottom: 1px solid var(--borde);
         background-image: linear-gradient(to top, #EDF1FB 1px, transparent 1px);
         background-size: 100% 50%; }
.vcol { flex: 1; height: 100%; display: flex; align-items: flex-end; justify-content: center; }
.vstack { width: 78%; max-width: 34px; display: flex; flex-direction: column-reverse;
          border-radius: 6px 6px 0 0; overflow: hidden; }
.vstack .seg { min-height: 2px; }
.vlabels { grid-column: 2; display: flex; gap: .4rem; padding: .3rem .3rem 0; }
.vlabels span { flex: 1; text-align: center; font-size: .68rem; color: var(--suave); }
 
.hlista { display: flex; flex-direction: column; gap: .85rem; }
.hcab { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: .3rem; }
.hnom { font-size: .88rem; font-weight: 600; color: var(--tinta); }
.hops { font-size: .78rem; color: var(--suave); white-space: nowrap; }
.hops b { color: var(--tinta); margin-right: .55rem; font-weight: 700; }
.hbar { display: flex; height: 9px; border-radius: 999px; overflow: hidden; background: #E6EBF5; }
 
/* ---------- Móvil ---------- */
@media (max-width: 640px) {
  .hero { flex-wrap: wrap; } .estado { margin-left: 0; }
  .an-grid { grid-template-columns: 1fr; }
  [data-testid="stFileUploaderDropzone"] { flex-wrap: wrap; }
}
</style>
"""
 
 
def aplicar_estilos() -> None:
    st.markdown(CSS.replace("var(--nube)", ICONO_NUBE), unsafe_allow_html=True)
 
 
def encabezado() -> None:
    st.markdown(
        """
        <div class="hero">
          <div class="icono">📷</div>
          <div>
            <h1>Escáner Inteligente de Encuestas</h1>
            <p>Convierte encuestas escritas a mano en una base de datos ordenada.</p>
          </div>
          <span class="estado">● Sistema listo</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
 
 
def _metrica(icono: str, fondo: str, texto: str, valor: int) -> str:
    return (f'<div class="metrica"><div class="chip" style="background:{fondo}">{icono}</div>'
            f'<div class="txt">{texto}</div><div class="num">{valor}</div></div>')
 
 
def _cols_pregunta(df: pd.DataFrame) -> list:
    """Columnas de opción múltiple (excluye la Pregunta 5 de texto libre)."""
    return [c for c in df.columns if c.startswith("Pregunta") and c != "Pregunta 5"]
 
 
# ---------------------------------------------------------
# Análisis por pregunta
# ---------------------------------------------------------
def _filas_analisis(df: pd.DataFrame) -> list:
    """Devuelve [(etiqueta, etiqueta_corta, {a,b,c: conteo}, total_registros)]."""
    filas = []
    if "Materia" in df.columns and df["Materia"].notna().any():
        for materia, n in ESPERADAS.items():
            sub = df[df["Materia"] == materia]
            if sub.empty:
                continue
            for i in range(1, n + 1):
                col = f"Pregunta {i}"
                if col in sub.columns:
                    filas.append((f"P{i} · {materia}", f"{ABREV[materia]}{i}", sub[col], len(sub)))
    else:
        for col in COLS_T2:
            if col in df.columns:
                corta = col.replace("Pregunta ", "P")
                filas.append((corta, corta, df[col], len(df)))
    return [(e, c, {op: int((s == op).sum()) for op in OPCIONES}, n) for e, c, s, n in filas]
 
 
def _html_vertical(filas: list) -> str:
    maximo = max((sum(c.values()) for _, _, c, _ in filas), default=0) or 1
    cols, etiquetas = "", ""
    for etiqueta, corta, conteo, _ in filas:
        alto = sum(conteo.values()) / maximo * 100
        segs = "".join(f'<div class="seg" style="flex:{conteo[o]};background:{COLORES[o]}"></div>'
                       for o in OPCIONES if conteo[o])
        cols += f'<div class="vcol" title="{etiqueta}"><div class="vstack" style="height:{alto:.1f}%">{segs}</div></div>'
        etiquetas += f"<span>{corta}</span>"
    eje = f"<span>{maximo:g}</span><span>{maximo / 2:g}</span><span>0</span>"
    return (f'<div class="vwrap"><div class="vy">{eje}</div><div class="vplot">{cols}</div>'
            f'<div class="vlabels">{etiquetas}</div></div>')
 
 
def _html_horizontal(filas: list) -> str:
    items = ""
    for etiqueta, _, conteo, n in filas:
        n = max(n, 1)
        segs = "".join(f'<div style="width:{conteo[o] / n * 100:.1f}%;background:{COLORES[o]}"></div>'
                       for o in OPCIONES if conteo[o])
        ops = "".join(f'<i style="background:{COLORES[o]}"></i><b>{o} {conteo[o]}</b>' for o in OPCIONES)
        items += (f'<div class="hfila"><div class="hcab"><span class="hnom">{etiqueta}</span>'
                  f'<span class="hops">{ops}</span></div><div class="hbar">{segs}</div></div>')
    return f'<div class="hlista">{items}</div>'
 
 
def _tarjeta_analisis(df: pd.DataFrame) -> None:
    with st.container(border=True):
        tipos = sorted(str(x) for x in df["Tipo Encuesta"].dropna().unique()) if "Tipo Encuesta" in df else []
        base = df
        if len(tipos) > 1:
            elegido = st.radio("Encuesta", tipos, horizontal=True, label_visibility="collapsed",
                               key="analisis_tipo")
            base = df[df["Tipo Encuesta"] == elegido]
        elif len(tipos) == 1:
            base = df[df["Tipo Encuesta"] == tipos[0]]
 
        leyenda = "".join(f'<span><i style="background:{COLORES[o]}"></i>{o}</span>' for o in OPCIONES)
        st.markdown(f'<div class="an-head"><h4>Análisis por pregunta</h4>'
                    f'<div class="leyenda">{leyenda}</div></div>', unsafe_allow_html=True)
 
        filas = _filas_analisis(base)
        if not filas:
            st.caption("Aún no hay respuestas para graficar.")
            return
        st.markdown(f'<div class="an-grid">{_html_vertical(filas)}{_html_horizontal(filas)}</div>',
                    unsafe_allow_html=True)
        st.caption("La barra gris indica respuestas sin marca. Cada barra es el 100 % de los registros de esa materia.")
 
 
def panel_resumen(df: pd.DataFrame) -> None:
    """Resumen + últimos registros arriba, análisis por pregunta a todo el ancho."""
    cols = _cols_pregunta(df)
    respuestas = df[cols] if cols else pd.DataFrame()
    total = int(respuestas.notna().sum().sum()) if cols else 0
    vacias = int(respuestas.isna().sum().sum()) if cols else 0
 
    c1, c2 = st.columns([1, 1.4])
 
    with c1.container(border=True):
        st.markdown("#### Resumen")
        st.markdown(
            _metrica("📝", "#E4ECFF", "Registros guardados", len(df))
            + _metrica("💬", "#E0F7EE", "Preguntas respondidas", total)
            + _metrica("⚠️", "#FFE8EC", "Respuestas sin marca", vacias),
            unsafe_allow_html=True,
        )
 
    with c2.container(border=True):
        st.markdown("#### Últimos registros")
        vista = pd.DataFrame({"Nombre": df.get("Nombre")})
        vista["Materia"] = df["Materia"].fillna("—") if "Materia" in df else "—"
        grupo = df["Grupo"] if "Grupo" in df else pd.Series([None] * len(df), index=df.index)
        if "Grado y grupo" in df:
            grupo = grupo.fillna(df["Grado y grupo"])
        vista["Grupo"] = grupo.fillna("—")
        st.dataframe(vista.head(4), hide_index=True, use_container_width=True)
        st.caption("La tabla completa está más abajo.")
 
    _tarjeta_analisis(df)
def panel_resumen(df: pd.DataFrame) -> None:
    ...
    _tarjeta_analisis(df)


filas_analisis = _filas_analisis