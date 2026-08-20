"""
Dashboard de Actividad Económica por Código Postal - San Luis Potosí
----------------------------------------------------------------------
Ejecutar con:  streamlit run app_slp.py

IMPORTANTE: el dataset incluido (denue_slp_demo.csv) es SIMULADO,
generado a partir del tamaño de cada polígono de código postal, para
que puedas ver el dashboard funcionando de inmediato. Más abajo en este
archivo (sección "DATOS REALES DE DENUE") están las instrucciones para
conectar el directorio real de negocios de INEGI.
"""

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import ACCENT, aplicar_tema, tema_plotly

st.set_page_config(
    page_title="SLP · Actividad Económica",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)
aplicar_tema()


# ----------------------------------------------------------------------
# Carga de datos
# ----------------------------------------------------------------------
@st.cache_data
def cargar_geojson():
    with open("slp_cp.geojson", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def cargar_datos():
    df = pd.read_csv("denue_slp_demo.csv", dtype={"cp": str})
    return df


geojson = cargar_geojson()
df = cargar_datos()

# ----------------------------------------------------------------------
# Aviso de datos de ejemplo
# ----------------------------------------------------------------------
st.warning(
    "⚠️ **Estos son datos simulados**, generados a partir del tamaño de cada "
    "polígono (zonas más pequeñas = más urbanas = más negocios estimados). "
    "No son cifras reales del DENUE. Ve al final de `app_slp.py` para "
    "instrucciones de cómo conectar los datos reales de INEGI."
)

# ----------------------------------------------------------------------
# Sidebar - filtros
# ----------------------------------------------------------------------
st.sidebar.title("Filtros")

sectores = sorted(df["sector_principal"].unique())
sector_sel = st.sidebar.multiselect("Sector", options=sectores, default=sectores)

rango_negocios = st.sidebar.slider(
    "Rango de negocios estimados por zona",
    int(df["negocios_estimados"].min()),
    int(df["negocios_estimados"].max()),
    (int(df["negocios_estimados"].min()), int(df["negocios_estimados"].max())),
)

busqueda_cp = st.sidebar.text_input("Buscar código postal")

df_f = df[
    df["sector_principal"].isin(sector_sel)
    & df["negocios_estimados"].between(*rango_negocios)
]
if busqueda_cp:
    df_f = df_f[df_f["cp"].str.contains(busqueda_cp)]

st.sidebar.markdown("---")
st.sidebar.caption(
    "Base geográfica: polígonos de código postal de San Luis Potosí (INEGI)."
)

# ----------------------------------------------------------------------
# Encabezado y KPIs
# ----------------------------------------------------------------------
st.title("🏙️ Actividad Económica por Código Postal · San Luis Potosí")
st.caption("Explora negocios estimados por zona (código postal)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Negocios estimados (total filtrado)", f"{df_f['negocios_estimados'].sum():,.0f}")
col2.metric("Zonas (CP) mostradas", len(df_f))
col3.metric(
    "CP con más negocios",
    df_f.loc[df_f["negocios_estimados"].idxmax(), "cp"] if not df_f.empty else "-",
)
col4.metric(
    "Densidad promedio (negocios/km²)",
    f"{df_f['densidad_negocios_km2'].mean():,.1f}" if not df_f.empty else "-",
)

st.markdown("---")

# ----------------------------------------------------------------------
# Mapa
# ----------------------------------------------------------------------
st.subheader("Mapa por código postal")

metrica = st.radio(
    "Colorear mapa por:",
    ["negocios_estimados", "densidad_negocios_km2"],
    horizontal=True,
    format_func=lambda x: "Negocios estimados" if x == "negocios_estimados" else "Densidad (negocios/km²)",
)

# Unas pocas zonas muy pequeñas tienen densidades extremas que, con una
# escala lineal normal, "aplastan" el color de todo el resto del mapa
# (todo se ve del mismo tono). Usamos el percentil 95 como techo de la
# escala de color -- los valores más altos que eso se pintan igual que
# el máximo, pero el resto del mapa recupera su contraste. Los valores
# reales (sin recortar) se siguen viendo en el hover y en la tabla.
techo_color = df_f[metrica].quantile(0.95)

fig_mapa = px.choropleth_mapbox(
    df_f,
    geojson=geojson,
    locations="cp",
    featureidkey="properties.cp",
    color=metrica,
    color_continuous_scale="Oranges",
    range_color=(df_f[metrica].min(), techo_color),
    mapbox_style="carto-darkmatter",
    zoom=6.6,
    center={"lat": 22.15, "lon": -100.7},
    opacity=0.8,
    hover_name="cp",
    hover_data={
        "sector_principal": True,
        "negocios_estimados": ":,",
        "densidad_negocios_km2": ":,.1f",
    },
)
fig_mapa.update_coloraxes(colorbar_title_text="", colorbar_ticksuffix="+" if metrica == "densidad_negocios_km2" else "")
fig_mapa.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=580)
st.plotly_chart(fig_mapa, use_container_width=True)
st.caption(
    "La escala de color se limita al percentil 95 para que unas pocas zonas "
    "extremas no aplasten el contraste del resto del mapa. Los valores "
    "exactos siguen disponibles al pasar el cursor y en la tabla."
)

