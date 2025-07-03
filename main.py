# main.py
from database import crear_bd_admin_si_no_existe
from ui import pantalla_inicio

if __name__ == "__main__":
    crear_bd_admin_si_no_existe()   # Asegura la existencia de la DB central
    pantalla_inicio()
