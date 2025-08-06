#!/usr/bin/env python
# coding: utf-8
# ui/main_window.py · WolfSight-PDF
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Callable, cast

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, QUrl
from PyQt6.QtGui import QIcon, QShowEvent
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSplitter,
    QStyle,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView

from modules.signature_manager import SignatureManager
from ui.dialogs import CustomConfirmDialog, SignedResultDialog
from ui.version import VersionDialog
from utils.resource_handler import resource_path

# Place-holders externos
try:
    from utils.download import download_pdf  # type: ignore
except ImportError:  # pragma: no cover
    def download_pdf(path: str, parent: QWidget | None = None) -> None:  # type: ignore[override]
        print(f"[PLACEHOLDER] Descargar {path}")


try:
    from utils.print import print_pdf  # type: ignore
except ImportError:  # pragma: no cover
    def print_pdf(path: str, parent: QWidget | None = None) -> None:  # type: ignore[override]
        print(f"[PLACEHOLDER] Imprimir {path}")


def merge_pdfs(base_pdf_path: str, files_to_annex: list[str], output_path: str) -> None:
    print(f"— ACCIÓN — Anexar {files_to_annex} → {output_path}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
class PdfViewer(QWebEngineView):
    """Visor embebido basado en QWebEngineView."""

    _profile: QWebEngineProfile | None = None

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        if PdfViewer._profile is None:
            PdfViewer._profile = QWebEngineProfile.defaultProfile()
        profile = cast(QWebEngineProfile, PdfViewer._profile)
        self.setPage(QWebEnginePage(profile, self))

        settings = cast(QWebEngineSettings, self.settings())
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)

    def createWindow(self, _type: QWebEnginePage.WebWindowType) -> "PdfViewer":  # type: ignore[override]
        return self

    def load_pdf(self, file_path: str | None) -> None:
        if file_path and os.path.exists(file_path):
            self.load(QUrl.fromLocalFile(os.path.abspath(file_path)))
        else:
            self.setHtml("")


