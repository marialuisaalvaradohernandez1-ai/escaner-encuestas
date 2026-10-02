"""Diseño visual del Escáner Inteligente de Encuestas.

Uso en app.py:
    from estilos import aplicar_estilos, encabezado, panel_resumen
"""
import pandas as pd
import streamlit as st

COLOR_A, COLOR_B, COLOR_C = "#3B6CF6", "#12B886", "#FF922B"

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
[data-testid="stSidebar"] input {
  background: rgba(255,255,255,.08) !important; color: #fff !important;
  border: 1px solid rgba(255,255,255,.12) !important; border-radius: 10px;
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

/* ---------- Zona de carga ---------- */
[data-testid="stFileUploaderDropzone"] {
  border: 2px dashed #9DB4FF; border-radius: 18px; background: #F5F8FF; padding: 1.6rem;
}
[data-testid="stFileUploaderDropzone"] button {
  background: linear-gradient(135deg, var(--azul), var(--violeta)); color: #fff;
  border: none; border-radius: 12px; font-weight: 600;
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

/* ---------- Móvil ---------- */
@media (max-width: 640px) {
  .hero { flex-wrap: wrap; } .estado { margin-left: 0; }
}
</style>
"""


def aplicar_estilos() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


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


def panel_resumen(df: pd.DataFrame) -> None:
    """Tres tarjetas: resumen, análisis por pregunta y vista previa de la base."""
    cols = _cols_pregunta(df)
    respuestas = df[cols] if cols else pd.DataFrame()
    total = int(respuestas.notna().sum().sum()) if cols else 0
    vacias = int(respuestas.isna().sum().sum()) if cols else 0

    c1, c2, c3 = st.columns([1, 1.5, 1.2])

    with c1.container(border=True):
        st.markdown("#### Resumen")
        st.markdown(
            _metrica("📝", "#E4ECFF", "Registros guardados", len(df))
            + _metrica("💬", "#E0F7EE", "Preguntas respondidas", total)
            + _metrica("⚠️", "#FFE8EC", "Respuestas sin marca", vacias),
            unsafe_allow_html=True,
        )

    with c2.container(border=True):
        st.markdown("#### Análisis por pregunta")
        base = df[df.get("Tipo Encuesta") == df["Tipo Encuesta"].dropna().iloc[0]] \
            if "Tipo Encuesta" in df and df["Tipo Encuesta"].notna().any() else df
        pcols = _cols_pregunta(base)
        if pcols:
            conteo = pd.DataFrame(
                {op: [int((base[c] == op).sum()) for c in pcols] for op in ("a", "b", "c")},
                index=[c.replace("Pregunta ", "P") for c in pcols],
            )
            st.bar_chart(conteo, color=[COLOR_A, COLOR_B, COLOR_C], stack=True, height=220)
            st.caption("Azul = a · Verde = b · Naranja = c")
        else:
            st.caption("Aún no hay respuestas para graficar.")

    with c3.container(border=True):
        st.markdown("#### Últimos registros")
        vista = [c for c in ("Nombre", "Materia", "Grupo", "Grado y grupo") if c in df.columns][:3]
        if vista:
            st.dataframe(df[vista].head(4), hide_index=True, use_container_width=True)
        st.caption("La tabla completa está más abajo.")