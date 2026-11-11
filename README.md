# alturia-nlp

Servicio y laboratorio del modelo **NLP (Procesamiento de Lenguaje Natural)** del Sistema de Gestión de Pedidos Alturia
(trabajo de grado, Ingeniería de Software, UCC Pasto). Corresponde al **objetivo específico 3** y al componente investigativo
del proyecto: construir el modelo comparando enfoques, modelos y algoritmos para que **funcione sin conexión** en el computador
de la caja y no se caiga.

- **Autores:** Juan David Maya Benavides (responsable del modelo) y Jack Anderson Limas Solarte (corpus y pruebas con meseros)
- **Repositorios del sistema:** `alturia-backend` · `alturia-frontend` · `alturia-nlp` (este)

## 1. Qué contiene
| Carpeta | Para qué |
|---|---|
| `app/` | Servicio FastAPI que corre en el computador de la caja (`POST /interpretar`). Pasos del diagrama C4 del servicio NLP: preprocesador, intención, entidades, resolución contra el menú y confianza. |
| `app/pipeline/` | Motor de **reglas y diccionario del menú** (línea base y respaldo del enfoque híbrido). Python puro, sin dependencias. |
| `app/modelos/` | Adaptadores intercambiables: `reglas` (por defecto) e `hibrido` (modelo ONNX + reglas; si el modelo falla, usa reglas). |
| `experiments/` | Comparación de enfoques: métricas, CRF, BETO/DistilBETO/ALBETO, exportación ONNX cuantizada. |
| `data/` | Menú de ejemplo y corpus anotado (semilla de 40 frases; la meta es ≥ 1.000 frases reales). |
| `scripts/` | Validación y división del corpus (70/15/15). |
| `reportes/` | Resultados de cada comparación (evidencia para el capítulo de resultados). |
| `tests/` | Escenarios de las HU-22 a HU-24 y validación del corpus. |

## 2. Contrato del servicio
`POST /interpretar`
```json
{ "frase": "dos cuyes medianos, uno sin ají, y una cola",
  "catalogo": [{"id": 1, "nombre": "Cuy asado mediano", "sinonimos": ["cuy mediano"], "disponible": true}, ...] }
```
Respuesta:
```json
{ "intencion": "PEDIR",
  "items": [{"productoId": 1, "producto": "Cuy asado mediano", "cantidad": 1, "modificaciones": [], "confianza": 0.95, "verificar": false, "texto": "..."},
            {"productoId": 1, "producto": "Cuy asado mediano", "cantidad": 1, "modificaciones": ["sin aji"], "confianza": 0.95, "verificar": false, "texto": "..."},
            {"productoId": 8, "producto": "Gaseosa", "cantidad": 1, "modificaciones": [], "confianza": 0.95, "verificar": false, "texto": "..."}],
  "restricciones": [], "modificacionesSinAsignar": [], "noReconocidos": [], "mensaje": null, "modelo": "reglas-v1", "tiempoMs": 3.1 }
```
- `verificar = true` cuando la confianza es menor a **0,80** o el producto está agotado: el mesero debe aceptarlo o corregirlo (HU-24).
- `modificacionesSinAsignar`: indicaciones como «sin picante» que no se sabe a qué producto pertenecen (HU-23).
- El servidor local espera máximo **3 s**; si no hay respuesta, el mesero pasa al registro manual (RNF-20).

## 3. Ejecutar
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000      # documentación interactiva en http://127.0.0.1:8000/docs
python -m unittest discover -s tests -v                 # 18 pruebas
```
Para usar el modelo entrenado: copie el directorio exportado a `modelos/seleccionado/` y arranque con `ALTURIA_MODELO=hibrido`.

## 4. Metodología de la comparación (sección 3.4.4 del documento)
1. **Corpus**: frases reales del restaurante, anotadas según [docs/guia_anotacion.md](docs/guia_anotacion.md); división 70/15/15 (`scripts/dividir_corpus.py`).
2. **Enfoques**: (1) reglas y diccionario del menú · (2) CRF · (3) spaCy · (4) BETO · (5) ALBETO/DistilBETO · (6) cuantización a 8 bits + ONNX.
3. **Criterios**: F1 de entidades ≥ 0,85 · exactitud de intención ≥ 0,85 · tiempo p95 ≤ 2 s en la CPU de la caja · memoria ≤ 1 GB · tamaño y esfuerzo de reentrenamiento.
4. **Selección**: el enfoque que cumpla con menor consumo de recursos, integrado de forma **híbrida** con las reglas (respaldo).

```bash
pip install -r requirements-experimentos.txt
python -m experiments.enfoque_crf                                                          # entrena CRF
python -m experiments.enfoque_transformer --base dccuchile/bert-base-spanish-wwm-cased --salida modelos/beto
python -m experiments.enfoque_transformer --base dccuchile/distilbert-base-spanish-uncased --salida modelos/distilbeto
python -m experiments.comparar --corpus data/corpus/prueba.jsonl --salida reportes/comparacion.md
python -m experiments.exportar_onnx --modelo modelos/distilbeto --salida modelos/seleccionado
```

### Resultado inicial (línea base, `reportes/comparacion_inicial.md`)
| Enfoque | F1 | Exactitud intención | Tiempo p95 |
|---|---|---|---|
| reglas-v1 | 0,992 | 1,000 | < 10 ms |

> Este valor es **optimista**: el corpus semilla lo escribió el equipo mientras construía las reglas. La evaluación válida para el
> documento se hará sobre el conjunto de prueba reservado de frases reales del restaurante.

## 5. Cómo trabajamos
Ramas `main` / `develop` / `feature/<persona>/<tema>`, commits pequeños con Conventional Commits en español y PR revisado por el otro
integrante. Propietarios por carpeta en [CONTRIBUTING.md](CONTRIBUTING.md). Pendientes en [docs/BACKLOG.md](docs/BACKLOG.md).
