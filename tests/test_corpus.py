"""Valida el formato del corpus anotado (responsable: Jack)."""
import json
import os
import unittest

MENU = {p['nombre'] for p in json.load(open('data/menu_ejemplo.json', encoding='utf8'))}
INTENCIONES = {'PEDIR', 'MODIFICAR', 'CANCELAR', 'CONSULTAR_MENU', 'OTRO'}


class CorpusTest(unittest.TestCase):
    def test_semilla_bien_formada(self):
        ruta = 'data/corpus/semilla.jsonl'
        self.assertTrue(os.path.exists(ruta))
        for n, linea in enumerate(open(ruta, encoding='utf8'), 1):
            ej = json.loads(linea)
            self.assertTrue(ej['frase'].strip(), f'línea {n}: frase vacía')
            self.assertIn(ej['intencion'], INTENCIONES, f'línea {n}')
            for it in ej['items']:
                self.assertIn(it['producto'], MENU, f'línea {n}: producto fuera del menú')
                self.assertGreaterEqual(it['cantidad'], 1)
                self.assertIsInstance(it['modificaciones'], list)


if __name__ == '__main__':
    unittest.main()
