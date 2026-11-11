import unittest
from app.pipeline.preprocesador import normalizar, raiz, cantidad


class PreprocesadorTest(unittest.TestCase):
    def test_quita_tildes_y_conserva_enie(self):
        self.assertEqual(normalizar('Ají y PIÑA'), 'aji y piña')

    def test_cantidades_de_varias_palabras(self):
        self.assertEqual(normalizar('un par de colas'), '2 colas')
        self.assertEqual(normalizar('media docena de empanadas'), '6 empanadas')

    def test_quita_muletillas(self):
        self.assertEqual(normalizar('Me regala una cola por favor'), 'una cola')

    def test_singular(self):
        self.assertEqual(raiz('cuyes'), 'cuy')
        self.assertEqual(raiz('colas'), 'cola')
        self.assertEqual(raiz('medianos'), 'mediano')

    def test_cantidad_en_palabras(self):
        self.assertEqual(cantidad('tres'), 3)
        self.assertEqual(cantidad('12'), 12)
        self.assertIsNone(cantidad('cuy'))


if __name__ == '__main__':
    unittest.main()
