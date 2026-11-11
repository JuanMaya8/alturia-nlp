"""Revisa un archivo del corpus y muestra estadísticas: frases, intenciones, productos y duplicados. Uso: python scripts/validar_corpus.py data/corpus/semilla.jsonl"""
import json, sys
from collections import Counter

ruta = sys.argv[1] if len(sys.argv) > 1 else 'data/corpus/semilla.jsonl'
filas = [json.loads(l) for l in open(ruta, encoding='utf8') if l.strip()]
frases = Counter(f['frase'].lower().strip() for f in filas)
print(f'Frases: {len(filas)}')
print('Intenciones:', dict(Counter(f['intencion'] for f in filas)))
print('Productos:', dict(Counter(i['producto'] for f in filas for i in f['items'])))
print('Con modificaciones:', sum(1 for f in filas if any(i['modificaciones'] for i in f['items'])))
print('Con restricciones:', sum(1 for f in filas if f['restricciones']))
dup = [f for f, c in frases.items() if c > 1]
print('Duplicadas:', dup or 'ninguna')
