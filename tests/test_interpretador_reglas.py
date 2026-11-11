"""Escenarios de aceptación de las HU-22, HU-23 y HU-24 sobre el motor de reglas."""
import json
import unittest
from app.pipeline.interpretador_reglas import interpretar

MENU = json.load(open('data/menu_ejemplo.json', encoding='utf8'))


def resumen(r):
    return [(i['producto'], i['cantidad'], i['modificaciones']) for i in r['items']]


class InterpretadorReglasTest(unittest.TestCase):
    def test_hu22_interpretacion_correcta(self):
        r = interpretar('dos cuyes medianos y una gaseosa', MENU)
        self.assertEqual(resumen(r), [('Cuy asado mediano', 2, []), ('Gaseosa', 1, [])])
        self.assertEqual(r['intencion'], 'PEDIR')

    def test_hu22_cantidades_en_palabras_y_nombres_locales(self):
        self.assertEqual(resumen(interpretar('un par de colas', MENU)), [('Gaseosa', 2, [])])

    def test_hu22_producto_fuera_del_menu(self):
        r = interpretar('una pizza y un jugo de lulo', MENU)
        self.assertEqual(resumen(r), [('Jugo de lulo', 1, [])])
        self.assertEqual(r['noReconocidos'], ['pizza'])

    def test_hu22_frase_sin_pedido(self):
        r = interpretar('buenas tardes', MENU)
        self.assertEqual(r['items'], [])
        self.assertIn('No se identificó ningún producto', r['mensaje'])

    def test_hu23_modificacion_de_un_producto(self):
        self.assertEqual(resumen(interpretar('una hamburguesa sin cebolla', MENU)), [('Hamburguesa', 1, ['sin cebolla'])])

    def test_hu23_modificacion_de_una_parte(self):
        r = interpretar('dos hamburguesas, una sin cebolla', MENU)
        self.assertEqual(resumen(r), [('Hamburguesa', 1, []), ('Hamburguesa', 1, ['sin cebolla'])])

    def test_hu23_restriccion_alimentaria(self):
        r = interpretar('un ceviche, el cliente es alérgico al maní', MENU)
        self.assertEqual(r['restricciones'], ['alergia a mani'])

    def test_hu23_modificacion_ambigua(self):
        r = interpretar('dos hamburguesas y un jugo, sin picante', MENU)
        self.assertEqual(r['modificacionesSinAsignar'], ['sin picante'])

    def test_hu24_baja_confianza_pide_verificar(self):
        r = interpretar('dos cuyes', MENU)   # no dice si es mediano o grande
        self.assertTrue(r['items'][0]['verificar'])
        self.assertLess(r['items'][0]['confianza'], 0.80)

    def test_tolera_errores_de_escritura(self):
        r = interpretar('una truha frita', MENU)
        self.assertEqual(r['items'][0]['producto'], 'Trucha frita')

    def test_producto_agotado_se_marca_para_verificar(self):
        menu = [dict(p, disponible=(p['id'] != 8)) for p in MENU]
        self.assertTrue(interpretar('una gaseosa', menu)['items'][0]['verificar'])

    def test_tiempo_de_respuesta_bajo_dos_segundos(self):
        self.assertLess(interpretar('dos cuyes medianos, uno sin ají, y una cola', MENU)['tiempoMs'], 2000)


if __name__ == '__main__':
    unittest.main()
