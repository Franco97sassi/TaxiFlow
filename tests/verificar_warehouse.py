
from pathlib import Path
import duckdb

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "data" / "warehouse" / "taxiflow.duckdb"

con = duckdb.connect(str(BASE), read_only=True)

try:
    total_clean = con.execute("""
        SELECT COUNT(*) FROM clean.viajes
    """).fetchone()[0]

    total_fact = con.execute("""
        SELECT COUNT(*) FROM analytics.fct_viajes
    """).fetchone()[0]

    print(f"Viajes CLEAN: {total_clean:,}")
    print(f"Viajes FACT: {total_fact:,}")

    assert total_clean == total_fact, (
        "La cantidad de registros no coincide"
    )

    print("Conciliación del Data Warehouse: OK")
finally:
    con.close()
