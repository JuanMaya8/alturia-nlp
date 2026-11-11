# Comparación de enfoques NLP

Corpus: `data/corpus/semilla.jsonl` (40 frases) · Fecha: 2026-11-08

| Enfoque | Precisión | Recall | F1 | Exactitud intención | Tiempo p95 (ms) | Memoria pico (MB) | Tamaño (MB) | Cumple F1 ≥ 0,85 |
|---|---|---|---|---|---|---|---|---|
| reglas-v1 | 1.000 | 0.984 | 0.992 | 1.000 | 7.72 | 0.10 | 0.0 | Sí |

**Advertencia:** si el corpus es la semilla escrita por el equipo, el resultado es optimista; la evaluación válida usa el conjunto de prueba reservado (15 %) de frases reales del restaurante.

Memoria medida con tracemalloc (solo objetos de Python). Para la memoria total del proceso use psutil en el computador de la caja.
