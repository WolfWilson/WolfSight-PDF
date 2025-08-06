# coding: utf-8
# ui/version.py

from __future__ import annotations

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from utils.resource_handler import resource_path


class VersionDialog(QDialog):
    """Ventana modal con información de versión."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("versionDialog")
        self.setWindowTitle("Acerca de WolfSight-PDF")
        self.setFixedSize(340, 220)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        # Cargar estilo dedicado (si existe)
        qss = resource_path("ui/styles/version.qss")
        if os.path.exists(qss):
            with open(qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo
        logo_path = resource_path("assets/icons/wolf.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(
                100,
                100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            lbl_logo = QLabel()
            lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_logo.setPixmap(pix)
            layout.addWidget(lbl_logo)

        # Texto versión
        lbl_info = QLabel("WolfSight-PDF  v1.0.0\n© 2025  Wilson Wolf")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_info.setObjectName("versionLabel")
        layout.addWidget(lbl_info)

        # Botón cerrar
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)
