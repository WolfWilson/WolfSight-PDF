import os
import sys

def resource_path(relative_path: str) -> str:
    """ 
    Devuelve la ruta absoluta a un recurso. Funciona tanto en desarrollo
    como en un ejecutable de PyInstaller.
    """
    # Usa getattr para obtener de forma segura el atributo _MEIPASS.
    # Si no existe, devuelve el directorio actual como valor por defecto.
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    
    return os.path.join(base_path, relative_path)