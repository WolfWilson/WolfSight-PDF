import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QSplitter, QDialog, QDialogButtonBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QUrl, Qt, QPropertyAnimation, QEasingCurve, QSize

# --- Lógica de PDF (simulada) ---
def merge_pdfs(base_pdf_path, files_to_annex, output_path):
    print(f"--- ACCIÓN REALIZADA: Anexar archivos a {os.path.basename(base_pdf_path)} ---")

def sign_pdf(pdf_path, signature_image_path, output_path, position):
    print(f"--- ACCIÓN REALIZADA: Firmar el documento {os.path.basename(pdf_path)} ---")

# --- Widget del Visor de PDF ---
from PyQt6.QtWebEngineWidgets import QWebEngineView
class PdfViewer(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings().setAttribute(self.settings().WebAttribute.PluginsEnabled, True)
        self.settings().setAttribute(self.settings().WebAttribute.PdfViewerEnabled, True)

    def load_pdf(self, file_path):
        if file_path and os.path.exists(file_path):
            self.load(QUrl.fromLocalFile(file_path))
        else:
            self.setHtml("") # Limpia la vista si el archivo no existe o la ruta es vacía

# --- Ventana de Confirmación Mejorada ---
class CustomConfirmDialog(QDialog):
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
            QPushButton#cancelButton {
                background-color: #6c757d;
            }
            QPushButton#cancelButton:hover {
                background-color: #5a6268;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        message = QLabel("¿Estás seguro de que deseas anexar este documento al expediente principal?")
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)

        if ok_button:
            ok_button.setText("Confirmar")
        if cancel_button:
            cancel_button.setText("Cancelar")
            cancel_button.setObjectName("cancelButton")
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(message)
        layout.addSpacing(15)
        layout.addWidget(button_box)
        self.setLayout(layout)

# --- Widget para el Encabezado Principal ---
class MainHeaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setStyleSheet("background-color: #e0e5e9; padding-left: 15px; border-bottom: 1px solid #c8cccf;")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(0)
        
        self.actuacion_label = QLabel("Actuación Digital: (ninguna)")
        self.actuacion_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; border: none;")
        self.titular_label = QLabel("Titular: (ninguno)")
        self.titular_label.setStyleSheet("font-size: 12px; color: #2c3e50; border: none;")
        
        layout.addWidget(self.actuacion_label)
        layout.addWidget(self.titular_label)
        self.setLayout(layout)

    def update_data(self, actuacion, titular):
        self.actuacion_label.setText(f"Actuación Digital: {actuacion}")
        self.titular_label.setText(f"Titular: {titular}")

# --- Ventana Principal del Dashboard ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard de Gestión de Expedientes")
        self.setGeometry(100, 100, 1200, 800)
        self.current_expediente_path = None
        self.current_annex_path = None
        self.menu_is_expanded = False

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Panel de Menú
        self.menu_frame = QWidget()
        self.menu_frame.setStyleSheet("background-color: #2c3e50; color: white;")
        self.menu_frame.setFixedWidth(60)
        menu_layout = QVBoxLayout()
        menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        menu_layout.setContentsMargins(5, 5, 5, 5)

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
            menu_layout.addWidget(btn)
        self.menu_frame.setLayout(menu_layout)
        
        # Área de Contenido Principal
        content_main_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.main_header = MainHeaderWidget()
        
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        main_viewer_container = self.create_viewer_container("Expediente Principal")
        self.main_viewer = PdfViewer()
        
        main_container_layout = main_viewer_container.layout()
        if main_container_layout:
            main_container_layout.addWidget(self.main_viewer)

        self.annex_viewer_container = self.create_viewer_container("Documento a Anexar", is_annex=True)
        self.annex_viewer = PdfViewer()
        
        annex_container_layout = self.annex_viewer_container.layout()
        if annex_container_layout:
            annex_container_layout.addWidget(self.annex_viewer)
        
        self.content_splitter.addWidget(main_viewer_container)
        self.content_splitter.addWidget(self.annex_viewer_container)
        self.content_splitter.setSizes([self.width(), 0])
        
        content_layout.addWidget(self.main_header)
        content_layout.addWidget(self.content_splitter)
        content_main_widget.setLayout(content_layout)
        
        main_layout.addWidget(self.menu_frame)
        main_layout.addWidget(content_main_widget)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Conexiones
        self.btn_toggle_menu.clicked.connect(self.toggle_menu)
        self.btn_open_expediente.clicked.connect(self.open_expediente)
        self.btn_load_annex.clicked.connect(self.load_document_to_annex)
        self.btn_confirm_annex.clicked.connect(self.confirm_and_annex)
        self.btn_close_annex.clicked.connect(self.close_annex_pane)
    
    def create_viewer_container(self, title, is_annex=False):
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = QWidget()
        header.setFixedHeight(35)
        header.setStyleSheet("background-color: #f8f9fa; border-bottom: 1px solid #dee2e6; padding: 0 5px;")
        header_layout = QHBoxLayout()
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

        header.setLayout(header_layout)
        layout.addWidget(header)
        container.setLayout(layout)
        return container

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
    
    def close_annex_pane(self):
        self.content_splitter.setSizes([self.width(), 0])
        self.annex_viewer.load_pdf("")
        self.current_annex_path = None
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
                btn.setText(f"  {text}")
        self.animation.start()
        self.menu_is_expanded = not self.menu_is_expanded

# --- Punto de Entrada ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())