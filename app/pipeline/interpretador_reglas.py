"""
Línea base del modelo NLP: reglas y diccionario del menú (enfoque 1 de la tabla de enfoques candidatos).
Implementa los pasos 2 a 5 del diagrama C4 del servicio NLP: intención, entidades, resolución contra el menú
y evaluación de confianza. No depende de librerías externas y funciona sin internet.
"""
import re
import time
from difflib import SequenceMatcher
from .preprocesador import normalizar, raiz, cantidad, sin_tildes

UMBRAL_CONFIANZA = 0.80
SEPARADORES = {',', 'y', 'e', 'mas', 'tambien', 'ademas', 'otra', 'otro'}
PALABRAS_VACIAS = {'de', 'del', 'la', 'el', 'los', 'las', 'con', 'en', 'al', 'a', 'que', 'pa', 'para', 'mi', 'su'}
PATRONES_MODIFICACION = [
    r'\bsin [a-zñ]+(?: [a-zñ]+)?', r'\bbien (?:asad[oa]s?|cocid[oa]s?|frit[oa]s?|fri[oa]s?|caliente)', r'\btermino (?:medio|tres cuartos)',
    r'\bpoco (?:picante|sal|aji|hielo|azucar)', r'\bextra [a-zñ]+', r'\bcon (?:hielo|limon|aji|picante|queso|salsa [a-zñ]+)',
    r'\bsin hielo', r'\bal clima', r'\bpara llevar', r'\bdoble [a-zñ]+',
]
PATRONES_RESTRICCION = [
    (r'\b(?:es |soy |son )?alergic[oa]s? (?:a|al|a la|a los|a las) ([a-zñ]+(?: [a-zñ]+)?)', 'alergia a {0}'),
    (r'\balergia (?:a|al|a la|a los|a las) ([a-zñ]+(?: [a-zñ]+)?)', 'alergia a {0}'),
    (r'\b(?:es |soy )?celiac[oa]s?\b', 'celiaquía (sin gluten)'),
    (r'\b(?:es |soy )?vegetarian[oa]s?\b', 'vegetariano'),
    (r'\bno (?:come|puede comer|consume) ([a-zñ]+)', 'no consume {0}'),
]
INTENCIONES = [
    ('CANCELAR', r'\b(cancel[a-z]*|anul[a-z]*)\b'),
    ('MODIFICAR', r'\b(cambi[a-z]*|quit[a-z]*|en vez de|en lugar de|mejor no)\b'),
    ('CONSULTAR_MENU', r'\b(que (?:hay|tienen|tiene)|menu|carta|recomienda)\b'),
]


def _limpiar_mod(m: str) -> str:
    return re.sub(r'\s+', ' ', m).strip()


class Catalogo:
    """Diccionario del menú: nombre y sinónimos de cada producto, en forma normalizada y en singular."""

    def __init__(self, productos):
        self.productos = {p['id']: p for p in productos}
        self.alias = []   # (tokens_raiz, producto_id, es_nombre)
        for p in productos:
            for i, nombre in enumerate([p['nombre']] + list(p.get('sinonimos') or [])):
                toks = [raiz(t) for t in normalizar(nombre).split() if t not in PALABRAS_VACIAS]
                if toks:
                    self.alias.append((toks, p['id'], i == 0))
        self.alias.sort(key=lambda a: -len(a[0]))   # coincidencia más larga primero

    def buscar(self, toks, inicio):
        """Devuelve (producto_id, fin, confianza) para la mejor coincidencia que empieza en `inicio`."""
        mejor = None
        for alias, pid, es_nombre in self.alias:
            n = len(alias)
            ventana = [t for t in toks[inicio:inicio + n + 2] if t not in PALABRAS_VACIAS][:n]
            if len(ventana) < n:
                continue
            sims = [1.0 if a == b else SequenceMatcher(None, a, b).ratio() for a, b in zip(alias, ventana)]
            if min(sims) < 0.8:
                continue
            conf = (0.95 if all(s == 1.0 for s in sims) else 0.9 * (sum(sims) / n))
            # posición final real dentro de toks (saltando palabras vacías)
            fin, vistos = inicio, 0
            while fin < len(toks) and vistos < n:
                if toks[fin] not in PALABRAS_VACIAS:
                    vistos += 1
                fin += 1
            cand = (pid, fin, conf, n)
            if mejor is None or (n, conf) > (mejor[3], mejor[2]):
                mejor = cand
        return mejor[:3] if mejor else None

    def coincidencia_parcial(self, toks):
        """Si la cláusula menciona solo la primera palabra de un producto (ej. «cuy»), propone el más probable con baja confianza."""
        for t in toks:
            cands = [pid for alias, pid, _ in self.alias if alias[0] == t]
            if cands:
                pid = cands[0]
                return pid, 0.6 if len(set(cands)) > 1 else 0.75
        return None


