from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from PyQt6.QtCore import Qt

class CustomConfirmDialog(QDialog):
    """Diálogo de confirmación personalizado."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmar Acción")
        self.setMinimumWidth(380)
        self.setObjectName("confirmDialog")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        message = QLabel("¿Estás seguro de que deseas anexar este documento al expediente principal?")
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # El error estaba en la siguiente línea, sobraba un guion
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel) # <<<--- CORREGIDO
        
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