st.markdown("---")

# ----------------------------------------------------------------------
# Gráficas + tabla
# ----------------------------------------------------------------------
col_izq, col_der = st.columns([1.2, 1])

with col_izq:
    st.subheader("Negocios por sector")
    df_sector = df_f.groupby("sector_principal", as_index=False)["negocios_estimados"].sum()
    df_sector = df_sector.sort_values("negocios_estimados", ascending=False)
    fig_barras = px.bar(
        df_sector,
        x="negocios_estimados",
        y="sector_principal",
        orientation="h",
        labels={"negocios_estimados": "Negocios", "sector_principal": "Sector"},
        color_discrete_sequence=[ACCENT],
    )
    fig_barras.update_layout(yaxis={"categoryorder": "total ascending"})
    fig_barras.update_traces(marker_line_width=0)
    tema_plotly(fig_barras, altura=340)
    st.plotly_chart(fig_barras, use_container_width=True)

    st.subheader("Top 15 zonas con más negocios")
    # OJO: 'cp' es texto (ej. "78000"), pero al parecerse a un número
    # Plotly lo trataba como eje numérico continuo y las barras salían
    # como líneas casi invisibles. Forzamos el eje como categoría.
    df_top = df_f.sort_values("negocios_estimados", ascending=False).head(15)
    df_top = df_top.sort_values("negocios_estimados", ascending=True)  # para que la barra más alta quede arriba
    fig_top = px.bar(
        df_top,
        x="negocios_estimados",
        y="cp",
        orientation="h",
        labels={"negocios_estimados": "Negocios estimados", "cp": "Código Postal"},
        color_discrete_sequence=[ACCENT],
        text="negocios_estimados",
    )
    fig_top.update_yaxes(type="category")  # <- el fix real del bug
    fig_top.update_traces(marker_line_width=0, textposition="outside", texttemplate="%{text:,}")
    fig_top.update_layout(showlegend=False, margin={"l": 10, "r": 40})
    tema_plotly(fig_top, altura=460)
    st.plotly_chart(fig_top, use_container_width=True)

with col_der:
    st.subheader("Datos")
    st.dataframe(
        df_f.sort_values("negocios_estimados", ascending=False)[
            ["cp", "sector_principal", "negocios_estimados", "densidad_negocios_km2", "area_km2"]
        ].reset_index(drop=True),
        use_container_width=True,
        height=820,
    )

st.caption("Hecho con Streamlit + Plotly")

# ----------------------------------------------------------------------
# DATOS REALES DE DENUE (opcional)
# ----------------------------------------------------------------------
# Para reemplazar el dataset simulado con negocios REALES del DENUE
# (Directorio Estadístico Nacional de Unidades Económicas) de INEGI:
#
# 1. Saca un token gratuito aquí (toma 2 minutos):
#    https://www.inegi.org.mx/servicios/api_denue.html
#
# 2. Instala requests si no lo tienes:  pip install requests
#
# 3. Usa una función como esta para consultar negocios por municipio
#    o por actividad económica en San Luis Potosí (clave de entidad = 24):
#
#    import requests
#
#    def consultar_denue(condicion, entidad="24", token="TU_TOKEN"):
#        url = (
#            f"https://www.inegi.org.mx/app/api/denue/v1/consulta/"
#            f"BuscarEntidad/{condicion}/{entidad}/{token}"
#        )
#        resp = requests.get(url)
#        resp.raise_for_status()
#        return resp.json()
#
#    # ejemplo: buscar restaurantes en SLP
#    datos = consultar_denue("restaurantes")
#
# 4. Cada negocio viene con su Código Postal (campo "CodigoPostal") y
#    coordenadas (Latitud/Longitud), así que puedes agrupar por CP con
#    pandas (`df.groupby("CodigoPostal").size()`) para armar un CSV con
#    la misma estructura que `denue_slp_demo.csv` y sustituirlo aquí.
#
# Nota: el API tiene límites de consultas por token; para todo el estado
# puede que necesites iterar por municipio o por actividad económica.sytre