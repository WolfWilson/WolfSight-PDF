# WolfSight-PDF/ui/main_window.py

import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QSplitter, QDialog, QDialogButtonBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QUrl, Qt, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtWebEngineWidgets import QWebEngineView

# --- Lógica de PDF (simulada, para ser movida a modules/) ---
def merge_pdfs(base_pdf_path, files_to_annex, output_path):
    """Función simulada para unir PDFs."""
    print(f"--- ACCIÓN REALIZADA: Anexar archivos a {os.path.basename(base_pdf_path)} ---")
    print(f"Archivos a anexar: {files_to_annex}")
    print(f"Archivo de salida: {output_path}")

def sign_pdf(pdf_path, signature_image_path, output_path, position):
    """Función simulada para firmar un PDF."""
    print(f"--- ACCIÓN REALIZADA: Firmar el documento {os.path.basename(pdf_path)} ---")

# --- Widget del Visor de PDF (para ser movido a ui/widgets/) ---
class PdfViewer(QWebEngineView):
    """Widget para mostrar archivos PDF."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- CORRECCIÓN 1: Comprobar si 'settings' existe ---
        # Guardamos la configuración en una variable para evitar llamarla múltiples veces
        settings = self.settings()
        # Nos aseguramos de que no sea None antes de usarla
        if settings:
            settings.setAttribute(settings.WebAttribute.PluginsEnabled, True)
            settings.setAttribute(settings.WebAttribute.PdfViewerEnabled, True)

    def load_pdf(self, file_path):
        if file_path and os.path.exists(file_path):
            self.load(QUrl.fromLocalFile(os.path.abspath(file_path)))
        else:
            self.setHtml("")  # Limpia la vista si no hay archivo

# --- Ventana de Confirmación (para ser movida a ui/dialogs.py) ---
class CustomConfirmDialog(QDialog):
    # (Este código no tenía errores y permanece igual)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmar Acción")
        self.setMinimumWidth(380)
        self.setStyleSheet("""
            QDialog { background-color: #ffffff; }
            QLabel { font-size: 14px; color: #333; }
            QPushButton { 
                background-color: #007bff; color: white; padding: 8px 20px; 
                border-radius: 4px; font-size: 14px; border: none;
            }
            QPushButton:hover { background-color: #0056b3; }
            QPushButton#cancelButton { background-color: #6c757d; }
            QPushButton#cancelButton:hover { background-color: #5a6268; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        message = QLabel("¿Estás seguro de que deseas anexar este documento al expediente principal?")
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)

        if ok_button: ok_button.setText("Confirmar")
        if cancel_button:
            cancel_button.setText("Cancelar")
            cancel_button.setObjectName("cancelButton")
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(message)
        layout.addSpacing(15)
        layout.addWidget(button_box)

# --- Widget del Encabezado (para ser movido a ui/widgets/) ---
class MainHeaderWidget(QWidget):
    # (Este código no tenía errores y permanece igual)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setStyleSheet("background-color: #e0e5e9; padding-left: 15px; border-bottom: 1px solid #c8cccf;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(0)
        
        self.actuacion_label = QLabel("Actuación Digital: (ninguna)")
        self.actuacion_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; border: none;")
        self.titular_label = QLabel("Titular: (ninguno)")
        self.titular_label.setStyleSheet("font-size: 12px; color: #2c3e50; border: none;")
        
        layout.addWidget(self.actuacion_label)
        layout.addWidget(self.titular_label)

    def update_data(self, actuacion, titular):
        self.actuacion_label.setText(f"Actuación Digital: {actuacion}")
        self.titular_label.setText(f"Titular: {titular}")

# --- Ventana Principal del Dashboard ---
class MainWindow(QMainWindow):
    """La ventana principal de la aplicación WolfSight-PDF."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WolfSight-PDF | Gestión de Expedientes")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon()) # Aquí podrías usar un ícono de 'assets/icons'
        
        self.current_expediente_path = None
        self.current_annex_path = None
        self.menu_is_expanded = False

        self._create_widgets()
        self._create_layout()
        self._connect_signals()
    
    def _create_widgets(self):
        """Crea todos los widgets necesarios para la ventana."""
        self.menu_frame = QWidget()
        self.menu_frame.setStyleSheet("background-color: #2c3e50; color: white;")
        self.menu_frame.setFixedWidth(60)
        
        self.btn_toggle_menu = QPushButton("")
        self.btn_open_expediente = QPushButton("")
        self.btn_load_annex = QPushButton("")
        self.btn_sign = QPushButton("")
        
        self.menu_buttons = {
            self.btn_toggle_menu: "Menú",
            self.btn_open_expediente: "Abrir Expediente",
            self.btn_load_annex: "Cargar Documento",
            self.btn_sign: "Firmar Documento",
        }
        for btn, text in self.menu_buttons.items():
            btn.setIcon(self.get_icon_for_button(text))
            btn.setIconSize(QSize(30, 30))
            btn.setToolTip(text)
            btn.setStyleSheet("QPushButton { text-align: left; padding: 8px; border: none; } QPushButton:hover { background-color: #34495e; }")

        self.main_header = MainHeaderWidget()
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- CORRECCIÓN 2: Crear visores primero y pasarlos al contenedor ---
        # 1. Creamos las instancias de los visores de PDF
        self.main_viewer = PdfViewer()
        self.annex_viewer = PdfViewer()

        # 2. Pasamos el visor como argumento para que el contenedor lo ensamble
        main_viewer_container = self.create_viewer_container("Expediente Principal", viewer=self.main_viewer)
        self.annex_viewer_container = self.create_viewer_container("Documento a Anexar", viewer=self.annex_viewer, is_annex=True)
        
        self.content_splitter.addWidget(main_viewer_container)
        self.content_splitter.addWidget(self.annex_viewer_container)
        self.content_splitter.setSizes([self.width(), 0])

    def _create_layout(self):
        # (Este código no tenía errores y permanece igual)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        menu_layout = QVBoxLayout(self.menu_frame)
        menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        menu_layout.setContentsMargins(5, 5, 5, 5)
        for btn in self.menu_buttons.keys():
            menu_layout.addWidget(btn)
        
        content_main_widget = QWidget()
        content_layout = QVBoxLayout(content_main_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.main_header)
        content_layout.addWidget(self.content_splitter)
        
        main_layout.addWidget(self.menu_frame)
        main_layout.addWidget(content_main_widget)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _connect_signals(self):
        # (Este código no tenía errores, solo se asegura que btn_confirm_annex exista)
        self.btn_toggle_menu.clicked.connect(self.toggle_menu)
        self.btn_open_expediente.clicked.connect(self.open_expediente)
        self.btn_load_annex.clicked.connect(self.load_document_to_annex)
        if hasattr(self, 'btn_confirm_annex'):
            self.btn_confirm_annex.clicked.connect(self.confirm_and_annex)
        if hasattr(self, 'btn_close_annex'):
            self.btn_close_annex.clicked.connect(self.close_annex_pane)
    
    # --- CORRECCIÓN 3: Modificar la firma de la función ---
    def create_viewer_container(self, title, viewer: QWidget, is_annex=False):
        """Crea un contenedor estándar para un visor de PDF."""
        container = QWidget()
        layout = QVBoxLayout(container) # Asignamos el layout directamente
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = QWidget()
        header.setFixedHeight(35)
        header.setStyleSheet("background-color: #f8f9fa; border-bottom: 1px solid #dee2e6; padding: 0 5px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(5, 0, 5, 0)

        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; border: none; color: #333;")
        header_layout.addWidget(label)

        if is_annex:
            header_layout.addStretch()
            self.btn_confirm_annex = QPushButton(self.get_icon_for_button("Anexar"), "")
            self.btn_confirm_annex.setToolTip("Anexar al Expediente")
            self.btn_confirm_annex.setIconSize(QSize(20, 20))
            self.btn_confirm_annex.setEnabled(False)
            self.btn_confirm_annex.setStyleSheet("border: none; padding: 5px;")
            header_layout.addWidget(self.btn_confirm_annex)

            self.btn_close_annex = QPushButton(self.get_icon_for_button("Cerrar"), "")
            self.btn_close_annex.setToolTip("Cerrar Panel de Anexo")
            self.btn_close_annex.setIconSize(QSize(20, 20))
            self.btn_close_annex.setStyleSheet("border: none; padding: 5px;")
            header_layout.addWidget(self.btn_close_annex)

        layout.addWidget(header)
        # Se añade el visor (u otro widget) al layout del contenedor
        layout.addWidget(viewer)
        return container

    # --- El resto de los métodos permanecen sin cambios ---
    def open_expediente(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Expediente PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.current_expediente_path = file_path
            self.main_viewer.load_pdf(file_path)
            actuacion_simulada = "K-003607-2025"
            titular_simulado = "CACERES GLADYS NILDA"
            self.main_header.update_data(actuacion_simulada, titular_simulado)
            if self.content_splitter.sizes()[1] == 0:
                self.content_splitter.setSizes([self.width(), 0])

    def load_document_to_annex(self):
        if not self.current_expediente_path:
            print("Primero debe abrir un expediente principal.")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Cargar Documento para Anexar", "", "PDF Files (*.pdf)")
        if file_path:
            self.current_annex_path = file_path
            self.annex_viewer.load_pdf(file_path)
            self.content_splitter.setSizes([self.width()//2, self.width()//2])
            self.btn_confirm_annex.setEnabled(True)
    
    def confirm_and_annex(self):
        if not self.current_expediente_path or not self.current_annex_path: return
        
        dialog = CustomConfirmDialog(self)
        if dialog.exec():
            output_path = self.current_expediente_path.replace(".pdf", "-anexado.pdf")
            merge_pdfs(self.current_expediente_path, [self.current_annex_path], output_path)
            self.close_annex_pane()
            self.main_viewer.load_pdf(output_path)
            self.current_expediente_path = output_path
    
    def close_annex_pane(self):
        self.content_splitter.setSizes([self.width(), 0])
        self.annex_viewer.load_pdf("")
        self.current_annex_path = None
        if hasattr(self, 'btn_confirm_annex'):
            self.btn_confirm_annex.setEnabled(False)

    def get_icon_for_button(self, text):
        style = self.style()
        if not style: return QIcon()
        
        icon_map = {
            "Menú": style.StandardPixmap.SP_FileDialogListView,
            "Abrir Expediente": style.StandardPixmap.SP_DirOpenIcon,
            "Cargar Documento": style.StandardPixmap.SP_FileIcon,
            "Firmar Documento": style.StandardPixmap.SP_DialogApplyButton,
            "Anexar": style.StandardPixmap.SP_FileLinkIcon,
            "Cerrar": style.StandardPixmap.SP_DialogCloseButton,
        }
        return style.standardIcon(icon_map.get(text, style.StandardPixmap.SP_DesktopIcon))

    def toggle_menu(self):
        collapsed_width = 60
        expanded_width = 220
        
        self.animation = QPropertyAnimation(self.menu_frame, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        if self.menu_is_expanded:
            self.animation.setEndValue(collapsed_width)
            for btn, text in self.menu_buttons.items():
                btn.setText("")
                btn.setToolTip(text)
        else:
            self.animation.setEndValue(expanded_width)
            for btn, text in self.menu_buttons.items():
                btn.setText(f"   {text}")
        
        self.animation.start()
        self.menu_is_expanded = not self.menu_is_expanded