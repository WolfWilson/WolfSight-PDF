# test_pyhanko.py (Versión Definitiva y Correcta)

from pathlib import Path
from pyhanko.sign import signers
import traceback

def test_pfx_loading():
    """
    Función para probar la carga de un certificado PFX y su clave privada
    utilizando pyhanko.
    """
    print("--- Iniciando prueba de carga de certificado PFX con pyhanko ---")
    
    try:
        pfx_path = Path(r"C:\Users\wolfwilson\Downloads\Git\WolfSight-PDF\tests\credencials\certificado_prueba.pfx")
        password_bytes = b"123456"

        print(f"[*] Intentando cargar el archivo: {pfx_path}")
        print("[*] Usando la contraseña proporcionada...")

        signer = signers.SimpleSigner.load_pkcs12(
            pfx_file=pfx_path,
            passphrase=password_bytes 
        )

        if signer and signer.signing_cert:
            print("\n----------------------------------------------------")
            print("✅ ¡Éxito! Certificado y clave privada cargados correctamente.")
            print("----------------------------------------------------")
            
            cert_info = signer.signing_cert
            subject_info = cert_info.subject.native
            
            print(f"   Sujeto (Subject)    : {subject_info.get('common_name', 'N/A')}")
            print(f"   Organización (O)    : {subject_info.get('organization_name', 'N/A')}")
            print(f"   Emisor (Issuer)     : {cert_info.issuer.native.get('common_name', 'N/A')}")
            print(f"   Número de Serie     : {cert_info.serial_number}")
            
            # --- SECCIÓN CORREGIDA DEFINITIVA ---
            # La forma correcta es acceder como si fuera un diccionario.
            # Usamos '# type: ignore' para indicarle a Pylance que sabemos lo que hacemos,
            # ya que la librería no está completamente tipada para el análisis estático.
            
            # Acceso a las fechas de validez
            validity_data = cert_info['tbs_certificate']['validity']  # type: ignore
            valid_from = validity_data['not_before'].native
            valid_to = validity_data['not_after'].native
            print(f"   Válido desde        : {valid_from.strftime('%d-%m-%Y %H:%M:%S')}")
            print(f"   Válido hasta        : {valid_to.strftime('%d-%m-%Y %H:%M:%S')}")
            
            # Acceso al algoritmo de firma
            sig_algo_name = cert_info['signature_algorithm']['algorithm'].native  # type: ignore
            print(f"   Algoritmo de Firma   : {sig_algo_name}")

        else:
            print("\n❌ Error: La función 'load_pkcs12' se completó pero no devolvió un firmante válido.")

    except FileNotFoundError:
        print(f"\n❌ ERROR CRÍTICO: No se pudo encontrar el archivo PFX.")
        print(f"   Ruta verificada: {pfx_path}")
        print("   Asegúrate de que el archivo exista en esa ubicación.")

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: Ocurrió un problema durante el procesamiento del certificado.")
        print("   Causas comunes: Contraseña incorrecta, archivo PFX corrupto o un error en el script.")
        print("\n--- Detalles del Error ---")
        traceback.print_exc()

if __name__ == "__main__":
    test_pfx_loading()