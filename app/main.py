"""
Servicio NLP del Sistema Alturia (FastAPI). Se ejecuta en el computador de la caja y funciona sin internet.
El servidor local (alturia-backend) lo llama con la frase y el catálogo vigente y espera máximo 3 s.
"""
import os
import time
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.modelos.reglas import InterpretadorReglas
from app.modelos.hibrido_onnx import InterpretadorHibrido

MODELO = os.environ.get('ALTURIA_MODELO', 'reglas')
interpretador = InterpretadorHibrido() if MODELO == 'hibrido' else InterpretadorReglas()

app = FastAPI(title='Alturia NLP', version='0.1.0',
              description='Interpretación local de pedidos en lenguaje natural (HU-22 a HU-24)')


class ProductoCatalogo(BaseModel):
    id: int
    nombre: str
    sinonimos: list[str] = Field(default_factory=list)
    disponible: bool = True


class Peticion(BaseModel):
    frase: str = Field(min_length=1, max_length=500)
    catalogo: list[ProductoCatalogo]


@app.get('/salud')
def salud():
    return {'estado': 'ok', 'modelo': interpretador.nombre}


@app.post('/interpretar')
def interpretar(p: Peticion):
    t0 = time.perf_counter()
    r = interpretador.interpretar(p.frase, [c.model_dump() for c in p.catalogo])
    r['tiempoMs'] = round((time.perf_counter() - t0) * 1000, 2)
    return r
