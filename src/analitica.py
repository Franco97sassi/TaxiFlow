
from pathlib import Path

import duckdb

RAIZ = Path(__file__).resolve().parent.parent

BASE_DATOS = (
    RAIZ / "data" / "warehouse" / "taxiflow.duckdb"
)


def conectar():
    if not BASE_DATOS.is_file():
        raise FileNotFoundError(
            "No existe el Data Warehouse. "
            "Ejecutá primero python src/pipeline.py"
        )

    return duckdb.connect(
        str(BASE_DATOS),
        read_only=True
    )


def obtener_kpis():
    con = conectar()

    try:
        resultado = con.execute("""
            SELECT
                COUNT(*) AS total_viajes,
                ROUND(SUM(total_amount), 2) AS ingresos,
                ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
                ROUND(AVG(trip_distance), 2) AS distancia_promedio,
                ROUND(AVG(duracion_minutos), 2) AS duracion_promedio
            FROM analytics.fct_viajes
        """).fetchone()

        return resultado
    finally:
        con.close()


def obtener_viajes_diarios():
    con = conectar()

    try:
        return con.execute("""
            SELECT
                CAST(fecha_inicio AS DATE) AS fecha,
                COUNT(*) AS viajes,
                ROUND(SUM(total_amount), 2) AS ingresos
            FROM analytics.fct_viajes
            GROUP BY 1
            ORDER BY 1
        """).fetchdf()
    finally:
        con.close()


def obtener_medios_pago():
    con = conectar()

    try:
        return con.execute("""
            SELECT
                p.tipo_pago,
                COUNT(*) AS viajes
            FROM analytics.fct_viajes f
            JOIN analytics.dim_pago p
                ON f.pago_id = p.pago_id
            GROUP BY 1
            ORDER BY viajes DESC
        """).fetchdf()
    finally:
        con.close()


if __name__ == "__main__":
    print("=== TAXIFLOW ANALYTICS ===")

    kpis = obtener_kpis()

    nombres = [
        "Total viajes",
        "Ingresos registrados",
        "Tarifa promedio",
        "Distancia promedio",
        "Duración promedio"
    ]

    for nombre, valor in zip(nombres, kpis):
        print(f"{nombre}: {valor:,.2f}")

    print("\n=== VIAJES DIARIOS ===")
    print(obtener_viajes_diarios().head(5))

    print("\n=== MEDIOS DE PAGO ===")
    print(obtener_medios_pago())
