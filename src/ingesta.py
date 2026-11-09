
import argparse
import logging
from datetime import date
from pathlib import Path

import duckdb
import requests

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_RAW = RAIZ / "data" / "raw"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("taxiflow")


def validar_parquet(ruta: Path) -> int:
    con = duckdb.connect()
    try:
        total = con.execute(
            "SELECT COUNT(*) FROM read_parquet(?)",
            [str(ruta)],
        ).fetchone()[0]

        if total == 0:
            raise ValueError("El dataset está vacío")

        return total
    finally:
        con.close()


def descargar_datos(anio: int, mes: int):
    if not 2009 <= anio <= date.today().year:
        raise ValueError("Año fuera de rango")

    if not 1 <= mes <= 12:
        raise ValueError("El mes debe estar entre 1 y 12")

    periodo = f"{anio}-{mes:02d}"
    nombre = f"yellow_tripdata_{periodo}.parquet"

    url = (
        "https://d37ci6vzurychx.cloudfront.net/"
        f"trip-data/{nombre}"
    )

    CARPETA_RAW.mkdir(parents=True, exist_ok=True)
    destino = CARPETA_RAW / nombre
    temporal = CARPETA_RAW / f"{nombre}.part"

    if destino.exists():
        try:
            total = validar_parquet(destino)
            logger.info(
                "Archivo existente y válido: %s (%s registros)",
                nombre, total,
            )
            return
        except (duckdb.Error, ValueError):
            logger.warning("Archivo existente inválido: %s", nombre)

    logger.info("Iniciando descarga: %s", nombre)

    try:
        with requests.get(
            url, stream=True, timeout=(10, 120)
        ) as respuesta:
            respuesta.raise_for_status()

            with temporal.open("wb") as archivo:
                for bloque in respuesta.iter_content(
                    chunk_size=1024 * 1024
                ):
                    if bloque:
                        archivo.write(bloque)

        total = validar_parquet(temporal)
        temporal.replace(destino)

        logger.info("Descarga completada: %s", nombre)
        logger.info("Registros: %s", total)
        logger.info(
            "Tamaño: %.2f MB",
            destino.stat().st_size / (1024 * 1024),
        )

    except Exception:
        temporal.unlink(missing_ok=True)
        logger.exception("Falló la ingesta de %s", periodo)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingesta de datos NYC Taxi"
    )
    parser.add_argument("--anio", type=int, default=2025)
    parser.add_argument("--mes", type=int, default=1)
    args = parser.parse_args()

    descargar_datos(args.anio, args.mes)
