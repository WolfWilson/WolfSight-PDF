import logging
from pathlib import Path
from pyhanko.sign import simple # Usaremos la API de alto nivel 'simple'
from pyhanko.sign.signers import SimpleSigner
from pyhanko.sign.signers.pdf_cms import PdfSignatureMetadata

# --- Configuración ---
# Asegúrate de que estas rutas sean correctas
PFX_FILE = Path("tests/credencials/certificado_prueba.pfx")
PFX_PASS = "123456"
INPUT_PDF = Path("tests/docs/documento_de_prueba.pdf")
OUTPUT_DIR = Path("output")
OUTPUT_PDF = OUTPUT_DIR / "minimal_signed.pdf"

# --- Lógica de la prueba ---
def run_minimal_test():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    if not all([PFX_FILE.exists(), INPUT_PDF.exists()]):
        logging.error("No se encontró el archivo PFX o el PDF de entrada.")
        return

    logging.info("Iniciando prueba de firma mínima...")
    try:
        # 1. Cargar el firmante (signer)
        signer = SimpleSigner.load_pkcs12(
            pfx_file=PFX_FILE,
            passphrase=PFX_PASS.encode('utf-8')
        )
        logging.info("Firmante cargado correctamente.")

        # 2. Preparar los metadatos
        meta = PdfSignatureMetadata(
            reason="Prueba de firma mínima",
            location="Resistencia, Chaco"
        )

        # 3. Asegurar que el directorio de salida exista
        OUTPUT_DIR.mkdir(exist_ok=True)

        # 4. Firmar el PDF usando la API simple
        #    Esta es la forma más directa que ofrece pyhanko.
        #    Toma los archivos de entrada/salida y el firmante.
        with open(INPUT_PDF, 'rb') as inf, open(OUTPUT_PDF, 'wb') as outf:
            simple.sign_pdf(
                inf,
                outf,
                signer=signer,
                sig_meta=meta
            )

        logging.info(f"✅ ¡ÉXITO! PDF firmado y guardado en: {OUTPUT_PDF}")

    except Exception:
        logging.error("❌ Ocurrió un error fatal durante la prueba mínima.", exc_info=True)

if __name__ == "__main__":
    run_minimal_test()