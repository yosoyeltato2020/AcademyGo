from models import crear_usuario, agregar_alumno
from database import normalizar_nombre_db
import random
import datetime

# 1. El nombre de la academia en tu base de datos:
academia_nombre = "prueba"
dbname = normalizar_nombre_db(academia_nombre)

# 2. Crea tres usuarios por si quieres probar
usuarios = [
    ("admin", "admin"),
    ("profesor1", "clave1"),
    ("invitado", "1234"),
]
for usuario, clave in usuarios:
    try:
        crear_usuario(dbname, usuario, clave)
        print(f"Usuario {usuario} creado")
    except Exception as e:
        print(f"Usuario {usuario}: {e}")

# 3. Datos de ejemplo para los alumnos
nombres = ["Juan", "Lucía", "Carlos", "Ana", "Pedro", "Marta", "Luis", "Sara", "David", "Elena",
           "Jorge", "Paula", "Diego", "Sofía", "Miguel", "Noelia", "Raúl", "Carmen", "Rubén", "Irene"]
apellidos = ["García", "Martínez", "López", "Sánchez", "Pérez", "Gómez", "Díaz", "Ruiz", "Moreno", "Álvarez",
             "Jiménez", "Romero", "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Serrano", "Molina"]
cursos = ["Python Básico", "Excel Pro", "Inglés A2", "Word Experto", "Contabilidad", "Redes", "Mecánica", "Francés", "Matemáticas", "Química"]
familias = ["Informática", "Idiomas", "Administración", "Ciencias", "Mecánica"]
codigos = ["IFC0609", "ADG0108", "SSCE0110", "ELEE0109", "HOTR0108"]
estudios = ["ESO", "Bachillerato", "Grado Medio", "Grado Superior", "Universitario"]

# 4. Insertar 20 alumnos
for i in range(20):
    nombre = nombres[i]
    apellido = apellidos[i]
    dni = f"1234567{i}A"
    telefono = f"6001234{str(i).zfill(2)}"
    mail = f"{nombre.lower()}.{apellido.lower()}@ejemplo.com"
    # Fecha de nacimiento: entre 1990 y 2005
    anio_nac = random.randint(1990, 2005)
    mes_nac = random.randint(1, 12)
    dia_nac = random.randint(1, 28)
    fecha_nacimiento = datetime.date(anio_nac, mes_nac, dia_nac)
    # Fecha de finalización: aleatoria entre 2022 y 2025
    anio_fin = random.randint(2022, 2025)
    mes_fin = random.randint(1, 12)
    dia_fin = random.randint(1, 28)
    fecha_finalizacion = datetime.date(anio_fin, mes_fin, dia_fin)
    curso = random.choice(cursos)
    familia_curso = random.choice(familias)
    codigo_curso = random.choice(codigos)
    estudios_completados = random.choice(estudios)
    grado_curso = random.choice([1, 2, 3, 4])
    ocupacion = random.choice(["Empleado", "Desempleado"])

    try:
        agregar_alumno(
            dbname,
            nombre,
            apellido,
            dni,
            telefono,
            mail,
            fecha_nacimiento,
            fecha_finalizacion,
            curso,
            familia_curso,
            codigo_curso,
            estudios_completados,
            grado_curso,
            ocupacion
        )
        print(f"Alumno {nombre} {apellido} añadido")
    except Exception as e:
        print(f"Alumno {nombre} {apellido}: {e}")

print("Población de ejemplo finalizada.")
