import mysql.connector

DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "TuContraseñaSegura"  # <-- ¡CAMBIA ESTO!

DB_GENERAL = "academygo_admin"  # Aquí solo la tabla de academias

def conectar_admin():
    """
    Conecta a la base de datos general de administración (solo lista de academias).
    """
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_GENERAL
    )
    return conn

def normalizar_nombre_db(nombre):
    """
    Convierte el nombre visual de la academia a nombre de base de datos ('Mi Academia' => 'academia_mi_academia').
    """
    return "academia_" + nombre.lower().replace(" ", "_")

def crear_bd_admin_si_no_existe():
    """
    Crea la base de datos de administración y la tabla 'academias' con columna dbname si no existen.
    Además, migra datos antiguos para que todos tengan dbname.
    """
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
    # --- Migración automática para academias antiguas sin dbname ---
    # Añadir la columna si no existe (idempotente)
    cursor.execute("SHOW COLUMNS FROM academias LIKE 'dbname'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE academias ADD COLUMN dbname VARCHAR(120) UNIQUE")
        conn.commit()
    # Rellenar dbname donde esté a NULL
    cursor.execute("SELECT id, nombre FROM academias WHERE dbname IS NULL OR dbname = ''")
    for aid, nombre in cursor.fetchall():
        dbname = normalizar_nombre_db(nombre)
        cursor.execute("UPDATE academias SET dbname=%s WHERE id=%s", (dbname, aid))
    conn.commit()
    cursor.close()
    conn.close()

def crear_bd_academia(nombre):
    """
    Crea una nueva base de datos para la academia y sus tablas.
    Registra su nombre visual y dbname en la tabla de academias (único punto de entrada).
    """
    dbname = normalizar_nombre_db(nombre)
    # Crear la base de datos de la academia
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
    # Crear tablas en la nueva base de datos
    crear_tablas_academia(dbname)
    # Registrar en la tabla de academias, si no existe ya ese nombre/dbname
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
    Conecta a la base de datos de una academia.
    """
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=dbname
    )

def crear_tablas_academia(dbname):
    """
    Crea las tablas de usuarios y alumnos en la base de datos de la academia.
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
    # Tabla alumnos
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
            curso VARCHAR(100)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# --------- Comprobación al arrancar el programa ---------
if __name__ == "__main__":
    crear_bd_admin_si_no_existe()
    print("Base de datos y tabla de academias lista.")
