"""Interfaz común de los enfoques comparados en la investigación (reglas, CRF, spaCy, BETO, ALBETO/DistilBETO)."""
from typing import Protocol


class Interpretador(Protocol):
    nombre: str

    def interpretar(self, frase: str, catalogo: list[dict]) -> dict:
        """Devuelve la propuesta en el formato del contrato (ver README, sección «Contrato»)."""
        ...
