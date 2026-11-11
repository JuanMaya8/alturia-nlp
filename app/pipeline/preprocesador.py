"""Paso 1 del diagrama C4 del servicio NLP: normaliza la frase y convierte números escritos en dígitos."""
import re
import unicodedata

NUMEROS = {
    'un': 1, 'una': 1, 'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5, 'seis': 6, 'siete': 7,
    'ocho': 8, 'nueve': 9, 'diez': 10, 'once': 11, 'doce': 12, 'quince': 15, 'veinte': 20,
}
# Expresiones de cantidad de varias palabras (se aplican antes de separar)
FRASES_CANTIDAD = [
    (r'\bmedia docena de\b', '6'), (r'\buna docena de\b', '12'), (r'\bun par de\b', '2'),
    (r'\bpar de\b', '2'), (r'\bun parcito de\b', '2'),
]
# Modismos y muletillas frecuentes al pedir que no aportan información
RELLENO = r'\b(por favor|porfa|porfavor|me regala|me regalas|regaleme|regálame|me da|deme|dame|quiero|queremos|para la mesa|nos trae|traiganos|tráiganos|me trae|me trae)\b'


def sin_tildes(texto: str) -> str:
    # Conserva la ñ: solo quita tildes y diéresis
    nfd = unicodedata.normalize('NFD', texto.replace('ñ', '\0').replace('Ñ', '\1'))
    limpio = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    return limpio.replace('\0', 'ñ').replace('\1', 'Ñ')


def normalizar(frase: str) -> str:
    t = sin_tildes(frase.lower())
    t = re.sub(r'[¡!¿?\.;:"]', ' ', t)
    for patron, reemplazo in FRASES_CANTIDAD:
        t = re.sub(patron, reemplazo, t)
    t = re.sub(RELLENO, ' ', sin_tildes(t))
    t = re.sub(r'\s*,\s*', ' , ', t)
    return re.sub(r'\s+', ' ', t).strip()


def raiz(palabra: str) -> str:
    """Singular aproximado para comparar: cuyes→cuy, colas→cola, medianos→mediano, jugos→jugo."""
    p = palabra
    if len(p) > 4 and p.endswith('es') and p[-3] in 'yrlnd':
        return p[:-2]
    if len(p) > 3 and p.endswith('s'):
        return p[:-1]
    return p


def cantidad(token: str):
    if token.isdigit():
        return int(token)
    return NUMEROS.get(token)
