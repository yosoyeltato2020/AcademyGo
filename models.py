from database import (
    conectar_admin,
    conectar_academia,
    crear_bd_admin_si_no_existe,
    crear_bd_academia,
    normalizar_nombre_db,
)

# --------------------- Academias ---------------------
def listar_academias():
    """
    Devuelve lista de (nombre_visible, dbname) de academias.
    """
    conn = conectar_admin()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, dbname FROM academias ORDER BY nombre")
    academias = cursor.fetchall()
    cursor.close()
    conn.close()
    return academias  # [(nombre_visible, dbname), ...]

def crear_academia(nombre):
    """
    Crea academia (tabla admin y base datos) y devuelve dbname.
    NO duplica registros si ya existe (por nombre o dbname).
    """
    dbname = normalizar_nombre_db(nombre)
    conn = conectar_admin()
    cursor = conn.cursor()
    # ¿Ya existe academia con ese nombre o dbname?
    cursor.execute("SELECT id FROM academias WHERE nombre=%s OR dbname=%s", (nombre, dbname))
    res = cursor.fetchone()
    if res is None:
        # Insertar solo si no existe
        cursor.execute("INSERT INTO academias (nombre, dbname) VALUES (%s, %s)", (nombre, dbname))
        conn.commit()
        # Crear la base de datos y tablas
        crear_bd_academia(nombre)
    cursor.close()
    conn.close()
    return dbname

# --------------------- Usuarios ---------------------
def crear_usuario(dbname, usuario, contrasena):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (%s, %s)", (usuario, contrasena))
    conn.commit()
    cursor.close()
    conn.close()

def autenticar_usuario(dbname, usuario, contrasena):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE usuario=%s AND contrasena=%s", (usuario, contrasena))
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return res is not None

def listar_usuarios(dbname):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario FROM usuarios ORDER BY usuario")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return usuarios

# --------------------- Alumnos ---------------------
def agregar_alumno(dbname, nombre, apellidos, dni, telefono, mail, fecha_nac, fecha_fin, curso):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alumnos (nombre, apellidos, dni, telefono, mail, fecha_nacimiento, fecha_finalizacion, curso)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (nombre, apellidos, dni, telefono, mail, fecha_nac, fecha_fin, curso))
    conn.commit()
    cursor.close()
    conn.close()

def actualizar_alumno(dbname, id_alumno, nombre, apellidos, dni, telefono, mail, fecha_nac, fecha_fin, curso):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE alumnos SET nombre=%s, apellidos=%s, dni=%s, telefono=%s, mail=%s, fecha_nacimiento=%s, fecha_finalizacion=%s, curso=%s
        WHERE id=%s
    """, (nombre, apellidos, dni, telefono, mail, fecha_nac, fecha_fin, curso, id_alumno))
    conn.commit()
    cursor.close()
    conn.close()

def borrar_alumno(dbname, id_alumno):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM alumnos WHERE id=%s", (id_alumno,))
    conn.commit()
    cursor.close()
    conn.close()

def obtener_alumnos(dbname, filtro=""):
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    if filtro:
        cursor.execute("SELECT * FROM alumnos WHERE nombre LIKE %s OR apellidos LIKE %s ORDER BY apellidos, nombre", (f'%{filtro}%', f'%{filtro}%'))
    else:
        cursor.execute("SELECT * FROM alumnos ORDER BY apellidos, nombre")
    alumnos = cursor.fetchall()
    cursor.close()
    conn.close()
    return alumnos

def filtrar_alumnos_avanzado(
    dbname, nombre="", apellidos="", fecha_nac_desde=None, fecha_nac_hasta=None,
    curso="", fecha_fin_desde=None, fecha_fin_hasta=None
):
    # Permite hacer búsquedas avanzadas por los campos principales
    sql = "SELECT * FROM alumnos WHERE 1=1"
    params = []
    if nombre:
        sql += " AND nombre LIKE %s"
        params.append(f'%{nombre}%')
    if apellidos:
        sql += " AND apellidos LIKE %s"
        params.append(f'%{apellidos}%')
    if fecha_nac_desde:
        sql += " AND fecha_nacimiento >= %s"
        params.append(fecha_nac_desde)
    if fecha_nac_hasta:
        sql += " AND fecha_nacimiento <= %s"
        params.append(fecha_nac_hasta)
    if curso:
        sql += " AND curso LIKE %s"
        params.append(f'%{curso}%')
    if fecha_fin_desde:
        sql += " AND fecha_finalizacion >= %s"
        params.append(fecha_fin_desde)
    if fecha_fin_hasta:
        sql += " AND fecha_finalizacion <= %s"
        params.append(fecha_fin_hasta)
    sql += " ORDER BY apellidos, nombre"
    conn = conectar_academia(dbname)
    cursor = conn.cursor()
    cursor.execute(sql, tuple(params))
    alumnos = cursor.fetchall()
    cursor.close()
    conn.close()
    return alumnos
