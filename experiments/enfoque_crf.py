"""Enfoque 2: campos aleatorios condicionales (Lafferty et al., 2001) con sklearn-crfsuite. Entrene con `python -m experiments.enfoque_crf`."""
import json, os, pickle
from app.pipeline.interpretador_reglas import Catalogo, interpretar as por_reglas
from experiments.bio import a_bio

RUTA = 'modelos/crf/crf.pkl'


def rasgos(toks, i):
    t = toks[i]
    f = {'w': t, 'suf3': t[-3:], 'es_num': t.isdigit(), 'largo': len(t)}
    f.update({'w-1': toks[i - 1] if i else '<s>', 'w+1': toks[i + 1] if i + 1 < len(toks) else '</s>'})
    return f


class InterpretadorCRF:
    nombre = 'crf'
    ruta = RUTA

    def __init__(self):
        import sklearn_crfsuite  # noqa: F401  (falla si no está instalado)
        with open(RUTA, 'rb') as f:
            self.crf = pickle.load(f)

    def interpretar(self, frase, catalogo):
        # PENDIENTE (Juan): reconstruir ítems a partir de las etiquetas BIO; por ahora valida con reglas las entidades marcadas.
        return por_reglas(frase, catalogo) | {'modelo': self.nombre}


def entrenar(corpus='data/corpus/semilla.jsonl', menu='data/menu_ejemplo.json'):
    import sklearn_crfsuite
    m = json.load(open(menu, encoding='utf8'))
    X, y = [], []
    for linea in open(corpus, encoding='utf8'):
        toks, etq = a_bio(json.loads(linea), m)
        X.append([rasgos(toks, i) for i in range(len(toks))]); y.append(etq)
    crf = sklearn_crfsuite.CRF(algorithm='lbfgs', c1=0.1, c2=0.1, max_iterations=100)
    crf.fit(X, y)
    os.makedirs(os.path.dirname(RUTA), exist_ok=True)
    with open(RUTA, 'wb') as f:
        pickle.dump(crf, f)
    print('CRF guardado en', RUTA)


if __name__ == '__main__':
    entrenar()
