import mysql.connector

DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "TuContraseñaSegura"  # <-- ¡CAMBIA ESTO!
DB_GENERAL = "academygo_admin"  # Aquí solo la tabla de academias

def conectar_admin():
    """
    Conecta a la base de datos administrativa (academygo_admin).
    """
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_GENERAL
    )

def normalizar_nombre_db(nombre):
    """
    Normaliza el nombre de una academia para crear el nombre de la base de datos.
    """
    return "academia_" + nombre.lower().replace(" ", "_")

def crear_bd_admin_si_no_existe():
    """
    Crea la base de datos administrativa y la tabla de academias si no existen.
    """
    # Crear la base de datos general si no existe
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_GENERAL} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    conn.commit()
    cursor.close()
    conn.close()

    # Crear la tabla de academias
    conn = conectar_admin()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS academias (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) UNIQUE,
            dbname VARCHAR(120) UNIQUE
        )
    """)
    conn.commit()
    # Normalizar posibles academias antiguas
    cursor.execute("SHOW COLUMNS FROM academias LIKE 'dbname'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE academias ADD COLUMN dbname VARCHAR(120) UNIQUE")
        conn.commit()
    cursor.execute("SELECT id, nombre FROM academias WHERE dbname IS NULL OR dbname = ''")
    for aid, nombre in cursor.fetchall():
        dbname = normalizar_nombre_db(nombre)
        cursor.execute("UPDATE academias SET dbname=%s WHERE id=%s", (dbname, aid))
    conn.commit()
    cursor.close()
    conn.close()

def crear_bd_academia(nombre):
    """
    Crea la base de datos de una academia (si no existe) y sus tablas iniciales.
    """
    dbname = normalizar_nombre_db(nombre)
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbname} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    conn.commit()
    cursor.close()
    conn.close()
    crear_tablas_academia(dbname)
    # Registrar academia en admin
    conn = conectar_admin()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM academias WHERE nombre=%s OR dbname=%s", (nombre, dbname))
    existe = cursor.fetchone()[0]
    if not existe:
        cursor.execute("INSERT INTO academias (nombre, dbname) VALUES (%s, %s)", (nombre, dbname))
        conn.commit()
    cursor.close()
    conn.close()
    return dbname

def conectar_academia(dbname):
    """
    Conecta a la base de datos de una academia concreta.
    """
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=dbname
    )

def crear_tablas_academia(dbname):
    """
    Crea todas las tablas necesarias en una base de datos de academia.
    """
    conn = conectar_academia(dbname)
    cursor = conn.cursor()

    # --- Tabla usuarios ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(50) UNIQUE,
            contrasena VARCHAR(255)
        )
    """)

    # --- Tabla alumnos ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100),
            apellidos VARCHAR(100),
            dni VARCHAR(20) UNIQUE,
            telefono VARCHAR(20),
            mail VARCHAR(100),
            fecha_nacimiento DATE,
            fecha_finalizacion DATE,
            curso VARCHAR(100),
            familia_curso VARCHAR(100),
            codigo_curso VARCHAR(30),
            estudios_completados VARCHAR(100),
            grado_curso INT,
            ocupacion VARCHAR(20)
        )
    """)
    # --- ALTER TABLE para añadir campos a tablas antiguas ---
    columnas_nuevas = [
        ("familia_curso", "VARCHAR(100)"),
        ("codigo_curso", "VARCHAR(30)"),
        ("estudios_completados", "VARCHAR(100)"),
        ("grado_curso", "INT"),
        ("ocupacion", "VARCHAR(20)")
    ]
    cursor.execute("SHOW COLUMNS FROM alumnos")
    existentes = {col[0] for col in cursor.fetchall()}
    for col, tipo in columnas_nuevas:
        if col not in existentes:
            cursor.execute(f"ALTER TABLE alumnos ADD COLUMN {col} {tipo} NULL")

    # --- Tabla profesores ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profesores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apellidos VARCHAR(100) NOT NULL,
            dni VARCHAR(20) UNIQUE,
            telefono VARCHAR(20),
            mail VARCHAR(100),
            fecha_nacimiento DATE,
            direccion VARCHAR(200),
            observaciones TEXT
        )
    """)
    # --- Tabla relación profesores-cursos (N:M) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profesores_cursos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            id_profesor INT NOT NULL,
            curso VARCHAR(100) NOT NULL,
            FOREIGN KEY (id_profesor) REFERENCES profesores(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

# ========== FUNCIONES CRUD PROFESORES Y RELACIÓN CURSOS ==========

def agregar_profesor(dbname, nombre, apellidos, dni, telefono, mail, fecha_nacimiento, direccion, observaciones):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO profesores (nombre, apellidos, dni, telefono, mail, fecha_nacimiento, direccion, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (nombre, apellidos, dni, telefono, mail, fecha_nacimiento, direccion, observaciones))
    conn.commit()
    prof_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return prof_id

def actualizar_profesor(dbname, id_profesor, nombre, apellidos, dni, telefono, mail, fecha_nacimiento, direccion, observaciones):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE profesores
        SET nombre=%s, apellidos=%s, dni=%s, telefono=%s, mail=%s,
            fecha_nacimiento=%s, direccion=%s, observaciones=%s
        WHERE id=%s
    """, (nombre, apellidos, dni, telefono, mail, fecha_nacimiento, direccion, observaciones, id_profesor))
    conn.commit()
    cursor.close()
    conn.close()

def borrar_profesor(dbname, id_profesor):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profesores WHERE id=%s", (id_profesor,))
    cursor.execute("DELETE FROM profesores_cursos WHERE id_profesor=%s", (id_profesor,))
    conn.commit()
    cursor.close()
    conn.close()

def obtener_profesores(dbname, filtro=""):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    if filtro:
        cursor.execute("""
            SELECT * FROM profesores
            WHERE nombre LIKE %s OR apellidos LIKE %s OR dni LIKE %s
            ORDER BY apellidos, nombre
        """, (f'%{filtro}%', f'%{filtro}%', f'%{filtro}%'))
    else:
        cursor.execute("SELECT * FROM profesores ORDER BY apellidos, nombre")
    profesores = cursor.fetchall()
    cursor.close()
    conn.close()
    return profesores

def asignar_cursos_a_profesor(dbname, id_profesor, lista_cursos):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    # Borra las relaciones antiguas
    cursor.execute("DELETE FROM profesores_cursos WHERE id_profesor=%s", (id_profesor,))
    # Añade las nuevas relaciones
    for curso in lista_cursos:
        cursor.execute(
            "INSERT INTO profesores_cursos (id_profesor, curso) VALUES (%s, %s)",
            (id_profesor, curso)
        )
    conn.commit()
    cursor.close()
    conn.close()

def obtener_cursos_de_profesor(dbname, id_profesor):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    cursor.execute("SELECT curso FROM profesores_cursos WHERE id_profesor=%s", (id_profesor,))
    cursos = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return cursos

def obtener_cursos_unicos_alumnos(dbname):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT curso FROM alumnos WHERE curso IS NOT NULL AND curso <> ''")
    cursos = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return cursos

# --------- Comprobación al arrancar el programa ---------
if __name__ == "__main__":
    crear_bd_admin_si_no_existe()
    print("Base de datos y tabla de academias lista.")

