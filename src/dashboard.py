
from datetime import date
from pathlib import Path

import duckdb
import plotly.express as px
import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "data" / "warehouse" / "taxiflow.duckdb"

st.set_page_config(
    page_title="TaxiFlow Analytics",
    page_icon="🚕",
    layout="wide"
)

st.title("🚕 TaxiFlow Analytics Dashboard")
st.caption("NYC Yellow Taxi | DuckDB + SQL + Streamlit")


@st.cache_data(ttl=300)
def cargar_filtros():
    con = duckdb.connect(str(BASE), read_only=True)
    try:
        fechas = con.execute("""
            SELECT
                MIN(CAST(fecha_inicio AS DATE)),
                MAX(CAST(fecha_inicio AS DATE))
            FROM analytics.fct_viajes
        """).fetchone()

        pagos = con.execute("""
            SELECT DISTINCT tipo_pago
            FROM analytics.dim_pago
            ORDER BY tipo_pago
        """).fetchall()

        return fechas, [fila[0] for fila in pagos]
    finally:
        con.close()


@st.cache_data(ttl=300)
def cargar_analitica(inicio, fin, medio_pago):
    con = duckdb.connect(str(BASE), read_only=True)

    try:
        filtro = """
            FROM analytics.fct_viajes f
            JOIN analytics.dim_pago p
              ON f.pago_id = p.pago_id
            WHERE CAST(f.fecha_inicio AS DATE) BETWEEN ? AND ?
              AND (? = 'Todos' OR p.tipo_pago = ?)
        """

        parametros = [inicio, fin, medio_pago, medio_pago]

        kpis = con.execute("""
            SELECT COUNT(*),
                   COALESCE(SUM(f.total_amount), 0),
                   AVG(f.fare_amount),
                   AVG(f.trip_distance),
                   AVG(f.duracion_minutos)
        """ + filtro, parametros).fetchone()

        diarios = con.execute("""
            SELECT
                CAST(f.fecha_inicio AS DATE) AS fecha,
                COUNT(*) AS viajes,
                SUM(f.total_amount) AS ingresos
        """ + filtro + """
            GROUP BY 1
            ORDER BY 1
        """, parametros).fetchdf()

        pagos = con.execute("""
            SELECT
                p.tipo_pago,
                COUNT(*) AS viajes
        """ + filtro + """
            GROUP BY 1
            ORDER BY viajes DESC
        """, parametros).fetchdf()

        return kpis, diarios, pagos
    finally:
        con.close()


if not BASE.is_file():
    st.error("No se encontró el Data Warehouse.")
    st.stop()

try:
    (fecha_min, fecha_max), opciones_pago = cargar_filtros()

    st.sidebar.header("Filtros")

    inicio = st.sidebar.date_input(
        "Fecha inicial",
        value=date(2025, 1, 1),
        min_value=fecha_min,
        max_value=fecha_max
    )

    fin = st.sidebar.date_input(
        "Fecha final",
        value=date(2025, 2, 28),
        min_value=fecha_min,
        max_value=fecha_max
    )

    medio_pago = st.sidebar.selectbox(
        "Medio de pago",
        ["Todos"] + opciones_pago
    )

    if inicio > fin:
        st.error("La fecha inicial no puede superar la final.")
        st.stop()

    kpis, diarios, pagos = cargar_analitica(
        inicio, fin, medio_pago
    )

except Exception as error:
    st.error(f"Error al consultar los datos: {error}")
    st.stop()


st.subheader("Indicadores del período")

total, ingresos, tarifa, distancia, duracion = kpis

if total == 0:
    st.warning("No hay viajes para los filtros seleccionados.")
    st.stop()

c1, c2, c3 = st.columns(3)

c1.metric("Total de viajes", f"{total:,.0f}")
c2.metric("Importe registrado", f"US$ {ingresos:,.2f}")
c3.metric("Tarifa promedio", f"US$ {tarifa:,.2f}")

c4, c5 = st.columns(2)

c4.metric("Distancia promedio", f"{distancia:.2f} millas")
c5.metric("Duración promedio", f"{duracion:.2f} min")

st.divider()

st.subheader("Evolución diaria de viajes")

fig_viajes = px.line(
    diarios,
    x="fecha",
    y="viajes",
    labels={"fecha": "Fecha", "viajes": "Viajes"}
)

st.plotly_chart(fig_viajes, use_container_width=True)

st.subheader("Importes diarios")

fig_ingresos = px.bar(
    diarios,
    x="fecha",
    y="ingresos",
    labels={"fecha": "Fecha", "ingresos": "USD"}
)

st.plotly_chart(fig_ingresos, use_container_width=True)

st.subheader("Distribución por medio de pago")

fig_pagos = px.pie(
    pagos,
    names="tipo_pago",
    values="viajes",
    hole=0.4
)

st.plotly_chart(fig_pagos, use_container_width=True)

st.subheader("Datos diarios")

st.dataframe(diarios, use_container_width=True, hide_index=True)

st.download_button(
    "Descargar datos filtrados (CSV)",
    data=diarios.to_csv(index=False).encode("utf-8"),
    file_name="taxiflow_analytics.csv",
    mime="text/csv"
)

st.caption(
    "Importes registrados de viajes ordinarios; "
    "no representan necesariamente ingresos netos."
)
