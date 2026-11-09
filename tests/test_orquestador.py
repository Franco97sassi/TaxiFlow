
import os
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from pipeline import ejecutar


class TestOrquestador(unittest.TestCase):

    def test_tarea_exitosa(self):
        ejecutar(
            "Prueba exitosa",
            [sys.executable, "-c", "print('OK')"],
            os.environ.copy()
        )

    def test_tarea_fallida(self):
        with self.assertRaises(
            __import__("subprocess").CalledProcessError
        ):
            ejecutar(
                "Prueba de fallo",
                [sys.executable, "-c", "raise SystemExit(1)"],
                os.environ.copy()
            )


if __name__ == "__main__":
    unittest.main()
