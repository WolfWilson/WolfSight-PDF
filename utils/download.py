from PyQt6.QtWidgets import QFileDialog, QWidget
import shutil, os

def download_pdf(source_path: str, parent: QWidget | None = None) -> None:
    dest, _ = QFileDialog.getSaveFileName(
        parent, "Guardar PDF", os.path.basename(source_path), "PDF Files (*.pdf)"
    )
    if dest:
        shutil.copyfile(source_path, dest)
