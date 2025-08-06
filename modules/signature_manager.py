# coding: utf-8
"""
Módulo para firmar documentos PDF con un QR de validación y una firma PAdES.
Versión 11 - ¡FUNCIONA!
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, asdict  # <-- 1. IMPORTAR asdict
from io import BytesIO
from pathlib import Path
from typing import Any, Final, Tuple

import qrcode
import qrcode.constants as qr_const
from PyPDF2 import PdfReader, PdfWriter
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers
from pyhanko.sign.fields import SigFieldSpec
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

_LOG = logging.getLogger("SignatureManager")
_JSON_FILE: Final[Path] = Path("validaciones.json")

@dataclass(slots=True, frozen=True)
class ValidationRecord:
    code: str
    user: str
    datetime_utc: str
    file_name: str
    sha256: str

class SignatureManager:
    def __init__(self, store_path: str | Path | None = None) -> None:
        self._store = Path(store_path or _JSON_FILE).resolve()
        if not self._store.exists():
            self._store.write_text("[]", encoding="utf-8")

    def sign_pdf(
        self,
        *,
        pdf_in: str | Path,
        pdf_out: str | Path,
        pfx_path: str | Path,
        pfx_password: str,
        user: str = "demo_user",
        qr_pos: tuple[float, float] = (50.0, 50.0),
        qr_size: float = 100.0,
        validation_base_url: str = "https://intranet-demo/validar?codigo=",
        reason: str = "Firma de conformidad",
    ) -> Tuple[ValidationRecord, bytes]:
        in_path = Path(pdf_in).resolve()
        out_path = Path(pdf_out).resolve()
        pfx_path = Path(pfx_path).resolve()
        code = uuid.uuid4().hex
        qr_png_data = self._generate_qr(validation_base_url + code)
        pdf_with_qr_data = self._overlay_qr_in_memory(
            pdf_in_path=in_path,
            qr_png_data=qr_png_data,
            code=code,
            qr_pos=qr_pos,
            qr_size=qr_size,
        )
        self._sign_with_pfx(
            pdf_in_data=pdf_with_qr_data,
            pdf_out_path=out_path,
            pfx_path=pfx_path,
            pfx_password=pfx_password,
            reason=reason,
        )
        record = ValidationRecord(
            code=code,
            user=user,
            datetime_utc=_dt.datetime.now(_dt.timezone.utc).isoformat(),
            file_name=out_path.name,
            sha256=self._sha256(out_path),
        )
        self._append_record(record)
        return record, qr_png_data

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
    def _overlay_qr_in_memory(
        *,
        pdf_in_path: Path,
        qr_png_data: bytes,
        code: str,
        qr_pos: tuple[float, float],
        qr_size: float,
    ) -> BytesIO:
        reader = PdfReader(pdf_in_path)
        first_page = reader.pages[0]
        overlay_bio = BytesIO()
        w, h = (float(first_page.mediabox.width), float(first_page.mediabox.height))
        c = canvas.Canvas(overlay_bio, pagesize=(w, h))
        x, y = qr_pos
        c.drawImage(ImageReader(BytesIO(qr_png_data)), x, y, width=qr_size, height=qr_size, mask="auto")
        c.setFont("Helvetica", 8)
        c.drawString(x, y - 10, f"Código de validación: {code}")
        c.save()
        overlay_bio.seek(0)
        overlay_pdf = PdfReader(overlay_bio)
        first_page.merge_page(overlay_pdf.pages[0])
        writer = PdfWriter()
        writer.clone_document_from_reader(reader)
        output_pdf_bio = BytesIO()
        writer.write(output_pdf_bio)
        output_pdf_bio.seek(0)
        return output_pdf_bio

    @staticmethod
    def _sign_with_pfx(
        *,
        pdf_in_data: BytesIO,
        pdf_out_path: Path,
        pfx_path: Path,
        pfx_password: str,
        reason: str
    ) -> None:
        signer = signers.SimpleSigner.load_pkcs12(
            pfx_file=pfx_path,
            passphrase=pfx_password.encode('utf-8')
        )
        if not signer:
            raise ValueError("No se pudo cargar el firmante desde el archivo PFX.")

        signature_meta = signers.PdfSignatureMetadata(
            reason=reason,
            location="Resistencia, Chaco, Argentina",
            field_name='Signature1'
        )
        field_spec = SigFieldSpec(
            sig_field_name='Signature1',
            box=(0, 0, 0, 0)
        )
        w = IncrementalPdfFileWriter(pdf_in_data)
        with pdf_out_path.open("wb") as outf:
            signers.sign_pdf(
                w,
                signature_meta=signature_meta,
                signer=signer,
                new_field_spec=field_spec,
                output=outf
            )

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
        
        # --- 2. USAR asdict(rec) EN LUGAR DE rec.__dict__ ---
        data.append(asdict(rec))
        
        self._store.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    PFX_TEST_FILE = Path("tests/credencials/certificado_prueba.pfx")
    PFX_TEST_PASS = "123456"
    PDF_INPUT_FILE = Path("tests/docs/documento_de_prueba.pdf")
    OUTPUT_DIR = Path("output")
    OUTPUT_DIR.mkdir(exist_ok=True)
    PDF_OUTPUT_FILE = OUTPUT_DIR / f"firmado_{uuid.uuid4().hex[:8]}.pdf"
    if not PFX_TEST_FILE.exists() or not PDF_INPUT_FILE.exists():
        _LOG.error("Error: Archivo PFX o PDF de entrada no encontrado.")
        _LOG.error(f"Verifica la ruta del PFX: {PFX_TEST_FILE.resolve()}")
        _LOG.error(f"Verifica la ruta del PDF: {PDF_INPUT_FILE.resolve()}")
    else:
        _LOG.info("Archivos de entrada encontrados. Iniciando proceso de firma...")
        try:
            manager = SignatureManager(store_path=OUTPUT_DIR / "mis_validaciones.json")
            validation_record, qr_code_bytes = manager.sign_pdf(
                pdf_in=PDF_INPUT_FILE,
                pdf_out=PDF_OUTPUT_FILE,
                pfx_path=PFX_TEST_FILE,
                pfx_password=PFX_TEST_PASS,
                user="Wolf-Wilson",
                reason="Documento validado para el proyecto WolfSight-PDF"
            )
            _LOG.info("✅ Proceso completado exitosamente.")
            _LOG.info(f"   PDF firmado guardado en: {PDF_OUTPUT_FILE.resolve()}")
            _LOG.info(f"   Registro de validación: {validation_record}")
            qr_path = OUTPUT_DIR / f"{validation_record.code}.png"
            qr_path.write_bytes(qr_code_bytes)
            _LOG.info(f"   Imagen QR guardada en: {qr_path.resolve()}")
        except Exception as e:
            _LOG.error("❌ Ocurrió un error fatal durante el proceso.", exc_info=True)