"""
Enfoques 4 y 5: BETO, DistilBETO o ALBETO afinados para etiquetado de entidades (Cañete et al., 2020; 2022).
Entrenamiento:  python -m experiments.enfoque_transformer --base dccuchile/bert-base-spanish-wwm-cased --salida modelos/beto
                python -m experiments.enfoque_transformer --base dccuchile/distilbert-base-spanish-uncased --salida modelos/distilbeto
                python -m experiments.enfoque_transformer --base dccuchile/albert-tiny-spanish --salida modelos/albeto
(Verifique los nombres exactos de los modelos en https://huggingface.co/dccuchile antes de entrenar.)
"""
import argparse, json
from experiments.bio import a_bio
from app.pipeline.interpretador_reglas import interpretar as por_reglas

ETIQUETAS = ['O', 'B-PROD', 'I-PROD', 'B-CANT', 'B-MOD', 'I-MOD']


class InterpretadorTransformer:
    def __init__(self, nombre):
        from transformers import pipeline
        self.nombre = nombre
        self.ruta = f'modelos/{nombre}'
        self.ner = pipeline('token-classification', model=self.ruta, aggregation_strategy='simple', device=-1)

    def interpretar(self, frase, catalogo):
        entidades = self.ner(frase)
        r = por_reglas(frase, catalogo)          # las reglas resuelven contra el menú (enfoque híbrido)
        r['modelo'] = self.nombre
        r['entidades'] = [{'tipo': e['entity_group'], 'texto': e['word'], 'score': float(e['score'])} for e in entidades]
        # PENDIENTE (Juan): usar `entidades` para construir los ítems antes que las reglas y medir la diferencia.
        return r


def entrenar(base, salida, corpus, menu, epocas):
    from datasets import Dataset
    from transformers import (AutoTokenizer, AutoModelForTokenClassification, DataCollatorForTokenClassification,
                              Trainer, TrainingArguments)
    m = json.load(open(menu, encoding='utf8'))
    filas = [a_bio(json.loads(l), m) for l in open(corpus, encoding='utf8') if l.strip()]
    tok = AutoTokenizer.from_pretrained(base)

    def codificar(ej):
        enc = tok(ej['toks'], is_split_into_words=True, truncation=True)
        ids, prev, etq = enc.word_ids(), None, []
        for w in ids:
            etq.append(-100 if w is None or w == prev else ETIQUETAS.index(ej['etq'][w]))
            prev = w
        enc['labels'] = etq
        return enc

    ds = Dataset.from_list([{'toks': t, 'etq': e} for t, e in filas]).map(codificar, remove_columns=['toks', 'etq'])
    partes = ds.train_test_split(test_size=0.15, seed=42)
    modelo = AutoModelForTokenClassification.from_pretrained(base, num_labels=len(ETIQUETAS),
                                                             id2label=dict(enumerate(ETIQUETAS)), label2id={e: i for i, e in enumerate(ETIQUETAS)})
    args = TrainingArguments(salida, num_train_epochs=epocas, per_device_train_batch_size=16, learning_rate=5e-5,
                             eval_strategy='epoch', save_strategy='no', logging_steps=10, report_to=[])
    Trainer(model=modelo, args=args, train_dataset=partes['train'], eval_dataset=partes['test'],
            data_collator=DataCollatorForTokenClassification(tok)).train()
    modelo.save_pretrained(salida); tok.save_pretrained(salida)
    print('Modelo guardado en', salida)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True); ap.add_argument('--salida', required=True)
    ap.add_argument('--corpus', default='data/corpus/semilla.jsonl'); ap.add_argument('--menu', default='data/menu_ejemplo.json')
    ap.add_argument('--epocas', type=int, default=8)
    a = ap.parse_args()
    entrenar(a.base, a.salida, a.corpus, a.menu, a.epocas)
