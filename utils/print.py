from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPageLayout
from typing import cast
import os

def print_pdf(source_path: str, parent: QWidget | None = None) -> None:
    printer = QPrinter()
    dialog = QPrintDialog(printer, parent)
    if dialog.exec():
        # Shell-out a simple print (alternativamente usar QtPdf ^)
        os.startfile(source_path, "print")  # Windows quick-hack
