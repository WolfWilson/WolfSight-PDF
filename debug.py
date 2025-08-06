import inspect
import pyhanko
from pyhanko.sign import signers

print("--- Diagnóstico de la Instalación de PyHanko ---")

try:
    # 1. Imprimir la versión de pyhanko que Python está usando
    print(f"Versión de pyhanko detectada: {pyhanko.__version__}")

    # 2. Inspeccionar la función sign_pdf de pyhanko.sign.signers
    #    Esto nos dirá exactamente qué argumentos y keyword arguments espera
    print("\nInspeccionando 'pyhanko.sign.signers.sign_pdf':")
    spec = inspect.getfullargspec(signers.sign_pdf)
    print(f"    - Argumentos posicionales: {spec.args}")
    print(f"    - Argumentos de solo-palabra-clave (kwargs): {spec.kwonlyargs}")

except Exception as e:
    print(f"\nOcurrió un error durante el diagnóstico: {e}")

print("\n--- Fin del Diagnóstico ---")