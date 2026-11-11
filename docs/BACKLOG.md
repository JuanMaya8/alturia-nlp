# Trabajo pendiente del NLP (objetivo específico 3)

## Jack Anderson Limas Solarte (corpus y validación con meseros)
1. Recolectar frases reales en el restaurante (meta ≥ 1.000), en lotes de 50 por commit: `data(corpus): agrega lote N de frases reales`.
2. Anotar cada lote según la guía y ejecutar `python scripts/validar_corpus.py`.
3. Reemplazar `data/menu_ejemplo.json` por el menú real (nombres, sinónimos usados por los clientes, disponibilidad).
4. Dividir el corpus (`scripts/dividir_corpus.py`) y no tocar `prueba.jsonl` después.
5. Prueba con meseros: 20 pedidos dictados y escritos; registrar en `reportes/prueba_meseros.md` aciertos, correcciones y tiempo.

## Juan David Maya Benavides (modelos y servicio)
1. Instalar `requirements-experimentos.txt` y entrenar CRF, spaCy, BETO, DistilBETO y ALBETO con `entrenamiento.jsonl`.
2. Completar la reconstrucción de ítems desde etiquetas BIO en `enfoque_crf.py` y `enfoque_transformer.py`.
3. Ejecutar `experiments.comparar` sobre `prueba.jsonl` en el **computador de la caja** y guardar `reportes/comparacion.md`.
4. Exportar el elegido a ONNX cuantizado y completar `app/modelos/hibrido_onnx.py`.
5. Medir memoria total con psutil (RNF-19 ≤ 1 GB) y documentar la selección para la sección 4.2 del documento.
6. Instalar el servicio como tarea de inicio de Windows en el computador de la caja.
