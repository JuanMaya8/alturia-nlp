"""Métricas de la comparación: F1 de entidades (producto, cantidad, modificación) y exactitud de la intención."""
from collections import Counter


def entidades(resultado: dict) -> Counter:
    """Convierte una propuesta (o la anotación de referencia) en un multiconjunto de entidades comparables."""
    c = Counter()
    for it in resultado.get('items', []):
        prod = it.get('producto')
        if not prod:
            continue
        c[('PRODUCTO', prod)] += 1
        c[('CANTIDAD', prod, it.get('cantidad', 1))] += 1
        for m in it.get('modificaciones', []):
            c[('MODIFICACION', prod, m.strip().lower())] += 1
    for r in resultado.get('restricciones', []):
        c[('RESTRICCION', r.strip().lower())] += 1
    return c


def prf(pred: Counter, gold: Counter):
    tp = sum((pred & gold).values())
    p = tp / max(1, sum(pred.values()))
    r = tp / max(1, sum(gold.values()))
    f = 0.0 if p + r == 0 else 2 * p * r / (p + r)
    return tp, sum(pred.values()), sum(gold.values()), p, r, f


def evaluar(predicciones: list[dict], referencias: list[dict]) -> dict:
    tp = np_ = ng = 0
    aciertos_intencion = 0
    for pr, gd in zip(predicciones, referencias):
        a, b, c, *_ = prf(entidades(pr), entidades(gd))
        tp += a; np_ += b; ng += c
        aciertos_intencion += pr.get('intencion') == gd.get('intencion')
    p = tp / max(1, np_)
    r = tp / max(1, ng)
    return {'precision': p, 'recall': r, 'f1': 0.0 if p + r == 0 else 2 * p * r / (p + r),
            'exactitud_intencion': aciertos_intencion / max(1, len(referencias)), 'n': len(referencias)}
