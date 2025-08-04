# WolfSight-PDF/run_app.py

import sys
from PyQt6.QtWidgets import QApplication

# Importamos la ventana principal desde su módulo en la carpeta 'ui'
from ui.main_window import MainWindow

if __name__ == '__main__':
    # Es necesario instalar PyQt6 y PyQt6-WebEngine
    # pip install PyQt6 PyQt6-WebEngine
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())