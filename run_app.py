# Archivo: run_app.py

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.resource_handler import resource_path

def load_main_stylesheet():
    """Carga la hoja de estilos principal de la aplicación."""
    try:
        qss_path = resource_path("ui/styles/main_style.qss")
        # Se especifica la codificación UTF-8 para evitar errores
        with open(qss_path, "r", encoding="utf-8") as f: # <<<--- CAMBIO AQUÍ
            return f.read()
    except FileNotFoundError:
        print("Advertencia: No se encontró la hoja de estilos principal 'main_style.qss'.")
        return ""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    stylesheet = load_main_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())