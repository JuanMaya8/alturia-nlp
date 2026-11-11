# Guía de anotación del corpus de pedidos

Objetivo: reunir **al menos 1.000 frases reales** de pedidos del Restaurante Alturia (sin datos personales) para entrenar y evaluar los modelos.

## Formato (una línea JSON por frase, archivo `data/corpus/restaurante.jsonl`)
```json
{"frase": "dos cuyes medianos, uno sin ají, y una cola", "intencion": "PEDIR",
 "items": [{"producto": "Cuy asado mediano", "cantidad": 1, "modificaciones": []},
           {"producto": "Cuy asado mediano", "cantidad": 1, "modificaciones": ["sin aji"]},
           {"producto": "Gaseosa", "cantidad": 1, "modificaciones": []}],
 "restricciones": [], "fuente": "mesero-2026-11-10"}
```

## Reglas
1. **Intención**: PEDIR, MODIFICAR, CANCELAR, CONSULTAR_MENU u OTRO.
2. **Producto**: el nombre exacto del menú, no como lo dijo el cliente («cola» → «Gaseosa»).
3. **Cantidad**: número entero; «un par» = 2, «media docena» = 6. Si no se dice, 1.
4. **Modificaciones**: en minúsculas y sin tildes («sin aji», «bien asado»), asociadas al producto al que se refieren.
   Si la frase separa unidades («dos hamburguesas, una sin cebolla»), se anotan como dos ítems.
5. **Restricciones**: alergias o dietas del comensal («alergia a mani», «celiaquía (sin gluten)»).
6. No anote nombres, teléfonos ni datos del cliente.
7. Las dudas se discuten entre los dos integrantes y la decisión se agrega a esta guía.

## Recolección
- Durante el servicio, el mesero escribe o dicta en la tablet; el servidor local guarda la frase y su versión confirmada (`EjemploNlp`).
- Exportación desde el backend (pendiente, Juan) y anotación/revisión (Jack).
- Al llegar a 1.000 frases: `python scripts/dividir_corpus.py data/corpus/restaurante.jsonl`.
