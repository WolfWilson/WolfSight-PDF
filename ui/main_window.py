#!/usr/bin/env python
# coding: utf-8
# ──────────────────────────────────────────────────────────────────────────────
#  ui/main_window.py
#  WolfSight-PDF · Gestor de Expedientes Digitales
# ──────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import os
import sys
from typing import cast

# ─── Qt ──────────────────────────────────────────────────────────────────────
from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    QUrl,
)
from PyQt6.QtGui import QIcon, QShowEvent
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QStyle,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineSettings,
)

# ─── Internos ────────────────────────────────────────────────────────────────
from ui.dialogs import CustomConfirmDialog
from utils.resource_handler import resource_path

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  Funciones “mock”                                                         ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
def merge_pdfs(base_pdf_path: str, files_to_annex: list[str], output_path: str) -> None:
    print(f"— ACCIÓN — Anexar {len(files_to_annex)} archivo(s) a "
          f"{os.path.basename(base_pdf_path)} → {output_path}")


def sign_pdf(
    pdf_path: str, signature_image_path: str, output_path: str, position: tuple[int, int]
) -> None:
    print(f"— ACCIÓN — Firmar {os.path.basename(pdf_path)} → {output_path}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  Visor PDF                                                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
class PdfViewer(QWebEngineView):
    """Visor PDF basado en QWebEngineView (sin pop-ups)."""

    _profile: QWebEngineProfile | None = None  # perfil único compartido

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Lazy-init del perfil -------------------------------------------------
        if PdfViewer._profile is None:
            PdfViewer._profile = QWebEngineProfile.defaultProfile()

        profile = cast(QWebEngineProfile, PdfViewer._profile)
        self.setPage(QWebEnginePage(profile, self))

        # Ajustes del visor (cast elimina el Optional[None]) ------------------
        settings = cast(QWebEngineSettings, self.settings())
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)

    # ——forzar apertura en la misma ventana—----------------------------------
    def createWindow(  # type: ignore[override]
        self, _type: QWebEnginePage.WebWindowType
    ) -> "PdfViewer":
        return self

    # ————————————————————————————————————————————
    def load_pdf(self, file_path: str | None) -> None:
        if file_path and os.path.exists(file_path):
            self.load(QUrl.fromLocalFile(os.path.abspath(file_path)))
        else:
            self.setHtml("")  # limpia


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  Header informativo                                                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
class MainHeaderWidget(QWidget):
    """Header con datos del expediente."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setObjectName("mainHeader")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(0)

        self.actuacion_label = QLabel("Actuación Digital: (ninguna)")
        self.actuacion_label.setObjectName("actuacionLabel")

        self.titular_label = QLabel("Titular: (ninguno)")
        self.titular_label.setObjectName("titularLabel")

        layout.addWidget(self.actuacion_label)
        layout.addWidget(self.titular_label)

    def update_data(self, actuacion: str, titular: str) -> None:
        self.actuacion_label.setText(f"Actuación Digital: {actuacion}")
        self.titular_label.setText(f"Titular: {titular}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  Ventana principal                                                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
class MainWindow(QMainWindow):
    """Shell principal."""

    def __init__(self) -> None:
        super().__init__()
        self.setVisible(False)
        self.setUpdatesEnabled(False)

        self.setWindowTitle("WolfSight-PDF | Gestión de Expedientes")
        self.resize(1200, 800)
        self.setWindowIcon(self._get_icon("AppIcon"))

        # Estado interno ------------------------------------------------------
        self.current_expediente_path: str | None = None
        self.current_annex_path: str | None = None
        self.menu_is_expanded: bool = False

        # Interfaz ------------------------------------------------------------
        self._create_widgets()
        self._create_layout()
        self._connect_signals()

        # Carga automática de prueba ------------------------------------------
        default_pdf = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "tests", "E-010529-2025.pdf")
        )
        if os.path.exists(default_pdf):
            self.current_expediente_path = default_pdf
            self.main_viewer.load_pdf(default_pdf)
            self.main_header.update_data("E-010529-2021", "TITULAR DEMO")

        self.setUpdatesEnabled(True)
        self.setVisible(True)

    # ——————————————————————————————————————————
    def showEvent(self, event: QShowEvent) -> None:  # noqa: D401
        self.setUpdatesEnabled(True)
        super().showEvent(event)

    # ══════════════════════ WIDGETS ═══════════════════════════════════════════
    def _create_widgets(self) -> None:
        # Menú lateral --------------------------------------------------------
        self.menu_frame = QWidget()
        self.menu_frame.setObjectName("menuFrame")
        self.menu_frame.setFixedWidth(60)

        self.btn_toggle_menu = QPushButton("")
        self.btn_open_expediente = QPushButton("")
        self.btn_load_annex = QPushButton("")
        self.btn_sign = QPushButton("")

        self.menu_buttons: dict[QPushButton, str] = {
            self.btn_toggle_menu: "Menú",
            self.btn_open_expediente: "Abrir Expediente",
            self.btn_load_annex: "Cargar Documento",
            self.btn_sign: "Firmar Documento",
        }
        for btn, text in self.menu_buttons.items():
            btn.setIcon(self._get_icon(text))
            btn.setIconSize(QSize(30, 30))
            btn.setToolTip(text)

        # Header y visores ----------------------------------------------------
        self.main_header = MainHeaderWidget()

        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_viewer = PdfViewer()
        self.annex_viewer = PdfViewer()

        main_container = self._create_viewer_container(
            "Expediente Principal", viewer=self.main_viewer
        )
        self.annex_container = self._create_viewer_container(
            "Documento a Anexar", viewer=self.annex_viewer, is_annex=True
        )

        self.content_splitter.addWidget(main_container)
        self.content_splitter.addWidget(self.annex_container)
        self.content_splitter.setSizes([self.width(), 0])

    # ══════════════════════ LAYOUT ════════════════════════════════════════════
    def _create_layout(self) -> None:
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        menu_layout = QVBoxLayout(self.menu_frame)
        menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        menu_layout.setContentsMargins(5, 5, 5, 5)
        for btn in self.menu_buttons:
            menu_layout.addWidget(btn)

        central_panel = QWidget()
        central_vbox = QVBoxLayout(central_panel)
        central_vbox.setContentsMargins(0, 0, 0, 0)
        central_vbox.setSpacing(0)
        central_vbox.addWidget(self.main_header)
        central_vbox.addWidget(self.content_splitter)

        main_layout.addWidget(self.menu_frame)
        main_layout.addWidget(central_panel)

        wrapper = QWidget()
        wrapper.setLayout(main_layout)
        self.setCentralWidget(wrapper)

    # ═════════════════════ SEÑALES ════════════════════════════════════════════
    def _connect_signals(self) -> None:
        self.btn_toggle_menu.clicked.connect(self._toggle_menu)
        self.btn_open_expediente.clicked.connect(self._open_expediente)
        self.btn_load_annex.clicked.connect(self._load_document_to_annex)
        if hasattr(self, "btn_confirm_annex"):
            self.btn_confirm_annex.clicked.connect(self._confirm_and_annex)
        if hasattr(self, "btn_close_annex"):
            self.btn_close_annex.clicked.connect(self._close_annex_pane)

    # ═════════════ HELPERS DE CONSTRUCCIÓN ════════════════════════════════════
    def _create_viewer_container(
        self, title: str, viewer: QWidget, *, is_annex: bool = False
    ) -> QWidget:
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        header = QWidget()
        header.setObjectName("viewerHeader")  # ← ahora sí, sin kwargs
        header.setFixedHeight(35)
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(5, 0, 5, 0)

        hbox.addWidget(QLabel(title))

        if is_annex:
            hbox.addStretch()
            self.btn_confirm_annex = QPushButton(self._get_icon("Anexar"), "")
            self.btn_confirm_annex.setIconSize(QSize(20, 20))
            self.btn_confirm_annex.setToolTip("Anexar al Expediente")
            self.btn_confirm_annex.setEnabled(False)
            hbox.addWidget(self.btn_confirm_annex)

            self.btn_close_annex = QPushButton(self._get_icon("Cerrar"), "")
            self.btn_close_annex.setIconSize(QSize(20, 20))
            self.btn_close_annex.setToolTip("Cerrar Panel de Anexo")
            hbox.addWidget(self.btn_close_annex)

        vbox.addWidget(header)
        vbox.addWidget(viewer)
        return container

    # ═════════════════════ UTILIDADES ════════════════════════════════════════
    def _get_icon(self, key: str) -> QIcon:
        icon_map = {
            "Menú": "menu.png",
            "Abrir Expediente": "abrir-expediente.png",
            "Cargar Documento": "cargar-documento.png",
            "Firmar Documento": "firmar-documento.png",
            "Anexar": "anexar.png",
            "Cerrar": "cerrar.png",
            "AppIcon": "app_icon.png",
        }

        filename = icon_map.get(key)
        if filename:
            path = resource_path(os.path.join("assets", "icons", filename))
            if os.path.exists(path):
                return QIcon(path)

        if key == "AppIcon":
            return QIcon()  # fallback silencioso

        style = cast(QStyle, self.style())
        fallback = {
            "Menú": style.StandardPixmap.SP_FileDialogListView,
            "Abrir Expediente": style.StandardPixmap.SP_DirOpenIcon,
            "Cargar Documento": style.StandardPixmap.SP_FileIcon,
            "Firmar Documento": style.StandardPixmap.SP_DialogApplyButton,
            "Anexar": style.StandardPixmap.SP_FileLinkIcon,
            "Cerrar": style.StandardPixmap.SP_DialogCloseButton,
        }
        print(f"[WARN] Icono “{filename}” no encontrado → usando fallback.")
        return style.standardIcon(fallback.get(key, style.StandardPixmap.SP_DesktopIcon))

    # ═════════════════════ SLOTS ═════════════════════════════════════════════
    def _open_expediente(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Expediente PDF", "", "PDF Files (*.pdf)"
        )
        if not path:
            return

        self.current_expediente_path = path
        self.main_viewer.load_pdf(path)
        self.main_header.update_data("K-003607-2025", "CACERES GLADYS NILDA")

        # Colapsa anexo si estuviera abierto
        if self.content_splitter.sizes()[1] != 0:
            self.content_splitter.setSizes([self.width(), 0])

    def _load_document_to_annex(self) -> None:
        if not self.current_expediente_path:
            print("► Abra primero un expediente principal.")
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Cargar Documento para Anexar", "", "PDF Files (*.pdf)"
        )
        if not path:
            return

        self.current_annex_path = path
        self.annex_viewer.load_pdf(path)
        self.content_splitter.setSizes([self.width() // 2, self.width() // 2])
        if hasattr(self, "btn_confirm_annex"):
            self.btn_confirm_annex.setEnabled(True)

    def _confirm_and_annex(self) -> None:
        if not (self.current_expediente_path and self.current_annex_path):
            return

        dialog = CustomConfirmDialog(self)
        if dialog.exec():
            output = self.current_expediente_path.replace(".pdf", "-anexado.pdf")
            merge_pdfs(self.current_expediente_path, [self.current_annex_path], output)
            self._close_annex_pane()
            self.main_viewer.load_pdf(output)
            self.current_expediente_path = output

    def _close_annex_pane(self) -> None:
        self.content_splitter.setSizes([self.width(), 0])
        self.annex_viewer.load_pdf("")
        self.current_annex_path = None
        if hasattr(self, "btn_confirm_annex"):
            self.btn_confirm_annex.setEnabled(False)

    def _toggle_menu(self) -> None:
        collapsed, expanded = 60, 220
        self.animation = QPropertyAnimation(self.menu_frame, b"minimumWidth", self)
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        if self.menu_is_expanded:
            self.animation.setEndValue(collapsed)
            for btn in self.menu_buttons:
                btn.setText("")
        else:
            self.animation.setEndValue(expanded)
            for btn, text in self.menu_buttons.items():
                btn.setText(f"   {text}")

        self.animation.start()
        self.menu_is_expanded = not self.menu_is_expanded


# ─── Ejecución directa para pruebas ─────────────────────────────────────────
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
