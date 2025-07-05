import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import smtplib

CONFIG_FILE = "config_email.json"
SMTP_DEFAULTS = {
    "SMTP_HOST": "smtp.gmail.com",
    "SMTP_PORT": 587,
    "SMTP_USER": "",
    "SMTP_PASS": ""
}

def cargar_config_email():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
        # Validar mínimos
        if all(k in data and data[k] for k in SMTP_DEFAULTS):
            return data
    return None

def guardar_config_email(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def ventana_config_smtp(parent=None):
    win = tk.Toplevel(parent)
    win.title("Configurar correo saliente")
    win.grab_set()
    win.geometry("420x320")
    win.resizable(False, False)
    win.configure(bg="#e9f0fb")
    style = ttk.Style(win)
    style.theme_use('clam')
    style.configure("TLabel", background="#e9f0fb", font=("Segoe UI", 11))
    style.configure("TButton", font=('Segoe UI', 10, 'bold'), background="#4a90e2")

    config = cargar_config_email() or SMTP_DEFAULTS.copy()

    campos = {}
    labels = [
        ("Servidor SMTP:", "SMTP_HOST"),
        ("Puerto:", "SMTP_PORT"),
        ("Usuario:", "SMTP_USER"),
        ("Contraseña:", "SMTP_PASS"),
    ]
    for i, (lbl, key) in enumerate(labels):
        ttk.Label(win, text=lbl, style="TLabel").place(x=40, y=34+44*i)
        campo = ttk.Entry(win, width=30, font=("Segoe UI", 11))
        if key == "SMTP_PASS":
            campo.config(show="*")
        campo.place(x=180, y=34+44*i)
        campo.insert(0, str(config.get(key, "")))
        campos[key] = campo

    def guardar_y_probar():
        smtp_host = campos["SMTP_HOST"].get().strip()
        smtp_port = campos["SMTP_PORT"].get().strip()
        smtp_user = campos["SMTP_USER"].get().strip()
        smtp_pass = campos["SMTP_PASS"].get().strip()
        # Validación básica
        if not smtp_host or not smtp_port or not smtp_user or not smtp_pass:
            messagebox.showerror("Faltan datos", "Completa todos los campos.", parent=win)
            return
        try:
            smtp_port = int(smtp_port)
        except Exception:
            messagebox.showerror("Puerto inválido", "El puerto debe ser un número.", parent=win)
            return
        # Probar conexión SMTP (con TLS típico)
        try:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=8)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.quit()
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar con estos datos:\n\n{e}", parent=win)
            return
        # Guardar configuración
        guardar_config_email({
            "SMTP_HOST": smtp_host,
            "SMTP_PORT": smtp_port,
            "SMTP_USER": smtp_user,
            "SMTP_PASS": smtp_pass
        })
        messagebox.showinfo("Correcto", "Configuración guardada y verificada correctamente.", parent=win)
        win.destroy()

    ttk.Button(win, text="Guardar y Probar", command=guardar_y_probar).place(x=85, y=230)
    ttk.Button(win, text="Cancelar", command=win.destroy).place(x=245, y=230)
    win.wait_window()
