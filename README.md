# 🐺 Lycan Visualizador - Gestor de Expedientes Digitales

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green?logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-PDF-orange)](https://pymupdf.readthedocs.io/)
[![pypdf](https://img.shields.io/badge/pypdf-PDF-red)](https://pypdf.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📢 Descripción General

**Lycan Visualizador** es una aplicación de escritorio diseñada para la gestión y manipulación de expedientes digitales en formato PDF dentro de un entorno organizacional.  
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

1️⃣ **Clonar el repositorio**
```bash
git clone https://github.com/TU_USUARIO/LycanVisualizador.git
cd LycanVisualizador
