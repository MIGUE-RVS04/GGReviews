# Catálogo y Reseñas de Videojuegos 🎮

Una aplicación web desarrollada en Python con Flask y MySQL que permite explorar un catálogo de videojuegos, ver sus detalles, filtrar por plataformas, registrarse y publicar reseñas. Además, cuenta con un panel de administración para gestionar el contenido de la plataforma.

## ✨ Características

- **Catálogo de Videojuegos:** Explora juegos con sus respectivos desarrolladores y plataformas.
- **Sistema de Usuarios:** Registro, inicio de sesión y gestión de sesiones seguras usando `werkzeug.security`.
- **Reseñas y Calificaciones:** Los usuarios autenticados pueden dejar calificaciones (1 a 5) y comentarios en los juegos.
- **Panel de Control de Usuario (Dashboard):** Los usuarios pueden ver y eliminar sus propias reseñas.
- **Panel de Administración:** Un área exclusiva para administradores donde pueden:
  - Añadir y editar videojuegos, plataformas y desarrolladores.
  - Asignar imágenes mediante URLs a juegos y plataformas.
  - Promover a otros usuarios al rol de administrador.
  - Moderar (eliminar) cualquier reseña de la plataforma.

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python, Flask
- **Base de Datos:** MySQL (conector `mysql-connector-python`)
- **Frontend:** HTML, CSS (plantillas Jinja2)

## 🚀 Instalación y Configuración

Sigue estos pasos para preparar y ejecutar el proyecto en tu entorno local:

### 1. Preparar el entorno

Accede a la carpeta del proyecto. Se recomienda crear y activar un entorno virtual:

```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

### 2. Instalar dependencias

Instala las librerías necesarias de Python:

```bash
pip install Flask mysql-connector-python werkzeug
```

### 3. Configurar la Base de Datos MySQL

1. Crea una base de datos en tu servidor MySQL (por defecto el proyecto se conecta a la base de datos `flask-db`).
2. Importa la estructura base ejecutando el contenido del archivo `sql.sql` en tu gestor de base de datos MySQL (phpMyAdmin, MySQL Workbench, o consola).
3. **¡Importante!** Edita las credenciales de conexión (host, usuario, contraseña y base de datos) en los siguientes archivos para que apunten a tu servidor local o remoto:
   - `app.py`
   - `seed.py`
   - `upgrade_admin.py`
   - `upgrade_image.py`
   - `upgrade_plat_img.py`

### 4. Poblar y actualizar la Base de Datos

El proyecto incluye scripts para rellenar la base de datos con datos de prueba y actualizar la estructura inicial. Te recomendamos registrar primero un usuario desde la aplicación web antes de ejecutar el script de administrador.

```bash
# 1. Sembrar datos de prueba (Juegos, plataformas y desarrolladores)
python seed.py

# 2. Agregar soporte para permisos de administrador
# Nota: Este script promoverá automáticamente al PRIMER usuario registrado a administrador.
python upgrade_admin.py (No obligatorio de hacer)

# 3. Agregar soporte para imágenes (URLs) en los videojuegos
python upgrade_image.py (No obligatorio de hacer)

# 4. Agregar soporte para imágenes (URLs) en las plataformas
python upgrade_plat_img.py (No obligatorio de hacer)
```

### 5. Ejecutar la aplicación

Una vez configurado todo, inicia el servidor de desarrollo de Flask:

```bash
python app.py
```

La aplicación estará disponible en tu navegador en `http://localhost:8080` (o `http://127.0.0.1:8080`).

## 📂 Estructura del Proyecto

- `app.py`: Archivo principal de la aplicación, contiene todas las rutas, lógica de la aplicación y la conexión a base de datos.
- `sql.sql`: Script con la estructura inicial de tablas de la base de datos.
- `seed.py`: Script para poblar la base de datos de forma automática con información de prueba.
- `upgrade_*.py`: Scripts de migración para añadir nuevas columnas a la base de datos que no estaban en el esquema original.
- `templates/`: Carpeta con las vistas HTML (Admin, Dashboard, Index, Login, Register, etc.).
- `static/`: Carpeta con los archivos estáticos de estilos CSS, imágenes y scripts del frontend.
