"""Diseño visual del Escáner Inteligente de Encuestas.
 
Uso en app.py:
    from estilos import aplicar_estilos, encabezado, panel_resumen
"""
import pandas as pd
import streamlit as st
 
COLOR_A, COLOR_B, COLOR_C = "#3B6CF6", "#12B886", "#FF922B"
COLORES = (COLOR_A, COLOR_B, COLOR_C)
 
COLS_GRUPO = {
    "Inglés": [f"Pregunta {i}" for i in range(1, 9)],
    "Programación": [f"Pregunta {i}" for i in range(1, 8)],
    "Plática STEM": ["Pregunta 1", "Pregunta 2", "Pregunta 3a", "Pregunta 3b",
                     "Pregunta 3c", "Pregunta 3d", "Pregunta 4"],
}
 
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
 
:root {
  --azul: #3B6CF6; --violeta: #6D4CFF; --tinta: #0F1B4D; --suave: #5B6B9A;
  --borde: #DCE5FA; --marino: #0B1646; --marino2: #14246B;
}
html, body, [class*="st-"], .stApp { font-family: 'Plus Jakarta Sans', sans-serif; }
/* Los íconos de Streamlit usan su propia fuente; sin esto se ven como texto ("upload") */
[data-testid="stIconMaterial"], [class*="material-symbols"], [class*="material-icons"] {
  font-family: 'Material Symbols Rounded' !important;
}
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
 
