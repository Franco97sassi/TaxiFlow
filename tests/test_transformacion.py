
from pathlib import Path
import unittest
import duckdb

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "data" / "warehouse" / "taxiflow.duckdb"


class TestTransformacion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.con = duckdb.connect(str(BASE), read_only=True)

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def test_cantidad_staging(self):
        total = self.con.execute(
            "SELECT COUNT(*) FROM staging.viajes"
        ).fetchone()[0]

        self.assertEqual(total, 7052769)

    def test_periodos(self):
        periodos = self.con.execute("""
            SELECT DISTINCT periodo_origen
            FROM staging.viajes
            ORDER BY 1
        """).fetchall()

        self.assertEqual(
            periodos,
            [("2025-01",), ("2025-02",)]
        )

    def test_conciliacion(self):
        total, clean, ajustes, excluidos = self.con.execute("""
            SELECT
                (SELECT COUNT(*) FROM staging.viajes),
                (SELECT COUNT(*) FROM clean.viajes),
                (SELECT COUNT(*) FROM clean.ajustes),
                (SELECT COUNT(*) FROM staging.viajes
                 WHERE excluir_clean
                   AND tipo_importe = 'ORDINARIO')
        """).fetchone()

        self.assertEqual(total, clean + ajustes + excluidos)

    def test_clean_sin_excluidos(self):
        errores = self.con.execute("""
            SELECT COUNT(*)
            FROM clean.viajes
            WHERE excluir_clean
               OR tipo_importe <> 'ORDINARIO'
               OR tipo_importe IS NULL
        """).fetchone()[0]

        self.assertEqual(errores, 0)


if __name__ == "__main__":
    unittest.main()
