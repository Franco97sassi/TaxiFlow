
from pathlib import Path
import duckdb

RAIZ = Path(__file__).resolve().parent.parent
BASE_DATOS = RAIZ / "data" / "warehouse" / "taxiflow.duckdb"
ARCHIVO_SQL = RAIZ / "sql" / "clean.sql"


def limpiar_datos():
    if not BASE_DATOS.is_file():
        raise FileNotFoundError(
            "Primero ejecutá src/transformacion.py"
        )

    sql = ARCHIVO_SQL.read_text(encoding="utf-8")

    con = duckdb.connect(str(BASE_DATOS))

    try:
        con.begin()
        con.execute(sql)

        resultado = con.execute("""
            SELECT
                (SELECT COUNT(*)
                 FROM staging.viajes) AS total_staging,

                (SELECT COUNT(*)
                 FROM clean.viajes) AS total_clean,

                (SELECT COUNT(*)
                 FROM clean.ajustes) AS total_ajustes,

                (SELECT COUNT(*)
                 FROM clean.viajes
                 WHERE requiere_revision) AS viajes_revision,

                (SELECT COUNT(*)
                 FROM staging.viajes
                 WHERE excluir_clean
                   AND tipo_importe = 'ORDINARIO'
                ) AS ordinarios_excluidos
        """).fetchone()

        (
            total_staging,
            total_clean,
            total_ajustes,
            viajes_revision,
            ordinarios_excluidos,
        ) = resultado

        if total_staging != (
            total_clean + total_ajustes + ordinarios_excluidos
        ):
            raise ValueError(
                "Falló la conciliación de registros"
            )

        con.commit()

        print("=== RESULTADOS DE CLEAN ===")
        print(f"Staging: {total_staging:,}")
        print(f"Viajes CLEAN: {total_clean:,}")
        print(f"Ajustes potenciales: {total_ajustes:,}")
        print(f"Viajes CLEAN para revisión: {viajes_revision:,}")
        print(f"Ordinarios excluidos: {ordinarios_excluidos:,}")
        print("\nConciliación: OK")

    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


if __name__ == "__main__":
    limpiar_datos()
