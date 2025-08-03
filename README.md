🐺 Lycan Visualizador - Gestor de Expedientes Digitales
📢 Descripción General
Lycan Visualizador es una aplicación de escritorio diseñada para la gestión y manipulación de expedientes digitales en formato PDF dentro de un entorno organizacional. Su objetivo es centralizar y simplificar el flujo de trabajo diario de los operadores, permitiendo visualizar, anexar y firmar documentos de manera eficiente y segura.

El sistema se conecta a un servidor de archivos para obtener los expedientes, los presenta en una interfaz de usuario moderna tipo dashboard y provee las herramientas necesarias para su modificación, garantizando la integridad y el seguimiento de cada actuación.

🚀 Objetivos del Proyecto
🖥️ Centralizar la Visualización: Ofrecer una única interfaz para abrir y examinar expedientes PDF complejos.

📎 Simplificar el Anexado: Facilitar la tarea de añadir nueva documentación a un expediente existente a través de un visor comparativo.

✍️ Integrar Firma Digital: Implementar una solución robusta para la firma digital de documentos, asegurando su validez legal y trazabilidad.

⚙️ Optimizar el Flujo de Trabajo: Reducir los pasos manuales y el riesgo de error humano en la gestión documental.

🎨 Proveer una Interfaz Moderna: Desarrollar una GUI intuitiva y agradable que mejore la experiencia del usuario.

🧩 Características Destacadas
✔ Interfaz tipo Dashboard: Menú lateral desplegable para un acceso rápido a las funciones.
✔ Visor de PDF Dual: Permite visualizar el expediente principal y el documento a anexar lado a lado.
✔ Encabezado Dinámico: Muestra información clave del expediente cargado en tiempo real.
✔ Flujo de Anexo Guiado: Proceso claro para cargar, visualizar y confirmar el anexado de documentos.
✔ Conexión a Servidor: Diseñado para operar con archivos centralizados en un servidor FTP.
✔ Alta Personalización: El código está estructurado para ser fácilmente extensible y adaptable.

🛠️ Tecnologías Utilizadas
Categoría

Herramientas

Lenguaje

Python 3.12

GUI

PyQt6, PyQt6-WebEngine

Manipulación de PDF

PyMuPDF (fitz), pypdf

Conectividad

ftplib (en la lógica original)

📦 Instalación y Uso
1️⃣ Clonar el repositorio
git clone [https://github.com/TU_USUARIO/LycanVisualizador.git](https://github.com/TU_USUARIO/LycanVisualizador.git)
cd LycanVisualizador

2️⃣ Crear y activar entorno virtual
# Crear
python -m venv venv

# Activar en Windows
venv\Scripts\activate

3️⃣ Instalar dependencias
pip install -r requirements.txt

4️⃣ Ejecutar la aplicación
python run_app.py

📂 Estructura del Proyecto
LycanVisualizador/
│
├── assets/                # Iconos, imágenes y otros recursos
│
├── modules/               # Lógica de negocio y backend
│   └── pdf_tools.py       # Funciones para unir y firmar PDFs
│   └── ftp_client.py      # Lógica de conexión y transferencia FTP
│
├── ui/                    # Componentes de la interfaz gráfica
│   └── main_window.py     # Lógica de la ventana principal (Dashboard)
│   └── widgets/           # Widgets personalizados (visor, header, etc.)
│   └── main_window.ui     # (Opcional) Archivo de diseño de Qt Designer
│
├── run_app.py             # Script principal para ejecutar la aplicación
├── requirements.txt       # Dependencias del proyecto
└── README.md

🔍 Flujo de Trabajo Actual
1️⃣ Iniciar la aplicación.
2️⃣ Abrir un expediente desde el servidor (o localmente en la prueba).
3️⃣ Los datos del expediente se cargan en el encabezado principal.
4️⃣ Cargar un documento para anexar, que se muestra en un segundo panel.
5️⃣ Confirmar el anexado a través de una ventana de diálogo.
6️⃣ (Futuro) Seleccionar la opción de firmar el documento.

🧠 Funcionalidades Futuras
🔜 Firma Digital Criptográfica: Implementar firma con certificados digitales.

🎨 Temas Claro/Oscuro: Permitir al usuario cambiar la apariencia de la aplicación.

🗄️ Conexión a Base de Datos: Obtener los metadatos del expediente (Titular, etc.) desde una base de datos en lugar de simularlos.

🔔 Sistema de Notificaciones: Mejorar la retroalimentación al usuario con notificaciones integradas.

🔄 Gestión de Versiones: Guardar un historial de cambios o versiones de los expedientes.

✅ Licencia
Este proyecto está bajo la licencia MIT.
