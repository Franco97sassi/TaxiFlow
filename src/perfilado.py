
from pathlib import Path
import duckdb

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO = RAIZ / "data" / "raw" / "yellow_tripdata_2025-01.parquet"


def perfilar_datos():
    if not ARCHIVO.is_file():
        raise FileNotFoundError(f"No existe el dataset: {ARCHIVO}")

    con = duckdb.connect()

    try:
        ruta = str(ARCHIVO)

        print("\n=== ESQUEMA DEL DATASET ===")
        esquema = con.execute(
            "DESCRIBE SELECT * FROM read_parquet(?)",
            [ruta]
        ).fetchdf()
        print(esquema.to_string(index=False))

        print("\n=== CANTIDAD DE REGISTROS ===")
        cantidad = con.execute(
            "SELECT COUNT(*) FROM read_parquet(?)",
            [ruta]
        ).fetchone()[0]
        print(f"Total de viajes: {cantidad:,}")

        print("\n=== ESTADÍSTICAS GENERALES ===")
        estadisticas = con.execute("""
            SELECT
                MIN(trip_distance) AS distancia_minima,
                MAX(trip_distance) AS distancia_maxima,
                ROUND(AVG(trip_distance), 2) AS distancia_promedio,
                ROUND(AVG(total_amount), 2) AS importe_promedio
            FROM read_parquet(?)
        """, [ruta]).fetchdf()
        print(estadisticas.to_string(index=False))

        print("\n=== VALORES NULOS ===")
        nulos = con.execute("""
            SELECT
                COUNT(*) FILTER (
                    WHERE tpep_pickup_datetime IS NULL
                ) AS fechas_nulas,
                COUNT(*) FILTER (
                    WHERE trip_distance IS NULL
                ) AS distancias_nulas,
                COUNT(*) FILTER (
                    WHERE total_amount IS NULL
                ) AS importes_nulos
            FROM read_parquet(?)
        """, [ruta]).fetchdf()
        print(nulos.to_string(index=False))

    finally:
        con.close()


if __name__ == "__main__":
    perfilar_datos()
