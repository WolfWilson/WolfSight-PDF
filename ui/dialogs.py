# coding: utf-8
from __future__ import annotations

from typing import cast

from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
    QPushButton,
)


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

        # QR
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

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn_box.accepted.connect(self.accept)

        layout.addWidget(qr_label)
        layout.addSpacing(10)
        layout.addWidget(code_label)
        layout.addSpacing(15)
        layout.addWidget(btn_box)
