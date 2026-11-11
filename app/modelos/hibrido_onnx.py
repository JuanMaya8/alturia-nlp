"""
Enfoque híbrido (Yang et al., 2025): un modelo de etiquetado de entidades exportado a ONNX marca producto, cantidad y
modificación, y las reglas lo validan contra el menú. Si el modelo no está instalado o falla, se usan solo las reglas.

PENDIENTE (Juan): completar `_etiquetar` cuando exista `modelos/seleccionado/` (ver experiments/exportar_onnx.py).
"""
import os
from app.pipeline.interpretador_reglas import interpretar as por_reglas

DIR_MODELO = os.environ.get('ALTURIA_DIR_MODELO', 'modelos/seleccionado')


class InterpretadorHibrido:
    nombre = 'hibrido-onnx'

    def __init__(self):
        self.sesion = None
        ruta = os.path.join(DIR_MODELO, 'model.onnx')
        if os.path.exists(ruta):
            try:
                import onnxruntime as ort   # solo se importa si hay modelo
                self.sesion = ort.InferenceSession(ruta, providers=['CPUExecutionProvider'])
            except Exception:
                self.sesion = None

    def interpretar(self, frase: str, catalogo: list[dict]) -> dict:
        base = por_reglas(frase, catalogo)
        if self.sesion is None:
            base['modelo'] = 'reglas-v1 (respaldo: modelo no instalado)'
            return base
        # TODO (Juan): tokenizar, ejecutar self.sesion, convertir etiquetas BIO en entidades y combinarlas con `base`.
        base['modelo'] = self.nombre
        return base
