
from pathlib import Path
import duckdb

RAIZ = Path(__file__).resolve().parent.parent

CARPETA_RAW = RAIZ / "data" / "raw"
BASE_DATOS = RAIZ / "data" / "warehouse" / "taxiflow.duckdb"
ARCHIVO_SQL = RAIZ / "sql" / "staging.sql"

PERIODOS = ["2025-01", "2025-02"]


def transformar_datos():
    archivos = [
        CARPETA_RAW / f"yellow_tripdata_{periodo}.parquet"
        for periodo in PERIODOS
    ]

    faltantes = [str(p) for p in archivos if not p.is_file()]

    if faltantes:
        raise FileNotFoundError(
            f"Datasets faltantes: {faltantes}"
        )

    BASE_DATOS.parent.mkdir(parents=True, exist_ok=True)

    sql = ARCHIVO_SQL.read_text(encoding="utf-8")
    sentencia = sql.split(";", 1)[1].strip()

    con = duckdb.connect(str(BASE_DATOS))

    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS staging")

        print("Transformando múltiples meses...")

        con.begin()

        try:
            con.execute(
                sentencia,
                [[str(archivo) for archivo in archivos]]
            )

            resultados = con.execute("""
                SELECT
                    periodo_origen,
                    COUNT(*) AS total
                FROM staging.viajes
                GROUP BY periodo_origen
                ORDER BY periodo_origen
            """).fetchall()

            total = sum(cantidad for _, cantidad in resultados)

            if total == 0 or len(resultados) != len(PERIODOS):
                raise ValueError(
                    "La transformación no contiene los períodos esperados"
                )

            print("\n=== RESULTADOS DE STAGING ===")

            for periodo, cantidad in resultados:
                print(f"{periodo}: {cantidad:,} registros")

            print(f"\nTotal: {total:,}")

            con.commit()

        except Exception:
            con.rollback()
            raise

    finally:
        con.close()


if __name__ == "__main__":
    transformar_datos()
