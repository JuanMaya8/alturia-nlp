"""
Exporta el modelo Transformer elegido a ONNX y lo cuantiza a 8 bits (Jacob et al., 2018) para ejecutarlo en la CPU de la caja.
Uso: python -m experiments.exportar_onnx --modelo modelos/distilbeto --salida modelos/seleccionado
"""
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--modelo', required=True)
    ap.add_argument('--salida', default='modelos/seleccionado')
    a = ap.parse_args()
    from optimum.onnxruntime import ORTModelForTokenClassification, ORTQuantizer
    from optimum.onnxruntime.configuration import AutoQuantizationConfig
    modelo = ORTModelForTokenClassification.from_pretrained(a.modelo, export=True)
    modelo.save_pretrained(a.salida)
    cuantizador = ORTQuantizer.from_pretrained(a.salida)
    cuantizador.quantize(save_dir=a.salida, quantization_config=AutoQuantizationConfig.avx2(is_static=False, per_channel=False))
    print('Modelo ONNX cuantizado en', a.salida, '— instale ese directorio en el computador de la caja y use ALTURIA_MODELO=hibrido')


if __name__ == '__main__':
    main()
