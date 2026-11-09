
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from analitica import (
    obtener_kpis,
    obtener_viajes_diarios,
    obtener_medios_pago,
)


class TestAnalitica(unittest.TestCase):

    def test_total_viajes(self):
        kpis = obtener_kpis()

        self.assertEqual(
            kpis[0],
            6_927_342
        )

    def test_ingresos_positivos(self):
        kpis = obtener_kpis()

        self.assertGreater(
            kpis[1],
            0
        )

    def test_distancia_promedio(self):
        kpis = obtener_kpis()

        self.assertGreater(
            kpis[3],
            0
        )

    def test_viajes_diarios(self):
        diarios = obtener_viajes_diarios()

        self.assertFalse(diarios.empty)

        self.assertEqual(
            int(diarios["viajes"].sum()),
            6_927_342
        )

    def test_medios_pago(self):
        pagos = obtener_medios_pago()

        self.assertFalse(pagos.empty)

        self.assertEqual(
            int(pagos["viajes"].sum()),
            6_927_342
        )


if __name__ == "__main__":
    unittest.main()
