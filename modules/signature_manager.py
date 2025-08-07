# coding: utf-8
# modules/signature_manager.py
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import logging
import os
import re
import uuid
from dataclasses import dataclass, asdict
from io import BytesIO
from pathlib import Path
from typing import Any, Final, Tuple, List
import tempfile # Importar para archivos temporales

import qrcode
import qrcode.constants as qr_const
from PyPDF2 import PdfReader, PdfWriter
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers
from pyhanko.sign.fields import SigFieldSpec
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

# --- Configuración de Logging para Depuración ---
# Asegúrate de tener un logging.basicConfig en tu punto de entrada principal
# para ver estos mensajes en la consola.
_LOG = logging.getLogger("SignatureManager")
# ------------------------------------------------

_JSON_FILE: Final[Path] = Path("validaciones.json")
_SIGNED_FOLDER: Final[str] = "firmado_digitalmente"

@dataclass(slots=True, frozen=True)
class ValidationRecord:
    code: str
    user: str
    datetime_utc: str
    original_filename: str
    constancia_filename: str
    signed_pages_str: str
    sha256_constancia: str

class SignatureManager:
    def __init__(self, store_path: str | Path | None = None) -> None:
        self._store = Path(store_path or _JSON_FILE).resolve()
        if not self._store.exists():
            self._store.write_text("[]", encoding="utf-8")

    def create_signed_constancia(
        self,
        *,
        main_pdf_path: Path,
        pfx_path: Path,
        pfx_password: str,
        pages_to_sign_str: str,
        user: str = "demo_user",
        qr_pos: tuple[float, float] = (480.0, 40.0),
        qr_size: float = 70.0,
        validation_base_url: str = "https://intranet-demo/validar?codigo=",
        reason: str = "Firma de conformidad",
    ) -> Tuple[ValidationRecord, bytes]:
        _LOG.info("--- Iniciando proceso de firma de constancia ---")
        main_pdf_path = main_pdf_path.resolve()
        reader = PdfReader(main_pdf_path)
        max_pages = len(reader.pages)
        page_indices = self._parse_page_range(pages_to_sign_str, max_pages)

        extracted_pdf_io = self._extract_pages_to_memory(main_pdf_path, page_indices)
        _LOG.info(f"[DEBUG] Tamaño del PDF extraído: {extracted_pdf_io.getbuffer().nbytes} bytes")

        code = uuid.uuid4().hex
        qr_png_data = self._generate_qr(validation_base_url + code)
        
        pdf_with_qr_io = self._overlay_qr_on_first_page(
            pdf_in_data=extracted_pdf_io,
            qr_png_data=qr_png_data,
            code=code,
            qr_pos=qr_pos,
            qr_size=qr_size,
        )
        _LOG.info(f"[DEBUG] Tamaño del PDF con QR (antes de firmar): {pdf_with_qr_io.getbuffer().nbytes} bytes")

        # --- ESTRATEGIA DE CORRECCIÓN: USAR UN ARCHIVO TEMPORAL ---
        # Se guarda el PDF a firmar en un archivo temporal para normalizarlo.
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_f:
                temp_file_path = Path(temp_f.name)
                temp_f.write(pdf_with_qr_io.getvalue())
            _LOG.info(f"[DEBUG] PDF a firmar guardado en archivo temporal: {temp_file_path}")

            # Se pasa la RUTA del archivo temporal a la función de firma.
            signed_constancia_io = self._sign_with_pfx(
                pdf_in_path=temp_file_path, # Pasando ruta en lugar de stream
                pfx_path=pfx_path,
                pfx_password=pfx_password,
                reason=reason,
            )
            _LOG.info(f"[DEBUG] Tamaño de la constancia firmada (en memoria): {signed_constancia_io.getbuffer().nbytes} bytes")
        finally:
            # Se limpia el archivo temporal
            if temp_file_path and temp_file_path.exists():
                temp_file_path.unlink()
                _LOG.info(f"[DEBUG] Archivo temporal eliminado: {temp_file_path}")
        # --------------------------------------------------------------
        
        if signed_constancia_io.getbuffer().nbytes == 0:
            raise RuntimeError("La operación de firma resultó en un archivo vacío. Verifique el certificado PFX y la contraseña.")

        output_dir = main_pdf_path.parent / _SIGNED_FOLDER
        output_dir.mkdir(exist_ok=True)
        constancia_filename = f"{main_pdf_path.stem}_constancia_{code[:8]}.pdf"
        constancia_path = output_dir / constancia_filename
        
        _LOG.info(f"Guardando constancia firmada en: {constancia_path}")
        with constancia_path.open("wb") as f:
            f.write(signed_constancia_io.getvalue())
        
        self._stamp_original_document(
            original_path=main_pdf_path,
            page_indices=page_indices,
            qr_png_data=qr_png_data,
            qr_pos=qr_pos,
            qr_size=qr_size,
        )

        record = ValidationRecord(
            code=code,
            user=user,
            datetime_utc=_dt.datetime.now(_dt.timezone.utc).isoformat(),
            original_filename=main_pdf_path.name,
            constancia_filename=os.path.join(_SIGNED_FOLDER, constancia_filename),
            signed_pages_str=pages_to_sign_str,
            sha256_constancia=self._sha256(constancia_path),
        )
        self._append_record(record)
        _LOG.info("--- Proceso de firma de constancia finalizado exitosamente ---")
        
        return record, qr_png_data

    # ... (funciones _parse_page_range, _extract_pages_to_memory, _generate_qr no cambian) ...
    def _parse_page_range(self, range_str: str, max_pages: int) -> list[int]:
        pages = set[int]()
        try:
            parts = [p.strip() for p in range_str.split(',')]
            for part in parts:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    if not (1 <= start <= end <= max_pages):
                        raise ValueError("Rango de páginas fuera de los límites.")
                    pages.update(range(start - 1, end))
                else:
                    page = int(part)
                    if not (1 <= page <= max_pages):
                        raise ValueError("Número de página fuera de los límites.")
                    pages.add(page - 1)
        except ValueError as e:
            raise ValueError(f"Formato de página inválido: '{range_str}'. {e}") from e
        
        if not pages:
            raise ValueError("No se seleccionaron páginas.")
        return sorted(list(pages))

    @staticmethod
    def _extract_pages_to_memory(pdf_path: Path, page_indices: list[int]) -> BytesIO:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        for index in page_indices:
            writer.add_page(reader.pages[index])
        
        output_io = BytesIO()
        writer.write(output_io)
        output_io.seek(0)
        return output_io

    @staticmethod
    def _generate_qr(url: str) -> bytes:
        qr = qrcode.QRCode(error_correction=qr_const.ERROR_CORRECT_Q)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fit=True)
        with BytesIO() as buf:
            img.save(buf, "PNG")
            return buf.getvalue()
            
    @staticmethod
    def _overlay_qr_on_first_page(
        pdf_in_data: BytesIO, qr_png_data: bytes, code: str, qr_pos: tuple[float, float], qr_size: float
    ) -> BytesIO:
        reader = PdfReader(pdf_in_data)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        first_page = writer.pages[0]
        
        overlay_bio = BytesIO()
        w, h = (float(first_page.mediabox.width), float(first_page.mediabox.height))
        c = canvas.Canvas(overlay_bio, pagesize=(w, h))
        x, y = qr_pos
        c.drawImage(ImageReader(BytesIO(qr_png_data)), x, y, width=qr_size, height=qr_size, mask="auto")
        c.setFont("Helvetica", 7)
        c.drawString(x, y - 10, f"Cod. Val: {code}")
        c.save()
        overlay_bio.seek(0)
        
        overlay_pdf = PdfReader(overlay_bio)
        first_page.merge_page(overlay_pdf.pages[0])
        
        output_pdf_bio = BytesIO()
        writer.write(output_pdf_bio)
        output_pdf_bio.seek(0)
        return output_pdf_bio
    
    @staticmethod
    def _stamp_original_document(
        original_path: Path, page_indices: list[int], qr_png_data: bytes, qr_pos: tuple[float, float], qr_size: float
    ) -> None:
        reader = PdfReader(original_path)
        writer = PdfWriter()

        pages_to_stamp_indices = set(page_indices)
        if len(page_indices) == len(reader.pages):
            pages_to_stamp_indices = {0}

        overlay_bio = BytesIO()
        c = canvas.Canvas(overlay_bio)
        c.drawImage(ImageReader(BytesIO(qr_png_data)), qr_pos[0], qr_pos[1], width=qr_size, height=qr_size, mask="auto")
        c.setFont("Helvetica", 7)
        c.drawString(qr_pos[0], qr_pos[1] - 10, "Pagina con constancia de firma")
        c.save()
        overlay_bio.seek(0)
        overlay_pdf = PdfReader(overlay_bio)

        for i, page in enumerate(reader.pages):
            if i in pages_to_stamp_indices:
                page.merge_page(overlay_pdf.pages[0])
            writer.add_page(page)

        with open(original_path, "wb") as out_file:
            writer.write(out_file)

    # --- FUNCIÓN DE FIRMA MODIFICADA ---
    # Ahora acepta una ruta de archivo (Path) en lugar de un stream (BytesIO)
    @staticmethod
    def _sign_with_pfx(
        pdf_in_path: Path, # Acepta una ruta
        pfx_path: Path, 
        pfx_password: str, 
        reason: str
    ) -> BytesIO:
        _LOG.info(f"[DEBUG] Iniciando firma PFX para el archivo: {pdf_in_path}")
        signer = signers.SimpleSigner.load_pkcs12(
            pfx_file=pfx_path,
            passphrase=pfx_password.encode('utf-8')
        )
        
        if not signer:
            raise ValueError("No se pudo cargar el firmante desde el archivo PFX. ¿Contraseña incorrecta?")

        signature_meta = signers.PdfSignatureMetadata(
            reason=reason,
            location="Resistencia, Chaco, Argentina",
            field_name='Signature1'
        )
        field_spec = SigFieldSpec(sig_field_name='Signature1', box=(0, 0, 0, 0))
        
        output_io = BytesIO()
        # Se abre el archivo de la ruta para leerlo
        with pdf_in_path.open("rb") as f_in:
            w = IncrementalPdfFileWriter(f_in)
            signers.sign_pdf(
                w,
                signature_meta=signature_meta,
                signer=signer,
                new_field_spec=field_spec,
                output=output_io
            )
        
        output_io.seek(0)
        return output_io

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as fp:
            for chunk in iter(lambda: fp.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _append_record(self, rec: ValidationRecord) -> None:
        try:
            data = json.loads(self._store.read_text("utf-8"))
            if not isinstance(data, list):
                raise ValueError("La raíz del JSON no es una lista")
        except (json.JSONDecodeError, ValueError, FileNotFoundError) as exc:
            _LOG.warning("Archivo de validaciones corrupto o no encontrado, se reiniciará: %s", exc)
            data: list[dict[str, Any]] = []
        
        data.append(asdict(rec))
        
        self._store.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        