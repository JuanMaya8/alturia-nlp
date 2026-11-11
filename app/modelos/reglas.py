from app.pipeline.interpretador_reglas import interpretar


class InterpretadorReglas:
    """Enfoque 1: reglas y diccionario del menú (línea base). También es el respaldo del enfoque híbrido."""
    nombre = 'reglas-v1'

    def interpretar(self, frase: str, catalogo: list[dict]) -> dict:
        return interpretar(frase, catalogo)
