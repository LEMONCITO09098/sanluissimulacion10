"""
Estilo compartido: tema oscuro minimalista (inspirado en el ejemplo
"Uber Pickups in NYC" de Streamlit) para usarse en ambos dashboards.
"""

import streamlit as st

ACCENT = "#2FE0A8"     # verde menta, acento principal (como el mapa de Uber)
BG = "#0B0B0C"          # negro casi puro
BG_CARD = "#161618"     # gris muy oscuro para tarjetas/sidebar
TEXT = "#F2F2F0"
MUTED = "#9A9A9E"


def aplicar_tema():
    st.markdown(
        f"""
        <style>
        /* Fondo general */
        .stApp {{
            background-color: {BG};
        }}

        /* Título estilo "Uber Pickups in NYC": serif, elegante, sin negritas duras */
        h1 {{
            font-family: Georgia, 'Times New Roman', serif !important;
            font-weight: 400 !important;
            letter-spacing: 0.5px;
            color: {TEXT} !important;
        }}
        h2, h3 {{
            font-family: -apple-system, "Segoe UI", sans-serif !important;
            font-weight: 500 !important;
            color: {TEXT} !important;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: {BG_CARD};
            border-right: 1px solid #232326;
        }}

        /* Tarjetas de métricas (KPIs) */
        div[data-testid="stMetric"] {{
            background-color: {BG_CARD};
            border: 1px solid #232326;
            border-radius: 10px;
            padding: 14px 16px;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {MUTED} !important;
        }}
        div[data-testid="stMetricValue"] {{
            color: {ACCENT} !important;
        }}

        /* Quitar el padding superior excesivo */
        .block-container {{
            padding-top: 2.2rem;
        }}

        /* Inputs / selects */
        .stMultiSelect [data-baseweb="tag"] {{
            background-color: {ACCENT} !important;
            color: #06110D !important;
        }}

        /* Ocultar el footer "Made with Streamlit" para un look más limpio */
        footer {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def tema_plotly(fig, altura=None):
    """Aplica fondo transparente + tipografía consistente a una figura de Plotly."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, family="-apple-system, Segoe UI, sans-serif"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    if altura:
        fig.update_layout(height=altura)
    return fig
