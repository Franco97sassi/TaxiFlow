
import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from time import perf_counter

# Rutas del proyecto
RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "data" / "warehouse" / "taxiflow.duckdb"

# Localizar el ejecutable de dbt
DBT = shutil.which("dbt")

logger = logging.getLogger("taxiflow.pipeline")


def ejecutar(nombre: str, comando: list[str], entorno: dict):
    """Ejecuta una tarea y registra su resultado."""

    inicio = perf_counter()
    logger.info("INICIO | %s", nombre)

    try:
        subprocess.run(
            comando,
            cwd=RAIZ,
            env=entorno,
            check=True
        )

    except (subprocess.CalledProcessError, OSError):
        logger.exception("FALLO | %s", nombre)
        raise

    segundos = perf_counter() - inicio

    logger.info(
        "OK | %s | %.2f segundos",
        nombre,
        segundos
    )


def main():
    parser = argparse.ArgumentParser(
        description="Orquestador del pipeline TaxiFlow"
    )

    parser.add_argument(
        "--solo-validar",
        action="store_true",
        help="Ejecuta pruebas sobre una base existente"
    )

    args = parser.parse_args()

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    # Variables de entorno para dbt
    entorno = os.environ.copy()
    entorno["TAXIFLOW_DB_PATH"] = BASE.as_posix()

    tareas = []

    if not args.solo_validar:

        # Verificar que dbt esté disponible
        if DBT is None:
            logger.error(
                "No se encontró dbt en el entorno virtual"
            )
            return 1

        # 1. Ingesta de datos
        for mes in [1, 2]:
            tareas.append((
                f"Ingesta 2025-{mes:02d}",
                [
                    sys.executable,
                    "src/ingesta.py",
                    "--anio", "2025",
                    "--mes", str(mes)
                ]
            ))

        # 2. Transformación, limpieza y warehouse
        tareas.extend([
            (
                "Transformación STAGING",
                [
                    sys.executable,
                    "src/transformacion.py"
                ]
            ),
            (
                "Limpieza CLEAN",
                [
                    sys.executable,
                    "src/limpieza.py"
                ]
            ),
            (
                "Construcción dbt",
                [
                    DBT,
                    "build",
                    "--profiles-dir", "."
                ]
            )
        ])

    # 3. Validaciones y tests
    tareas.extend([
        (
            "Conciliación del Warehouse",
            [
                sys.executable,
                "tests/verificar_warehouse.py"
            ]
        ),
        (
            "Pruebas Python",
            [
                sys.executable,
                "-m", "unittest",
                "discover",
                "-s", "tests",
                "-p", "test_*.py",
                "-v"
            ]
        )
    ])

    # 4. Ejecutar tareas en orden
    inicio_pipeline = perf_counter()

    try:
        for nombre, comando in tareas:
            ejecutar(nombre, comando, entorno)

    except (subprocess.CalledProcessError, OSError):
        logger.error("PIPELINE FALLIDO")
        return 1

    duracion = perf_counter() - inicio_pipeline

    logger.info(
        "PIPELINE COMPLETADO CORRECTAMENTE"
    )

    logger.info(
        "Duración total: %.2f segundos",
        duracion
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
