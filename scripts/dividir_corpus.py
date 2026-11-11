"""Divide el corpus en entrenamiento (70 %), validación (15 %) y prueba (15 %) con semilla fija. La prueba no se toca hasta la evaluación final."""
import json, random, sys

ruta = sys.argv[1] if len(sys.argv) > 1 else 'data/corpus/restaurante.jsonl'
filas = [l for l in open(ruta, encoding='utf8') if l.strip()]
random.Random(42).shuffle(filas)
n = len(filas)
cortes = {'entrenamiento': filas[:int(n * .7)], 'validacion': filas[int(n * .7):int(n * .85)], 'prueba': filas[int(n * .85):]}
for nombre, parte in cortes.items():
    with open(f'data/corpus/{nombre}.jsonl', 'w', encoding='utf8') as f:
        f.writelines(parte)
    print(nombre, len(parte))
