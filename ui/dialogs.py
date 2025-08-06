# coding: utf-8
# ui/dialogs.py
from __future__ import annotations

import re
from typing import cast, Tuple

from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QMessageBox,
)


class PageSelectionDialog(QDialog):
    """Diálogo para que el usuario seleccione un rango de páginas."""

    def __init__(self, max_pages: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.max_pages = max_pages
        self.setWindowTitle("Seleccionar Páginas para Firmar")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        info_label = QLabel(
            "Seleccione las páginas a firmar.\n"
            "Formatos válidos: '1-5', '8', '1-5, 8, 11'."
        )
        total_pages_label = QLabel(f"<b>Total de páginas del documento:</b> {self.max_pages}")
        
        self.pages_input = QLineEdit()
        self.pages_input.setPlaceholderText(f"Ej: 1-{self.max_pages}")
        self.pages_input.textChanged.connect(self._validate_input)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.ok_button = cast(QPushButton, self.button_box.button(QDialogButtonBox.StandardButton.Ok))
        self.ok_button.setText("Aceptar")
        
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(info_label)
        layout.addWidget(total_pages_label)
        layout.addSpacing(10)
        layout.addWidget(self.pages_input)
        layout.addWidget(self.button_box)
        
        self._validate_input(self.pages_input.text())

    def _validate_input(self, text: str) -> None:
        """Valida el texto de entrada para habilitar/deshabilitar el botón OK."""
        if not text.strip():
            self.ok_button.setEnabled(False)
            return
        
        pattern = re.compile(r"^\s*(\d+\s*-\s*\d+|\d+)(\s*,\s*(\d+\s*-\s*\d+|\d+))*\s*$")
        if not pattern.match(text):
            self.ok_button.setEnabled(False)
            return

        try:
            self._parse_page_range(text)
            self.ok_button.setEnabled(True)
        except ValueError:
            self.ok_button.setEnabled(False)

    def _parse_page_range(self, range_str: str) -> list[int]:
        """Parsea el string y valida que las páginas estén en el rango correcto."""
        pages = set[int]()
        parts = [p.strip() for p in range_str.split(',')]
        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                if start > end or start < 1 or end > self.max_pages:
                    raise ValueError("Rango de páginas inválido.")
                pages.update(range(start, end + 1))
            else:
                page = int(part)
                if page < 1 or page > self.max_pages:
                    raise ValueError("Número de página fuera de rango.")
                pages.add(page)
        return sorted(list(pages))

    def accept(self) -> None:
        """Sobrescribe para validar el contenido antes de cerrar."""
        try:
            self._parse_page_range(self.pages_input.text())
            super().accept()
        except ValueError as e:
            QMessageBox.warning(self, "Entrada Inválida", str(e))

    def get_selected_pages_str(self) -> str:
        """Retorna el string de páginas introducido por el usuario."""
        return self.pages_input.text()


class CustomConfirmDialog(QDialog):
    """Diálogo de confirmación."""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Confirmar Acción")
        self.setMinimumWidth(380)
        self.setObjectName("confirmDialog")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        msg = QLabel(
            "¿Estás seguro de que deseas anexar este documento al expediente principal?"
        )
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ERROR CORREGIDO AQUÍ
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        cast(QPushButton, buttons.button(QDialogButtonBox.StandardButton.Ok)).setText("Confirmar")
        cancel_btn = cast(QPushButton, buttons.button(QDialogButtonBox.StandardButton.Cancel))
        cancel_btn.setText("Cancelar")
        cancel_btn.setObjectName("cancelButton")

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(msg)
        layout.addSpacing(15)
        layout.addWidget(buttons)


class SignedResultDialog(QDialog):
    """Muestra QR + código de validación."""
    def __init__(self, *, code: str, qr_png: bytes, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Firma completada")
        self.setMinimumWidth(340)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        img = QImage.fromData(QByteArray(qr_png))
        qr_label = QLabel()
        qr_label.setPixmap(
            QPixmap.fromImage(img).scaled(
                160,
                160,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        code_label = QLabel(f"<b>Código de validación:</b><br>{code}")
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        code_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn_box.accepted.connect(self.accept)

        layout.addWidget(qr_label)
        layout.addSpacing(10)
        layout.addWidget(code_label)
        layout.addSpacing(15)
        layout.addWidget(btn_box)