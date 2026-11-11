"""
Compara los enfoques candidatos con los criterios de la metodología (Tabla «Criterios para comparar y seleccionar el modelo NLP»):
F1 ≥ 0,85 · exactitud de intención ≥ 0,85 · tiempo p95 ≤ 2 s en la CPU de la caja · memoria ≤ 1 GB · tamaño en disco.

Uso:  python -m experiments.comparar --corpus data/corpus/semilla.jsonl --menu data/menu_ejemplo.json
Genera reportes/comparacion.md. Cada enfoque se incluye solo si su dependencia está instalada.
"""
import argparse, json, os, statistics, time, tracemalloc, datetime
from experiments.metricas import evaluar, entidades


def cargar_enfoques():
    enfoques = []
    from app.modelos.reglas import InterpretadorReglas
    enfoques.append(InterpretadorReglas())
    try:
        from experiments.enfoque_crf import InterpretadorCRF
        enfoques.append(InterpretadorCRF())
    except Exception as e:
        print('CRF no disponible:', e)
    try:
        from experiments.enfoque_transformer import InterpretadorTransformer
        for nombre in ('beto', 'distilbeto', 'albeto'):
            if os.path.isdir(f'modelos/{nombre}'):
                enfoques.append(InterpretadorTransformer(nombre))
    except Exception as e:
        print('Transformers no disponible:', e)
    return enfoques


def tamano_mb(ruta):
    if not os.path.exists(ruta):
        return 0.0
    if os.path.isfile(ruta):
        return os.path.getsize(ruta) / 1e6
    return sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(ruta) for f in fs) / 1e6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', default='data/corpus/semilla.jsonl')
    ap.add_argument('--menu', default='data/menu_ejemplo.json')
    ap.add_argument('--salida', default='reportes/comparacion.md')
    a = ap.parse_args()
    corpus = [json.loads(l) for l in open(a.corpus, encoding='utf8') if l.strip()]
    menu = json.load(open(a.menu, encoding='utf8'))
    filas = []
    for enf in cargar_enfoques():
        tiempos, preds = [], []
        tracemalloc.start()
        for ej in corpus:
            t0 = time.perf_counter()
            preds.append(enf.interpretar(ej['frase'], menu))
            tiempos.append((time.perf_counter() - t0) * 1000)
        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        m = evaluar(preds, corpus)
        p95 = statistics.quantiles(tiempos, n=20)[18] if len(tiempos) >= 20 else max(tiempos)
        filas.append((enf.nombre, m, p95, pico / 1e6, tamano_mb(getattr(enf, 'ruta', ''))))
        errores = [(ej['frase'], p) for ej, p in zip(corpus, preds) if entidades(p) != entidades(ej) or p.get('intencion') != ej.get('intencion')]
        with open(a.salida.replace('.md', f'_errores_{enf.nombre}.jsonl'), 'w', encoding='utf8') as f:
            for frase, p in errores:
                f.write(json.dumps({'frase': frase, 'prediccion': p}, ensure_ascii=False) + '\n')
    os.makedirs(os.path.dirname(a.salida), exist_ok=True)
    with open(a.salida, 'w', encoding='utf8') as f:
        f.write(f'# Comparación de enfoques NLP\n\nCorpus: `{a.corpus}` ({len(corpus)} frases) · Fecha: {datetime.date.today()}\n\n')
        f.write('| Enfoque | Precisión | Recall | F1 | Exactitud intención | Tiempo p95 (ms) | Memoria pico (MB) | Tamaño (MB) | Cumple F1 ≥ 0,85 |\n|---|---|---|---|---|---|---|---|---|\n')
        for nombre, m, p95, mem, tam in filas:
            f.write(f"| {nombre} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['exactitud_intencion']:.3f} | "
                    f"{p95:.2f} | {mem:.2f} | {tam:.1f} | {'Sí' if m['f1'] >= 0.85 else 'No'} |\n")
        f.write('\n**Advertencia:** si el corpus es la semilla escrita por el equipo, el resultado es optimista; la evaluación válida usa el conjunto de prueba reservado (15 %) de frases reales del restaurante.\n')
        f.write('\nMemoria medida con tracemalloc (solo objetos de Python). Para la memoria total del proceso use psutil en el computador de la caja.\n')
    print(open(a.salida, encoding='utf8').read())


if __name__ == '__main__':
    main()
