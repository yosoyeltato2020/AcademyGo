contenido = """
# 🎓 AcademyGo · Gestión Profesional de Academias

**AcademyGo** es una aplicación de escritorio multiplataforma desarrollada en Python que permite gestionar de forma integral academias educativas. Desde el registro y seguimiento de alumnos hasta el envío de correos masivos, todo está pensado para facilitar la administración educativa de centros pequeños o medianos.

> Desarrollado con ❤️ por [PRACTICADORES.DEV](https://practicadores.dev)

---

## 🚀 Características Principales

- ✅ Gestión multi-academia con bases de datos separadas
- ✅ Registro y autenticación de usuarios
- ✅ Alta, edición, búsqueda avanzada y eliminación de alumnos
- ✅ Exportación a PDF / impresión directa del listado de alumnos
- ✅ Filtros por curso, edad, fechas, antigüedad y más
- ✅ Envío masivo de correos electrónicos desde la interfaz
- ✅ UI moderna con **Tkinter** y diseño responsivo

---

## 🏗️ Estructura del Proyecto

academygo/
├── main.py
├── database.py
├── models.py
├── ui.py
├── email_utils.py
├── email_dialog.py
├── busqueda_avanzada.py
└── academygo.png

---

## 🛠️ Requisitos

- Python 3.9 o superior
- MySQL Server (local o remoto)
- Módulos Python:

    pip install mysql-connector-python
    pip install reportlab
    pip install pillow

---

## ⚙️ Configuración inicial

1. Edita `database.py` con tus credenciales MySQL.
2. Ejecuta:

    python main.py

---

## 📧 Configurar envío de emails

Edita `email_utils.py` con tu usuario y clave SMTP (recomendada clave de aplicación para Gmail).

---

## 📄 Funcionalidades en desarrollo sugeridas

- [ ] Control de profesores y clases
- [ ] Gestión de asistencia
- [ ] Panel de estadísticas
- [ ] Exportación a Excel / CSV
- [ ] Roles y permisos (admin, profesor, etc.)
- [ ] Firma digital de documentos

---

## 🧠 Autor & Créditos

Este proyecto fue diseñado y desarrollado por **Ismael**  
Contacto: soporte@practicadores.dev

---

## 📝 Licencia

Distribuido bajo [MIT License](https://opensource.org/licenses/MIT)
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(contenido.strip())
print("README.md generado correctamente.")