class MainHeaderWidget(QWidget):
    """Barra superior con info del expediente."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setObjectName("mainHeader")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 8, 8, 8)
        layout.setSpacing(2)

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
class MainWindow(QMainWindow):
    """Shell principal."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("WolfSight-PDF | Gestión de Expedientes")
        self.resize(1200, 800)
        self.setWindowIcon(self._get_icon("AppIcon"))

        # Estado
        self.current_expediente_path: str | None = None
        self.current_annex_path: str | None = None
        self.menu_is_expanded: bool = False
        self._menu_animation: QPropertyAnimation | None = None

        # Firma
        self.signature_manager = SignatureManager()

        # UI
        self._create_widgets()
        self._create_layout()
        self._connect_signals()

        demo = resource_path("tests/E-010529-2025.pdf")
        if os.path.exists(demo):
            self.current_expediente_path = demo
            self.main_viewer.load_pdf(demo)
            self.main_header.update_data("E-010529-2021", "TITULAR DEMO")

    # ——————————————————————————————————————————
    def showEvent(self, event: QShowEvent) -> None:  # noqa: D401
        super().showEvent(event)
        self.setUpdatesEnabled(True)

    # ══════════════════════ widgets ══════════════════════════════════════════
    def _create_widgets(self) -> None:
        self.menu_frame = QWidget()
        self.menu_frame.setObjectName("menuFrame")
        self.menu_frame.setFixedWidth(60)

        self.btn_toggle = QPushButton()
        self.btn_open = QPushButton()
        self.btn_load = QPushButton()
        self.btn_download = QPushButton()
        self.btn_print = QPushButton()
        self.btn_sign = QPushButton()
        self.btn_version = QPushButton()

        menu_map: dict[QPushButton, str] = {
            self.btn_toggle: "Menú",
            self.btn_open: "Abrir Expediente",
            self.btn_load: "Cargar Documento",
            self.btn_download: "Descargar",
            self.btn_print: "Imprimir",
            self.btn_sign: "Firmar Documento",
        }
        for btn, label in menu_map.items():
            btn.setIcon(self._get_icon(label))
            btn.setIconSize(QSize(30, 30))
            btn.setToolTip(label)

        self.btn_version.setIcon(self._get_icon("Versión"))
        self.btn_version.setIconSize(QSize(40, 40))
        self.btn_version.setToolTip("Acerca de WolfSight-PDF")

        # Visores
        self.main_header = MainHeaderWidget()
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_viewer = PdfViewer()
        self.annex_viewer = PdfViewer()

        main_container = self._create_viewer_container(
            "Expediente Principal", self.main_viewer, path_getter=lambda: self.current_expediente_path
        )
        annex_container = self._create_viewer_container(
            "Documento a Anexar", self.annex_viewer, is_annex=True, path_getter=lambda: self.current_annex_path
        )
        self.content_splitter.addWidget(main_container)
        self.content_splitter.addWidget(annex_container)
        self.content_splitter.setSizes([self.width(), 0])

    # ══════════════════════ layout ═══════════════════════════════════════════
    def _create_layout(self) -> None:
        menu_vbox = QVBoxLayout(self.menu_frame)
        menu_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        menu_vbox.setContentsMargins(5, 5, 5, 5)
        menu_vbox.addWidget(self.btn_toggle)
        menu_vbox.addWidget(self.btn_open)
        menu_vbox.addWidget(self.btn_load)
        menu_vbox.addWidget(self.btn_download)
        menu_vbox.addWidget(self.btn_print)
        menu_vbox.addWidget(self.btn_sign)
        menu_vbox.addStretch()
        menu_vbox.addWidget(self.btn_version)

        central_panel = QWidget()
        central_vbox = QVBoxLayout(central_panel)
        central_vbox.setContentsMargins(0, 0, 0, 0)
        central_vbox.setSpacing(0)
        central_vbox.addWidget(self.main_header)
        central_vbox.addWidget(self.content_splitter)

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self.menu_frame)
        root_layout.addWidget(central_panel)

        self.setCentralWidget(root)

    # ═════════════════════ señales ═══════════════════════════════════════════
    def _connect_signals(self) -> None:
        self.btn_toggle.clicked.connect(self._toggle_menu)
        self.btn_open.clicked.connect(self._open_expediente)
        self.btn_load.clicked.connect(self._load_document_to_annex)
        self.btn_download.clicked.connect(lambda: self._download_pdf(self.current_expediente_path))
        self.btn_print.clicked.connect(lambda: self._print_pdf(self.current_expediente_path))
        self.btn_sign.clicked.connect(self._sign_current_pdf)
        self.btn_version.clicked.connect(lambda: VersionDialog(self).exec())

        if hasattr(self, "btn_confirm_annex"):
            self.btn_confirm_annex.clicked.connect(self._confirm_and_annex)
        if hasattr(self, "btn_close_annex"):
            self.btn_close_annex.clicked.connect(self._close_annex_pane)

    # ═════════════ viewer container ══════════════════════════════════════════
    def _create_viewer_container(
        self,
        title: str,
        viewer: QWidget,
        *,
        is_annex: bool = False,
        path_getter: Callable[[], str | None],
    ) -> QWidget:
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        header = QWidget()
        header.setObjectName("viewerHeader")
        header.setFixedHeight(35)
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(5, 0, 5, 0)

        hbox.addWidget(QLabel(title))
        hbox.addStretch()

        if is_annex:
            self.btn_confirm_annex = QPushButton(self._get_icon("Anexar"), "")
            self.btn_confirm_annex.setIconSize(QSize(30, 30))
            self.btn_confirm_annex.setToolTip("Anexar al Expediente")
            self.btn_confirm_annex.setEnabled(False)
            hbox.addWidget(self.btn_confirm_annex)

            self.btn_close_annex = QPushButton(self._get_icon("Cerrar"), "")
            self.btn_close_annex.setIconSize(QSize(30, 30))
            self.btn_close_annex.setToolTip("Cerrar Panel de Anexo")
            hbox.addWidget(self.btn_close_annex)

        vbox.addWidget(header)
        vbox.addWidget(viewer)
        return container

    # ═════════════════════ utilidades ════════════════════════════════════════
    def _get_icon(self, key: str) -> QIcon:
        icon_map = {
            "Menú": "menu.png",
            "Abrir Expediente": "abrir-expediente.png",
            "Cargar Documento": "cargar-documento.png",
            "Firmar Documento": "firmar-documento.png",
            "Descargar": "descargar.png",
            "Imprimir": "imprimir.png",
            "Anexar": "anexar.png",
            "Cerrar": "cerrar.png",
            "Versión": "wolf.png",
            "AppIcon": "app_icon.png",
        }
        filename = icon_map.get(key)
        if filename:
            full = resource_path(os.path.join("assets", "icons", filename))
            if os.path.exists(full):
                return QIcon(full)

        if key == "AppIcon":
            return QIcon()

        return cast(QStyle, self.style()).standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)

    # —— acciones básicas ——————————————————————————————————————————————
    def _download_pdf(self, path: str | None) -> None:
        if path:
            download_pdf(path, self)

    def _print_pdf(self, path: str | None) -> None:
        if path:
            print_pdf(path, self)

    def _open_expediente(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Abrir Expediente PDF", "", "PDF (*.pdf)")
        if path:
            self.current_expediente_path = path
            self.main_viewer.load_pdf(path)
            self.main_header.update_data("K-003607-2025", "CACERES GLADYS NILDA")
            if self.content_splitter.sizes()[1] != 0:
                self.content_splitter.setSizes([self.width(), 0])

    def _load_document_to_annex(self) -> None:
        if not self.current_expediente_path:
            print("► Primero abra un expediente principal.")
            return
        path, _ = QFileDialog.getOpenFileName(self, "Cargar Documento", "", "PDF (*.pdf)")
        if path:
            self.current_annex_path = path
            self.annex_viewer.load_pdf(path)
            self.content_splitter.setSizes([self.width() // 2, self.width() // 2])
            if hasattr(self, "btn_confirm_annex"):
                self.btn_confirm_annex.setEnabled(True)

    def _confirm_and_annex(self) -> None:
        if not (self.current_expediente_path and self.current_annex_path):
            return
        if CustomConfirmDialog(self).exec():
            output = self.current_expediente_path.replace(".pdf", "-anexado.pdf")
            merge_pdfs(self.current_expediente_path, [self.current_annex_path], output)
            self._close_annex_pane()
            self.main_viewer.load_pdf(output)
            self.current_expediente_path = output

    def _close_annex_pane(self) -> None:
        self.content_splitter.setSizes([self.width(), 0])
        self.annex_viewer.setHtml("")
        self.current_annex_path = None
        if hasattr(self, "btn_confirm_annex"):
            self.btn_confirm_annex.setEnabled(False)

    # ——— firma digital ——————————————————————————————————————————————
    def _sign_current_pdf(self) -> None:
        if not self.current_expediente_path:
            print("► Primero abra un expediente para firmar.")
            return

        pfx_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar certificado .pfx", "", "PFX (*.pfx)")
        if not pfx_path:
            return

        pwd, ok = QInputDialog.getText(
            self,
            "Contraseña",
            "Contraseña del certificado:",
            QLineEdit.EchoMode.Password,
        )
        if not ok:
            return

        src = Path(cast(str, self.current_expediente_path))
        dst = src.with_stem(src.stem + "-firmado")

        try:
            rec, qr_png = self.signature_manager.sign_pdf(
                pdf_in=src,
                pdf_out=dst,
                pfx_path=pfx_path,
                pfx_password=pwd,
                user="demo_user",
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] Firma fallida → {exc}")
            return

        self.current_expediente_path = str(dst)
        self.main_viewer.load_pdf(str(dst))
        SignedResultDialog(code=rec.code, qr_png=qr_png, parent=self).exec()

    # ——— menú lateral ——————————————————————————————————————————————
    def _toggle_menu(self) -> None:
        collapsed, expanded = 60, 220
        self._menu_animation = QPropertyAnimation(self.menu_frame, b"minimumWidth", self)
        self._menu_animation.setDuration(300)
        self._menu_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        if self.menu_is_expanded:
            self._menu_animation.setEndValue(collapsed)
            for btn in (
                self.btn_toggle,
                self.btn_open,
                self.btn_load,
                self.btn_download,
                self.btn_print,
                self.btn_sign,
            ):
                btn.setText("")
        else:
            self._menu_animation.setEndValue(expanded)
            self.btn_toggle.setText("   Menú")
            self.btn_open.setText("   Abrir Expediente")
            self.btn_load.setText("   Cargar Documento")
            self.btn_download.setText("   Descargar")
            self.btn_print.setText("   Imprimir")
            self.btn_sign.setText("   Firmar Documento")

        self._menu_animation.start()
        self.menu_is_expanded = not self.menu_is_expanded


# ─── Arranque directo ——————————————————————————————————————————————
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
