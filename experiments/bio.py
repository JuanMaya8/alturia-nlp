"""Convierte la anotación por ítems del corpus en etiquetas BIO por palabra (PROD, CANT, MOD) para CRF y Transformers."""
from app.pipeline.preprocesador import normalizar, raiz, cantidad


def a_bio(ejemplo: dict, menu: list[dict]) -> tuple[list[str], list[str]]:
    toks = normalizar(ejemplo['frase']).split()
    etiquetas = ['O'] * len(toks)
    alias = {}
    for p in menu:
        for n in [p['nombre']] + p.get('sinonimos', []):
            alias[tuple(raiz(t) for t in normalizar(n).split())] = p['nombre']
    raices = [raiz(t) for t in toks]
    for i in range(len(toks)):
        if cantidad(toks[i]) is not None:
            etiquetas[i] = 'B-CANT'
    for clave in sorted(alias, key=len, reverse=True):
        n = len(clave)
        for i in range(len(toks) - n + 1):
            if tuple(raices[i:i + n]) == clave and all(e == 'O' for e in etiquetas[i:i + n]):
                etiquetas[i] = 'B-PROD'
                for j in range(i + 1, i + n):
                    etiquetas[j] = 'I-PROD'
    for i, t in enumerate(toks):
        if t in ('sin', 'bien', 'extra', 'doble', 'poco', 'termino') and i + 1 < len(toks) and etiquetas[i] == 'O':
            etiquetas[i] = 'B-MOD'
            if etiquetas[i + 1] == 'O':
                etiquetas[i + 1] = 'I-MOD'
    return toks, etiquetas
