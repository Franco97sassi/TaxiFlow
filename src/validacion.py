
from pathlib import Path
import duckdb

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO = RAIZ / "data" / "raw" / "yellow_tripdata_2025-01.parquet"

COLUMNAS_REQUERIDAS = {
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "trip_distance",
    "total_amount",
}


def validar_datos():
    if not ARCHIVO.is_file():
        raise FileNotFoundError(f"No existe: {ARCHIVO}")

    con = duckdb.connect()

    try:
        ruta = str(ARCHIVO)

        esquema = con.execute(
            "DESCRIBE SELECT * FROM read_parquet(?)",
            [ruta]
        ).fetchall()

        columnas = {fila[0] for fila in esquema}
        faltantes = COLUMNAS_REQUERIDAS - columnas

        if faltantes:
            raise ValueError(
                f"Columnas faltantes: {sorted(faltantes)}"
            )

        print("=== VALIDACIÓN DEL ESQUEMA ===")
        print("Columnas requeridas: OK")

        resultado = con.execute("""
            SELECT
                COUNT(*) AS total_registros,

                COUNT(*) FILTER (
                    WHERE tpep_pickup_datetime IS NULL
                       OR tpep_dropoff_datetime IS NULL
                       OR trip_distance IS NULL
                       OR total_amount IS NULL
                ) AS registros_incompletos,

                COUNT(*) FILTER (
                    WHERE trip_distance < 0
                ) AS distancias_negativas,

                COUNT(*) FILTER (
                    WHERE trip_distance > 100
                ) AS distancias_extremas,

                COUNT(*) FILTER (
                    WHERE total_amount < 0
                ) AS importes_negativos,

                COUNT(*) FILTER (
                    WHERE tpep_dropoff_datetime
                          < tpep_pickup_datetime
                ) AS fechas_inconsistentes,

                COUNT(*) FILTER (
                    WHERE tpep_pickup_datetime
                          = tpep_dropoff_datetime
                ) AS viajes_duracion_cero

            FROM read_parquet(?)
        """, [ruta]).fetchone()

        nombres = [
            "Total de registros",
            "Registros incompletos",
            "Distancias negativas",
            "Distancias extremas (>100 millas)",
            "Importes negativos",
            "Fechas inconsistentes",
            "Viajes de duración cero",
        ]

        print("\n=== REPORTE DE CALIDAD ===")
        for nombre, valor in zip(nombres, resultado):
            print(f"{nombre}: {valor:,}")

        if resultado[0] == 0:
            raise ValueError("El dataset está vacío.")

        print("\nValidación estructural completada.")
        print("Las anomalías se conservarán para su análisis.")

    finally:
        con.close()


if __name__ == "__main__":
    validar_datos()