/* Campos de texto del sidebar: fondo oscuro y texto blanco */
[data-testid="stSidebar"] [data-testid="stTextInputRootElement"],
[data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-baseweb="base-input"],
[data-testid="stSidebar"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] [data-baseweb="base-input"] > div {
  background: rgba(255,255,255,.10) !important;
  border-color: rgba(255,255,255,.18) !important;
  border-radius: 10px;
}
[data-testid="stSidebar"] input {
  background: transparent !important;
  color: #fff !important;
  -webkit-text-fill-color: #fff !important;
  caret-color: #fff;
}
[data-testid="stSidebar"] [data-baseweb="input"] svg { fill: #E6ECFF; }
 
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stDownloadButton > button {
  background: rgba(255,255,255,.08); color: #fff; width: 100%;
  border: 1px solid rgba(255,255,255,.14); border-radius: 12px;
}
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] .stDownloadButton > button:hover {
  background: rgba(255,255,255,.16); border-color: rgba(255,255,255,.3);
}
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
  border-radius: 18px; background: linear-gradient(135deg, #E4ECFF, #F1EBFF); flex: none;
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
 
/* ---------- Radio como tarjetas ---------- */
.main div[role="radiogroup"] { gap: .8rem; }
.main div[role="radiogroup"] > label {
  background: #fff; border: 1.5px solid var(--borde); border-radius: 14px;
  padding: .8rem 1.1rem; transition: border-color .15s, box-shadow .15s;
}
.main div[role="radiogroup"] > label:has(input:checked) {
  border-color: var(--azul); box-shadow: 0 0 0 3px rgba(59,108,246,.15); background: #F5F8FF;
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
 
/* ---------- Resumen ---------- */
.metrica { display: flex; align-items: center; gap: .8rem; padding: .45rem 0; }
.metrica .chip { width: 2.4rem; height: 2.4rem; border-radius: 12px; display: grid; place-items: center; flex: none; }
.metrica .txt { color: var(--suave); font-size: .92rem; flex: 1; }
.metrica .num { font-size: 1.7rem; font-weight: 800; color: var(--tinta); }
 
/* ---------- Análisis por pregunta ---------- */
.graf-cab { display: flex; align-items: center; justify-content: space-between; margin-bottom: .4rem; }
.graf-cab h4 { margin: 0; padding: 0; font-size: 1.15rem; font-weight: 700; }
.leyenda { display: flex; gap: .9rem; font-size: .85rem; color: var(--suave); }
.leyenda .dot { display: inline-block; width: .6rem; height: .6rem; border-radius: 50%; margin-right: .3rem; }
.graf { display: grid; grid-template-columns: auto 1.4fr 1fr; gap: 1.2rem; height: 300px; margin-top: .5rem; }
.graf .eje { display: flex; flex-direction: column; justify-content: space-between;
  padding-bottom: 22px; font-size: .75rem; color: var(--suave); text-align: right; }
.graf .barras { display: flex; gap: 6px; border-left: 1px solid var(--borde); padding-left: 8px; }
.graf .col { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.graf .pila { flex: 1; display: flex; flex-direction: column-reverse; border-bottom: 1px solid var(--borde); }
.graf .seg { min-height: 0; }
.graf .et { height: 22px; text-align: center; font-size: .72rem; color: var(--suave); padding-top: 4px; white-space: nowrap; overflow: hidden; }
.graf .filas { overflow-y: auto; padding-right: 6px; }
.graf .fila { margin-bottom: .75rem; }
.graf .fila-t { display: flex; justify-content: space-between; font-size: .8rem; font-weight: 600; margin-bottom: .25rem; }
.graf .cnt { display: flex; gap: .5rem; font-weight: 700; }
.graf .barra { display: flex; height: 8px; border-radius: 99px; background: #E8EDF8; overflow: hidden; }
.graf .barra i { display: block; height: 100%; }
 
/* ---------- Móvil ---------- */
@media (max-width: 900px) {
  .graf { grid-template-columns: auto 1fr; height: auto; }
  .graf .barras { min-height: 200px; }
  .graf .filas { grid-column: 1 / -1; max-height: 220px; }
}
@media (max-width: 640px) {
  .hero { flex-wrap: wrap; } .estado { margin-left: 0; }
}
 
/* ===== Parches ===== */
/* 1. Íconos de Streamlit: que vuelvan a verse como íconos y no como texto */
span[data-testid="stIconMaterial"], .stApp [class*="material-symbols"] {
  font-family: "Material Symbols Rounded", "Material Symbols Outlined" !important;
  font-weight: normal !important; font-style: normal !important;
  font-feature-settings: "liga" !important; -webkit-font-feature-settings: "liga" !important;
  letter-spacing: normal !important; text-transform: none !important; white-space: nowrap !important;
}
 
/* 2. Campos del sidebar (incluida la contraseña): fondo claro y texto oscuro siempre visible */
section[data-testid="stSidebar"] [data-testid="stTextInputRootElement"],
section[data-testid="stSidebar"] [data-baseweb="input"],
section[data-testid="stSidebar"] [data-baseweb="base-input"] {
  background: #FFFFFF !important; border-radius: 10px !important;
  border: 1px solid #C9D6FA !important;
}
section[data-testid="stSidebar"] [data-testid="stTextInput"] input,
section[data-testid="stSidebar"] input[type="text"],
section[data-testid="stSidebar"] input[type="password"] {
  background: #FFFFFF !important; color: #0F1B4D !important;
  -webkit-text-fill-color: #0F1B4D !important; caret-color: #0F1B4D !important;
}
section[data-testid="stSidebar"] input::placeholder {
  color: #8A97BD !important; -webkit-text-fill-color: #8A97BD !important;
}
/* Botón del ojito (mostrar/ocultar contraseña) */
section[data-testid="stSidebar"] [data-baseweb="input"] button,
section[data-testid="stSidebar"] [data-baseweb="input"] button * {
  background: transparent !important; color: #5B6B9A !important; fill: #5B6B9A !important;
}
 
/* ===== Zona de carga: diseño final (ícono | textos | ilustración | botón) ===== */
[data-testid="stFileUploaderDropzone"] {
  display: flex !important; align-items: center !important; flex-wrap: nowrap;
  gap: 1.4rem !important; padding: 1.2rem 1.8rem !important;
  border: 1.5px solid #7CC4F8 !important; border-radius: 20px !important;
  background: linear-gradient(180deg, #FAFDFF, #EEF7FF) !important;
  box-shadow: 0 0 0 5px rgba(94,170,255,.10), 0 0 34px rgba(94,170,255,.40) !important;
}
 
/* 1. Ícono nube con flecha */
[data-testid="stFileUploaderDropzone"]::before {
  content: "" !important; order: 0 !important; flex: none;
  width: 4rem; height: 4rem; border-radius: 18px; display: block;
  background: #fff url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%233B6CF6' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'><path d='M7 18a4.5 4.5 0 0 1-.6-8.96A6 6 0 0 1 18 8.5a4.75 4.75 0 0 1-.5 9.5'/><path d='M12 20v-8M9 14.5l3-3 3 3'/></svg>") center / 2.4rem no-repeat !important;
  box-shadow: 0 8px 22px rgba(59,108,246,.18);
}
 
/* 2. Textos: uno debajo del otro */
[data-testid="stFileUploaderDropzoneInstructions"] {
  order: 1 !important; flex: 1 !important; display: block !important; min-width: 0;
}
[data-testid="stFileUploaderDropzoneInstructions"] > * { display: none !important; }
[data-testid="stFileUploaderDropzoneInstructions"]::before {
  content: "Arrastra tus imágenes aquí o haz clic para seleccionar";
  display: block !important; font-size: 1rem; font-weight: 600; color: #0F1B4D;
}
[data-testid="stFileUploaderDropzoneInstructions"]::after {
  content: "Formatos: JPG, PNG, WEBP  |  Máx. 200MB por archivo";
  display: block !important; font-size: .8rem; color: #5B6B9A; margin-top: .2rem;
}
 
/* 3. Ilustración de archivos */
[data-testid="stFileUploaderDropzone"]::after {
  content: ""; order: 2 !important; flex: none; width: 96px; height: 76px;
  background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 76'><g transform='rotate(-8 24 44)'><rect x='4' y='24' width='42' height='42' rx='6' fill='%234F86F7'/><text x='25' y='51' font-size='11' font-weight='700' fill='white' text-anchor='middle' font-family='Arial'>JPG</text></g><rect x='30' y='14' width='38' height='38' rx='6' fill='%23FF922B'/><text x='49' y='38' font-size='10' font-weight='700' fill='white' text-anchor='middle' font-family='Arial'>PNG</text><g transform='rotate(8 70 30)'><rect x='52' y='4' width='38' height='38' rx='6' fill='%2312B886'/><text x='71' y='28' font-size='9' font-weight='700' fill='white' text-anchor='middle' font-family='Arial'>WEBP</text></g></svg>") center / contain no-repeat;
}
 
/* 4. Botón a la derecha (se oculta su texto/ícono original y se pone el propio) */
[data-testid="stFileUploaderDropzone"] button[data-testid="stBaseButton-secondary"] {
  order: 3 !important; margin-left: 0 !important; flex: none; white-space: nowrap;
  padding: .65rem 1.6rem !important; border: none !important; border-radius: 12px !important;
  background: linear-gradient(135deg, #3B6CF6, #4F86F7) !important;
  box-shadow: 0 8px 20px rgba(59,108,246,.3);
}
[data-testid="stFileUploaderDropzone"] button[data-testid="stBaseButton-secondary"] * { display: none; }
[data-testid="stFileUploaderDropzone"] button[data-testid="stBaseButton-secondary"]::after {
  content: "Seleccionar Archivos"; color: #fff; font-weight: 600; font-size: .95rem;
}
 
/* El botón de quitar archivo (X) conserva su ícono */
[data-testid="stFileUploaderDeleteBtn"] button,
[data-testid="stFileUploaderDropzone"] button[data-testid="stBaseButton-minimal"] {
  margin-left: 0 !important; background: transparent !important; box-shadow: none !important;
  padding: .25rem !important;
}
[data-testid="stFileUploaderDeleteBtn"] button *,
[data-testid="stFileUploaderDropzone"] button[data-testid="stBaseButton-minimal"] * { display: revert !important; }
[data-testid="stFileUploaderDeleteBtn"] button::after,
[data-testid="stFileUploaderDropzone"] button[data-testid="stBaseButton-minimal"]::after { content: none !important; }
 
/* Con archivos ya cargados, se oculta la ilustración para dar espacio */
[data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"]) [data-testid="stFileUploaderDropzone"]::after {
  display: none;
}
 
/* Móvil */
@media (max-width: 900px) {
  [data-testid="stFileUploaderDropzone"] { flex-wrap: wrap; }
  [data-testid="stFileUploaderDropzone"]::after { display: none; }
}
</style>
"""
 
 
def aplicar_estilos() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
 
 
def encabezado() -> None:
    st.markdown(
        '<div class="hero"><div class="icono">📷</div><div>'
        '<h1>Escáner Inteligente de Encuestas</h1>'
        '<p>Convierte encuestas escritas a mano en una base de datos.</p>'
        '</div><span class="estado">● Sistema listo</span></div>',
        unsafe_allow_html=True,
    )
 
 
def _metrica(icono: str, fondo: str, texto: str, valor: int) -> str:
    return (f'<div class="metrica"><div class="chip" style="background:{fondo}">{icono}</div>'
            f'<div class="txt">{texto}</div><div class="num">{valor}</div></div>')
 
 
def _grupos(df: pd.DataFrame) -> dict:
    """Separa los registros por sección (Inglés, Programación, Plática STEM)."""
    mat = df["Materia"] if "Materia" in df.columns else pd.Series([None] * len(df), index=df.index)
    grupos = {}
    for nombre in ("Inglés", "Programación"):
        sub = df[mat == nombre]
        if len(sub):
            grupos[nombre] = sub.reindex(columns=COLS_GRUPO[nombre])
    sub = df[mat.isna()]
    if len(sub):
        grupos["Plática STEM"] = sub.reindex(columns=COLS_GRUPO["Plática STEM"])
    return grupos
 
 
def _grafica_html(nombre: str, sub: pd.DataFrame) -> str:
    n = len(sub)
    datos = {}
    for c in sub.columns:
        s = sub[c]
        datos[c] = ([int((s == o).sum()) for o in "abc"], int(s.notna().sum()))
    top = max(1, max(t for _, t in datos.values()))
    mid = round(top / 2)
 
    barras, filas = "", ""
    for c, (cnt, tot) in datos.items():
        r = c.replace("Pregunta ", "Q")
        segs = "".join(f'<div class="seg" style="flex:{k} 0 0%;background:{col}"></div>'
                       for k, col in zip(cnt, COLORES))
        barras += (f'<div class="col"><div class="pila">{segs}'
                   f'<div style="flex:{top - tot} 0 0%"></div></div><div class="et">{r}</div></div>')
        anchos = "".join(f'<i style="width:{k / n * 100:.1f}%;background:{col}"></i>'
                         for k, col in zip(cnt, COLORES))
        nums = "".join(f'<span style="color:{col}">{o} {k}</span>'
                       for o, k, col in zip("abc", cnt, COLORES))
        filas += (f'<div class="fila"><div class="fila-t"><span>{r}</span>'
                  f'<span class="cnt">{nums}</span></div><div class="barra">{anchos}</div></div>')
 
    return (f'<div class="graf"><div class="eje"><span>{top}</span><span>{mid}</span><span>0</span></div>'
            f'<div class="barras">{barras}</div><div class="filas">{filas}</div></div>')
 
 
def panel_resumen(df: pd.DataFrame) -> None:
    """Tres tarjetas: resumen, análisis por pregunta y últimos registros."""
    grupos = _grupos(df)
    total = sum(int(g.notna().sum().sum()) for g in grupos.values())
    vacias = sum(int(g.isna().sum().sum()) for g in grupos.values())
 
    c1, c2 = st.columns([1, 2.6])
 
    with c1.container(border=True):
        st.markdown("#### Resumen")
        st.markdown(
            _metrica("📝", "#E4ECFF", "Registros guardados", len(df))
            + _metrica("💬", "#E0F7EE", "Preguntas respondidas", total)
            + _metrica("⚠️", "#FFE8EC", "Respuestas sin marca", vacias),
            unsafe_allow_html=True,
        )
 
    with c2.container(border=True):
        leyenda = "".join(f'<span><span class="dot" style="background:{col}"></span>{o}</span>'
                          for o, col in zip("abc", COLORES))
        st.markdown(f'<div class="graf-cab"><h4>Análisis por pregunta</h4>'
                    f'<div class="leyenda">{leyenda}</div></div>', unsafe_allow_html=True)
        if not grupos:
            st.caption("Aún no hay respuestas para graficar.")
        else:
            nombre = (st.selectbox("Sección", list(grupos), key="grupo_grafica",
                                   label_visibility="collapsed")
                      if len(grupos) > 1 else next(iter(grupos)))
            if len(grupos) == 1:
                st.caption(nombre)
            st.markdown(_grafica_html(nombre, grupos[nombre]), unsafe_allow_html=True)
 