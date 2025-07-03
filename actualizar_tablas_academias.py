from database import conectar_admin, crear_tablas_academia

def obtener_bases_academias():
    """
    Devuelve una lista de todos los nombres de bases de datos de academias registradas.
    """
    conn = conectar_admin()
    cursor = conn.cursor()
    cursor.execute("SELECT dbname FROM academias")
    bases = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return bases

if __name__ == "__main__":
    bases = obtener_bases_academias()
    print(f"Se encontraron {len(bases)} academias.")
    for dbname in bases:
        try:
            crear_tablas_academia(dbname)
            print(f"✔️  Academia '{dbname}' actualizada correctamente.")
        except Exception as e:
            print(f"❌ Error actualizando '{dbname}': {e}")
    print("¡Actualización completada para todas las academias!")
