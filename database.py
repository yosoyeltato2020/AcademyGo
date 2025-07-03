# database
import mysql.connector

DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "TuContraseñaSegura"  # <-- ¡CAMBIA ESTO!

DB_GENERAL = "academygo_admin"  # Aquí solo la tabla de academias

def conectar_admin():
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_GENERAL
    )
    return conn

def normalizar_nombre_db(nombre):
    return "academia_" + nombre.lower().replace(" ", "_")

def crear_bd_admin_si_no_existe():
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

    # Crear tabla con columna dbname si no existe
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
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=dbname
    )

def crear_tablas_academia(dbname):
    """
    Crea las tablas de usuarios y alumnos en la base de datos de la academia,
    y asegura que la tabla alumnos tiene los nuevos campos.
    """
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    # Tabla usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(50) UNIQUE,
            contrasena VARCHAR(255)
        )
    """)
    # Tabla alumnos con nuevos campos
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
    conn.commit()
    cursor.close()
    conn.close()

# --------- Comprobación al arrancar el programa ---------
if __name__ == "__main__":
    crear_bd_admin_si_no_existe()
    print("Base de datos y tabla de academias lista.")
