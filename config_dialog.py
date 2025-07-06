# config_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import mysql.connector

CONFIG_FILE = "config_db.json"

def guardar_config_db(host, user, password):
    config = {
        "host": host,
        "user": user,
        "password": password
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def cargar_config_db():
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return config
    except Exception:
        return None

def mostrar_configuracion_db():
    """
    Lanza una ventana modal para configurar la conexión a la base de datos.
    Devuelve True si se guardó correctamente, False si se canceló.
    """
    resultado = {"ok": False}
    root = tk.Tk()
    root.withdraw()  # Oculta ventana raíz

    win = tk.Toplevel()
    win.title("Configuración de la Base de Datos")
    win.geometry("380x270")
    win.resizable(False, False)
    win.grab_set()
    win.focus_force()
    win.configure(bg="#eaf3fc")

    ttk.Label(win, text="Configuración de Base de Datos", font=("Segoe UI", 14, "bold")).pack(pady=(17, 6))
    frame = ttk.Frame(win, padding=12)
    frame.pack(expand=True, fill="both")

    ttk.Label(frame, text="Host (servidor):").grid(row=0, column=0, sticky="e", padx=7, pady=7)
    entry_host = ttk.Entry(frame)
    entry_host.grid(row=0, column=1, padx=7, pady=7)
    entry_host.insert(0, "localhost")

    ttk.Label(frame, text="Usuario:").grid(row=1, column=0, sticky="e", padx=7, pady=7)
    entry_user = ttk.Entry(frame)
    entry_user.grid(row=1, column=1, padx=7, pady=7)
    entry_user.insert(0, "root")

    ttk.Label(frame, text="Contraseña:").grid(row=2, column=0, sticky="e", padx=7, pady=7)
    entry_pass = ttk.Entry(frame, show="*")
    entry_pass.grid(row=2, column=1, padx=7, pady=7)

    def probar_conexion():
        host = entry_host.get().strip()
        user = entry_user.get().strip()
        password = entry_pass.get().strip()
        try:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password
            )
            conn.close()
            messagebox.showinfo("Correcto", "Conexión exitosa.", parent=win)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar:\n{e}", parent=win)

    def guardar():
        host = entry_host.get().strip()
        user = entry_user.get().strip()
        password = entry_pass.get().strip()
        if not host or not user:
            messagebox.showwarning("Campos requeridos", "Debes indicar host y usuario.", parent=win)
            return
        try:
            # Probamos conexión antes de guardar
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password
            )
            conn.close()
            guardar_config_db(host, user, password)
            messagebox.showinfo("Guardado", "Configuración guardada correctamente.", parent=win)
            resultado["ok"] = True
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar:\n{e}", parent=win)

    def cancelar():
        if messagebox.askyesno("Cancelar", "¿Cancelar la configuración?\nEl programa se cerrará.", parent=win):
            win.destroy()

    btns = ttk.Frame(win)
    btns.pack(pady=16)
    ttk.Button(btns, text="Probar conexión", command=probar_conexion).pack(side="left", padx=8)
    ttk.Button(btns, text="Guardar", command=guardar).pack(side="left", padx=8)
    ttk.Button(btns, text="Cancelar", command=cancelar).pack(side="left", padx=8)

    win.protocol("WM_DELETE_WINDOW", cancelar)
    win.wait_window()
    root.destroy()
    return resultado["ok"]