def _extraer_restricciones(texto):
    restricciones = []
    for patron, plantilla in PATRONES_RESTRICCION:
        for m in re.finditer(patron, texto):
            restricciones.append(plantilla.format(*[g.strip() for g in m.groups()]) if m.groups() else plantilla)
        texto = re.sub(patron, ' , ', texto)
    texto = re.sub(r'\b(el cliente|la cliente|la senora|el senor)\b', ' ', texto)
    return restricciones, texto


def _modificaciones(texto):
    mods = []
    for p in PATRONES_MODIFICACION:
        for m in re.finditer(p, texto):
            mods.append(_limpiar_mod(m.group(0)))
        texto = re.sub(p, ' ', texto)
    # quita duplicados conservando el orden
    vistos, unicos = set(), []
    for m in mods:
        if m not in vistos:
            vistos.add(m); unicos.append(m)
    return unicos, texto


def _clausulas(texto):
    actual, salida = [], []
    for t in texto.split():
        if t in SEPARADORES:
            if actual:
                salida.append(' '.join(actual)); actual = []
        else:
            actual.append(t)
    if actual:
        salida.append(' '.join(actual))
    return salida


def interpretar(frase: str, productos: list) -> dict:
    t0 = time.perf_counter()
    cat = Catalogo([p for p in productos])
    texto = normalizar(frase)
    intencion = 'OTRO'
    for nombre, patron in INTENCIONES:
        if re.search(patron, texto):
            intencion = nombre
            break
    restricciones, texto = _extraer_restricciones(texto)
    items, sin_asignar, no_reconocidos = [], [], []

    for clausula in _clausulas(texto):
        mods, resto = _modificaciones(clausula)
        toks_orig = resto.split()
        toks = [raiz(x) for x in toks_orig]
        cant, encontrado, i = None, False, 0
        while i < len(toks):
            c = cantidad(toks_orig[i])
            if c is not None:
                cant = c; i += 1; continue
            r = cat.buscar(toks, i)
            if r:
                pid, fin, conf = r
                items.append(_item(cat, pid, cant or 1, mods, conf, ' '.join(toks_orig[max(0, i - 1):fin])))
                mods, cant, encontrado, i = [], None, True, fin
                continue
            i += 1
        if encontrado:
            continue
        palabras = [x for x in toks_orig if cantidad(x) is None and x not in PALABRAS_VACIAS]
        if cant is not None and not palabras and mods and items:
            # «dos hamburguesas, una sin cebolla»: separa la línea anterior
            prev = items[-1]
            if prev['cantidad'] > cant:
                prev['cantidad'] -= cant
                nuevo = dict(prev, cantidad=cant, modificaciones=mods, texto=clausula)
                items.append(nuevo)
            else:
                prev['modificaciones'] += mods
            continue
        if palabras and not mods:
            parcial = cat.coincidencia_parcial([raiz(x) for x in palabras])
            if parcial:
                pid, conf = parcial
                items.append(_item(cat, pid, cant or 1, [], conf, clausula))
            elif cant is not None:
                no_reconocidos.append(' '.join(palabras))
            continue
        if mods:
            if len(items) == 1 and not palabras:
                items[0]['modificaciones'] += mods
            elif palabras and cant is not None:
                no_reconocidos.append(' '.join(palabras))
            else:
                sin_asignar += mods

    if items and intencion == 'OTRO':
        intencion = 'PEDIR'
    for it in items:
        it['verificar'] = it['confianza'] < UMBRAL_CONFIANZA or not it.pop('_disponible', True)
    mensaje = None
    if not items and intencion in ('OTRO', 'PEDIR'):
        mensaje = 'No se identificó ningún producto. Reformule o registre manualmente'
    return {
        'intencion': intencion, 'items': items, 'restricciones': restricciones,
        'modificacionesSinAsignar': sin_asignar, 'noReconocidos': no_reconocidos, 'mensaje': mensaje,
        'modelo': 'reglas-v1', 'tiempoMs': round((time.perf_counter() - t0) * 1000, 2),
    }


def _item(cat, pid, cant, mods, conf, texto):
    p = cat.productos[pid]
    return {'productoId': pid, 'producto': p['nombre'], 'cantidad': cant, 'modificaciones': list(mods),
            'confianza': round(conf, 2), 'verificar': False, 'texto': texto.strip(),
            '_disponible': p.get('disponible', True)}
