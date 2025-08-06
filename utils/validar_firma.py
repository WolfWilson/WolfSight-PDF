# coding: utf-8
# utils/validar_firma.py
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Optional

_LOG = logging.getLogger(__name__)

def find_and_validate_signature(
    main_pdf_path: Path,
    current_page_number: int,  # base 1
    validations_json_path: Path
) -> Optional[dict[str, Any]]:
    """
    Busca en el JSON de validaciones si la página actual de un PDF
    tiene una constancia de firma asociada y la valida.

    Retorna un diccionario con los datos de la firma si es válida,
    o None si no hay firma o no es válida.
    """
    _LOG.info(f"Validación solicitada para {main_pdf_path.name}, página {current_page_number}")
    if not validations_json_path.exists():
        _LOG.warning("Archivo de validaciones no encontrado.")
        return None

    try:
        records = json.loads(validations_json_path.read_text("utf-8"))
        if not isinstance(records, list):
            _LOG.error("El archivo de validaciones no contiene una lista JSON.")
            return None
    except json.JSONDecodeError:
        _LOG.error("Error al decodificar el archivo de validaciones JSON.")
        return None

    for record in records:
        if record.get('original_filename') != main_pdf_path.name:
            continue

        # Parsear las páginas firmadas del registro
        try:
            pages_str = record.get('signed_pages_str', '')
            signed_pages = set[int]()
            parts = [p.strip() for p in pages_str.split(',')]
            for part in parts:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    signed_pages.update(range(start, end + 1))
                else:
                    signed_pages.add(int(part))
            
            # Comprobar si la página actual fue firmada en este registro
            if current_page_number in signed_pages:
                constancia_path_str = record.get('constancia_filename', '')
                constancia_path = main_pdf_path.parent / constancia_path_str
                
                if not constancia_path.exists():
                    _LOG.warning(f"No se encontró el archivo de constancia: {constancia_path}")
                    continue

                # Validar el hash
                digest = hashlib.sha256()
                with constancia_path.open("rb") as fp:
                    for chunk in iter(lambda: fp.read(8192), b""):
                        digest.update(chunk)
                
                if digest.hexdigest() == record.get('sha256_constancia'):
                    _LOG.info(f"Validación de hash exitosa para la página {current_page_number}.")
                    # TODO (Avanzado): Usar pyhanko.validation para una verificación criptográfica.
                    return record  # Firma encontrada y válida
                else:
                    _LOG.warning(f"El hash de la constancia no coincide para la página {current_page_number}.")

        except (ValueError, TypeError) as e:
            _LOG.error(f"Error al procesar el registro de validación: {record}. Error: {e}")
            continue
            
    _LOG.info(f"No se encontró un registro de firma válido para la página {current_page_number}.")
    return None