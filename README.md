# 🐺 WolfSight-PDF - Gestor de Expedientes Digitales

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green?logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-PDF-orange)](https://pymupdf.readthedocs.io/)
[![pypdf](https://img.shields.io/badge/pypdf-PDF-red)](https://pypdf.readthedocs.io/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)

---

## 📢 Descripción General

**WolfSight-PDF** es una aplicación de escritorio diseñada para la gestión y manipulación de expedientes digitales en formato PDF dentro de un entorno organizacional.  
Su objetivo es **centralizar y simplificar el flujo de trabajo diario** de los operadores, permitiendo **visualizar, anexar y firmar documentos** de manera eficiente y segura.

El sistema se conecta a un **servidor de archivos** para obtener los expedientes, los presenta en una **interfaz moderna tipo dashboard** y provee las herramientas necesarias para su modificación, garantizando **integridad y trazabilidad**.

---

## 🚀 Objetivos del Proyecto

- 🖥️ **Centralizar la Visualización**: Ofrecer una única interfaz para abrir y examinar expedientes PDF complejos.  
- 📎 **Simplificar el Anexado**: Facilitar la tarea de añadir nueva documentación mediante un visor comparativo.  
- ✍️ **Integrar Firma Digital**: Implementar una solución robusta y legalmente válida para la firma de documentos.  
- ⚙️ **Optimizar el Flujo de Trabajo**: Reducir pasos manuales y minimizar errores humanos.  
- 🎨 **Proveer una Interfaz Moderna**: Mejorar la experiencia del usuario con un diseño intuitivo.

---

## 🧩 Características Destacadas

✔ **Interfaz tipo Dashboard**: Menú lateral desplegable para acceso rápido.  
✔ **Visor de PDF Dual**: Expediente principal y documento a anexar, lado a lado.  
✔ **Encabezado Dinámico**: Información clave del expediente en tiempo real.  
✔ **Flujo de Anexo Guiado**: Proceso claro para anexar documentos.  
✔ **Conexión a Servidor**: Compatible con entornos centralizados mediante FTP.  
✔ **Alta Personalización**: Código fácilmente extensible.

---

## 🛠️ Tecnologías Utilizadas

| Categoría | Herramientas |
|-----------|--------------|
| **Lenguaje** | Python 3.12 |
| **GUI** | PyQt6, PyQt6-WebEngine |
| **Manipulación de PDF** | PyMuPDF (fitz), pypdf |
| **Conectividad** | ftplib (versión original) |

---

## 📦 Instalación y Uso

```bash
# 1️⃣ Clonar el repositorio
git clone https://github.com/WolfWilson/WolfSight-PDF.git
cd WolfSight-PDF

# 2️⃣ Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate  # En Windows
source venv/bin/activate # En Linux/Mac

# 3️⃣ Instalar dependencias
pip install -r requirements.txt

# 4️⃣ Ejecutar la aplicación
python run_app.py
```

---

## 📂 Estructura del Proyecto

```
LycanVisualizador/
│
├── assets/                # Iconos, imágenes y recursos
│
├── modules/               # Lógica backend
│   ├── pdf_tools.py       # Unir y firmar PDFs
│   └── ftp_client.py      # Conexión y transferencia FTP
│
├── ui/                    # Interfaz gráfica
│   ├── main_window.py     # Ventana principal (Dashboard)
│   ├── widgets/           # Widgets personalizados
│   └── main_window.ui     # (Opcional) Diseño Qt Designer
│
├── run_app.py             # Script principal
├── requirements.txt       # Dependencias
└── README.md
```

---

## 🔍 Flujo de Trabajo Actual

1️⃣ Iniciar la aplicación.  
2️⃣ Abrir un expediente desde el servidor (o local en pruebas).  
3️⃣ Cargar datos en el encabezado principal.  
4️⃣ Cargar documento a anexar (panel secundario).  
5️⃣ Confirmar anexado en ventana de diálogo.  
6️⃣ *(Futuro)* Firmar digitalmente el documento.

---

## 🧠 Funcionalidades Futuras

- 🔜 **Firma Digital Criptográfica**: Certificados digitales.  
- 🎨 **Temas Claro/Oscuro**: Personalización visual.  
- 🗄️ **Conexión a Base de Datos**: Metadatos reales desde BD.  
- 🔔 **Sistema de Notificaciones**: Mejor feedback al usuario.  
- 🔄 **Gestión de Versiones**: Historial de cambios.

---

## ✅ Licencia

Este proyecto está bajo la licencia **AGPL-3.0**.  
Ver [LICENSE](LICENSE) para más detalles.
