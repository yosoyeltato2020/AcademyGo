# ui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
from models import (
    listar_academias, crear_academia,
    autenticar_usuario, crear_usuario,
    agregar_alumno, actualizar_alumno, borrar_alumno, obtener_alumnos,
)
from busqueda_avanzada import abrir_busqueda_avanzada
from email_dialog import ventana_redactar_email
from profesores import ventana_gestion_profesores
from email_utils import enviar_email_masivo
import platform
import math
import datetime
import webbrowser
import tempfile
import os
import pandas as pd
from tkinter import filedialog
import subprocess

def backup_base_datos(dbname, user, password, parent=None):
    archivo = filedialog.asksaveasfilename(
        defaultextension=".sql",
        filetypes=[("SQL files", "*.sql")],
        title="Guardar copia de seguridad",
        parent=parent
    )
    if not archivo:
        return

    comando = [
        "mysqldump",
        f"-u{user}",
        f"-p{password}",
        dbname
    ]
    try:
        with open(archivo, "w") as f:
            subprocess.run(comando, stdout=f, check=True)
        messagebox.showinfo("Backup", f"Copia de seguridad guardada en:\n{archivo}", parent=parent)
    except Exception as e:
        messagebox.showerror("Backup", f"Error al crear backup:\n{e}", parent=parent)

def restaurar_base_datos(dbname, user, password, parent=None):
    archivo = filedialog.askopenfilename(
        filetypes=[("SQL files", "*.sql")],
        title="Selecciona archivo SQL para restaurar",
        parent=parent
    )
    if not archivo:
        return

    comando = [
        "mysql",
        f"-u{user}",
        f"-p{password}",
        dbname
    ]
    try:
        with open(archivo, "r") as f:
            subprocess.run(comando, stdin=f, check=True)
        messagebox.showinfo("Restaurar", f"Base de datos restaurada desde:\n{archivo}", parent=parent)
    except Exception as e:
        messagebox.showerror("Restaurar", f"Error al restaurar:\n{e}", parent=parent)


TAB_COLOR = "#e9f0fb"

# --------- Pantalla Inicial: selección de academia y login/registro ----------
def pantalla_inicio():
    root = tk.Tk()
    root.title("AcademyGo - Gestión de Academias")
    root.configure(bg="#375aab")
    root.geometry("920x840")
    root.minsize(650, 730)  # Puedes ajustar si quieres más espacio

    # -------- Header superior -----------
    header_frame = tk.Frame(root, bg="#375aab")
    header_frame.pack(fill='x', pady=(36, 0))
    canvas = tk.Canvas(header_frame, width=230, height=145, bg="#375aab", highlightthickness=0)
    canvas.pack()
    _animar_prisma(canvas, scale=1.08, offset_x=115, offset_y=80)

    # Título y subtítulo
    tk.Label(root, text="AcademyGo", bg="#375aab", fg="white", font=("Segoe UI", 33, "bold")).pack(pady=(7, 0))
    tk.Label(root, text="Gestión de Academias", bg="#375aab", fg="#c7e0fa", font=("Segoe UI", 18, "italic")).pack(pady=(0, 19))

    main_frame = tk.Frame(root, bg="#375aab")
    main_frame.pack(pady=6)

    # --- Cargar academias y preparar mappings
    lista_academias = listar_academias()  # [(nombre, dbname)]
    nombres = [a[0] for a in lista_academias]
    mapping = {a[0]: a[1] for a in lista_academias}  # nombre_visible -> dbname

    # Selección de academia
    frame_academia = tk.Frame(main_frame, bg="#375aab")
    frame_academia.pack(pady=9)
    tk.Label(frame_academia, text="Academia:", bg="#375aab", fg="white", font=("Segoe UI", 14)).grid(row=0, column=0, padx=7, pady=7, sticky="e")
    cb_academia = ttk.Combobox(frame_academia, values=nombres, width=27, font=("Segoe UI", 14), state="readonly")
    cb_academia.grid(row=0, column=1, padx=10, pady=8)
    ttk.Button(frame_academia, text="Nueva academia", command=lambda: nueva_academia()).grid(row=0, column=2, padx=12)

    def refrescar_academias():
        nuevas = listar_academias()
        nombres_new = [a[0] for a in nuevas]
        mapping.clear()
        mapping.update({a[0]: a[1] for a in nuevas})
        cb_academia["values"] = nombres_new
        if nombres_new:
            cb_academia.set(nombres_new[0])

    def nueva_academia():
        nombre = simpledialog.askstring("Nueva Academia", "Introduce el nombre de la nueva academia:")
        if nombre:
            crear_academia(nombre)
            refrescar_academias()
            cb_academia.set(nombre)
            messagebox.showinfo("Academia", f"Academia '{nombre}' creada correctamente.")

    # --- Login/registro usuario
    frame_login = tk.Frame(main_frame, bg="#375aab")
    frame_login.pack(pady=(28, 10))
    tk.Label(frame_login, text="Usuario:", bg="#375aab", fg="white", font=("Segoe UI", 14)).grid(row=0, column=0, padx=10, pady=11, sticky="e")
    entry_usuario = ttk.Entry(frame_login, width=26, font=("Segoe UI", 14))
    entry_usuario.grid(row=0, column=1, padx=10, pady=6)
    tk.Label(frame_login, text="Contraseña:", bg="#375aab", fg="white", font=("Segoe UI", 14)).grid(row=1, column=0, padx=10, pady=11, sticky="e")
    entry_contra = ttk.Entry(frame_login, show="*", width=26, font=("Segoe UI", 14))
    entry_contra.grid(row=1, column=1, padx=10, pady=6)

    def registrar():
        nombre_acad = cb_academia.get()
        usuario = entry_usuario.get()
        contra = entry_contra.get()
        if not nombre_acad or not usuario or not contra:
            messagebox.showwarning("Registro", "Selecciona academia e introduce usuario y contraseña.")
            return
        dbname = mapping.get(nombre_acad)
        if not dbname:
            messagebox.showerror("Error", "Academia no válida.")
            return
        try:
            crear_usuario(dbname, usuario, contra)
            messagebox.showinfo("Registro", f"Usuario '{usuario}' registrado correctamente en {nombre_acad}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def login():
        nombre_acad = cb_academia.get()
        usuario = entry_usuario.get()
        contra = entry_contra.get()
        if not nombre_acad or not usuario or not contra:
            messagebox.showwarning("Login", "Selecciona academia e introduce usuario y contraseña.")
            return
        dbname = mapping.get(nombre_acad)
        if not dbname:
            messagebox.showerror("Error", "Academia no válida.")
            return
        ok = autenticar_usuario(dbname, usuario, contra)
        if ok:
            root.destroy()
            pantalla_principal(dbname, usuario)
        else:
            messagebox.showerror("Login incorrecto", "Usuario o contraseña incorrectos.")

    btns_login = tk.Frame(main_frame, bg="#375aab")
    btns_login.pack(pady=(6, 18))
    ttk.Button(btns_login, text="Registrar usuario", command=registrar).pack(side='left', padx=22)
    ttk.Button(btns_login, text="Iniciar sesión", command=login).pack(side='left', padx=22)

    # ---- Footer profesional (ayuda, contacto, sobre, soporte) ----
    ttk.Separator(root, orient='horizontal').pack(fill='x', padx=38, pady=(7, 1))
    footer = tk.Frame(root, bg="#375aab")
    footer.pack(side='bottom', fill='x', pady=(18, 0))

    def _abrir_ayuda():
        messagebox.showinfo("Ayuda AcademyGo", "Guía rápida:\n\n"
            "1. Selecciona tu academia o crea una nueva.\n"
            "2. Registra tu usuario o inicia sesión.\n"
            "3. Gestiona los alumnos y sus cursos fácilmente.\n\n"
            "¿Dudas? Contacta soporte en el botón 'Contacto' o consulta el manual en línea.")

    def _abrir_contacto():
        webbrowser.open_new_tab("mailto:soporte@practicadores.dev?subject=Soporte%20AcademyGo")

    def _abrir_sobre():
        messagebox.showinfo("Sobre AcademyGo", "AcademyGo\n\n"
            "Desarrollado por PRACTICADORES.DEV\n"
            "Versión 2025. Todos los derechos reservados.\n"
            "Más info: https://practicadores.dev")

    def _abrir_soporte():
        webbrowser.open_new_tab("https://practicadores.dev/soporte")

    btn_footer = tk.Frame(footer, bg="#375aab")
    btn_footer.pack(pady=6)
    ttk.Button(btn_footer, text="Ayuda", command=_abrir_ayuda).pack(side='left', padx=11)
    ttk.Button(btn_footer, text="Contacto", command=_abrir_contacto).pack(side='left', padx=11)
    ttk.Button(btn_footer, text="Sobre", command=_abrir_sobre).pack(side='left', padx=11)
    ttk.Button(btn_footer, text="Soporte", command=_abrir_soporte).pack(side='left', padx=11)

    tk.Label(root, text="Desarrollado por PRACTICADORES.DEV", bg="#375aab", fg="#c7e0fa", font=("Segoe UI", 11, "italic")).pack(side="bottom", pady=8)
    root.mainloop()


# --------- Interfaz principal: pestaña alumnos + acciones ---------
def pantalla_principal(dbname, usuario):
    root = tk.Tk()
    root.title(f"AcademyGo - {dbname} (Usuario: {usuario})")
    root.configure(bg=TAB_COLOR)
    root.geometry("1080x700")
    if platform.system() == "Windows":
        root.state('zoomed')
    else:
        try:
            root.attributes('-zoomed', True)
        except:
            pass

    # Header y prisma
    header = tk.Frame(root, bg="#375aab", height=72)
    header.pack(fill='x', side='top')
    logo_img = Image.open("academygo.png").resize((50, 50), Image.LANCZOS)
    logo_tk = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(header, image=logo_tk, bg="#375aab")
    logo_label.image = logo_tk
    logo_label.pack(side="left", padx=18, pady=8)
    tk.Label(header, text="AcademyGo", bg="#375aab", fg="white", font=("Segoe UI", 23, "bold")).pack(side="left", padx=10)
    tk.Label(header, text="Gestión profesional", bg="#375aab", fg="#c7e0fa", font=("Segoe UI", 15, "italic")).pack(side="left", padx=8, pady=16)
    canvas = tk.Canvas(header, width=88, height=72, bg="#375aab", highlightthickness=0)
    canvas.pack(side="right", padx=18)
    _animar_prisma(canvas, scale=0.47, offset_x=44, offset_y=38)

    # Pestaña alumnos
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=12, pady=12)
    tab_alumnos = tk.Frame(notebook, bg=TAB_COLOR)
    notebook.add(tab_alumnos, text="Alumnos")
    contenido_alumnos(tab_alumnos, dbname, root)

    # Botones de acciones principales
    botones = tk.Frame(root, bg=TAB_COLOR)
    botones.pack(pady=(10, 0))
    ttk.Button(botones, text="Búsqueda avanzada", command=lambda: abrir_busqueda_avanzada(dbname, root)).pack(side='left', padx=16)
    ttk.Button(botones, text="Imprimir", command=lambda: imprimir_alumnos(dbname)).pack(side='left', padx=16)
    ttk.Button(botones, text="Exportar PDF", command=lambda: exportar_pdf(dbname)).pack(side='left', padx=16)
    ttk.Button(botones, text="Profesores", command=lambda: ventana_gestion_profesores(dbname, root)).pack(side='left', padx=16)  # <--- AQUÍ
    ttk.Button(botones, text="Cerrar sesión", command=lambda: [root.destroy(), pantalla_inicio()]).pack(side='left', padx=16)
    # ... (el resto igual)


    # Usuario y contraseña de la BD para el backup
    DB_USER = "root"
    DB_PASS = "TuContraseñaSegura"  # <-- pon tu password real

    ttk.Button(botones, text="Backup BD", command=lambda: backup_base_datos(dbname, DB_USER, DB_PASS, root)).pack(side='left', padx=16)
    ttk.Button(botones, text="Restaurar BD", command=lambda: restaurar_base_datos(dbname, DB_USER, DB_PASS, root)).pack(side='left', padx=16)

    tk.Label(root, text="© 2025 PRACTICADORES.DEV", bg=TAB_COLOR, fg="#375aab", font=("Segoe UI", 11, "italic")).pack(side='bottom', pady=4)
    root.mainloop()

def importar_alumnos_desde_excel(dbname, cargar_y_actualizar, parent):
    file_path = filedialog.askopenfilename(
        parent=parent,
        title="Selecciona archivo Excel o CSV",
        filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("CSV", "*.csv"), ("Todos", "*.*")]
    )
    if not file_path:
        return

    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el archivo: {e}", parent=parent)
        return

    columnas_archivo = list(df.columns)
    campos_bd = [
        'Nombre', 'Apellidos', 'DNI', 'Teléfono', 'Mail',
        'Fecha nacimiento', 'Fecha finalización', 'Curso',
        'Familia curso', 'Código curso', 'Estudios completados', 'Grado curso', 'Ocupación'
    ]

    ventana_map = tk.Toplevel(parent)
    ventana_map.title("Asociar columnas")
    ventana_map.geometry("480x540")
    asignaciones = {}
    for i, campo in enumerate(campos_bd):
        ttk.Label(ventana_map, text=f"{campo}").grid(row=i, column=0, padx=7, pady=4, sticky='e')
        var = tk.StringVar()
        cb = ttk.Combobox(ventana_map, textvariable=var, values=[""] + columnas_archivo, width=26, state="readonly")
        cb.grid(row=i, column=1, padx=7, pady=4)
        asignaciones[campo] = var

    def ejecutar_importacion():
        mapeo = {campo: var.get() for campo, var in asignaciones.items()}
        # Validación de campos obligatorios
        if not mapeo['Nombre'] or not mapeo['Apellidos']:
            messagebox.showwarning("Campos obligatorios", "Debes asignar las columnas de Nombre y Apellidos.", parent=ventana_map)
            return
        count_ok, count_fail = 0, 0
        for idx, row in df.iterrows():
            datos = []
            for campo in campos_bd:
                col = mapeo[campo]
                if col:
                    val = row.get(col, "")
                    # Parsear fechas si el campo tiene "fecha"
                    if "fecha" in campo.lower() and val:
                        try:
                            if isinstance(val, str):
                                val = pd.to_datetime(val, dayfirst=True, errors='coerce').date()
                            else:
                                val = val.date()
                        except Exception:
                            val = None
                    datos.append(val)
                else:
                    datos.append("")
            try:
                agregar_alumno(dbname, *datos)
                count_ok += 1
            except Exception:
                count_fail += 1
        ventana_map.destroy()
        cargar_y_actualizar()
        messagebox.showinfo(
            "Importación completada",
            f"Alumnos importados: {count_ok}\nFallidos: {count_fail}",
            parent=parent
        )

    ttk.Button(ventana_map, text="Importar", command=ejecutar_importacion).grid(row=len(campos_bd)+1, column=1, pady=18)

# --------- Contenido de la pestaña de alumnos ---------
def contenido_alumnos(tab, dbname, root):
    # Colores y estilos personalizados
    BG_FORM = "#eaf3fc"
    BG_TAB = "#e6f2ff"
    BG_HEADER = "#375aab"
    COLOR_LABEL = "#234b80"
    COLOR_FONDO = "#e7f0fb"

    frame = ttk.Frame(tab, padding=18, style="Custom.TFrame")
    frame.pack(fill='both', expand=True, padx=24, pady=16)
    root.configure(bg=COLOR_FONDO)
    tab.configure(bg=COLOR_FONDO)

    style = ttk.Style()
    style.theme_use('default')
    style.configure("Custom.TFrame", background=BG_FORM)
    style.configure("Custom.TLabel", background=BG_FORM, foreground=COLOR_LABEL, font=('Segoe UI', 11))
    style.configure("Custom.TLabelframe", background=BG_FORM, foreground=COLOR_LABEL)
    style.configure("Custom.Treeview", background=BG_TAB, fieldbackground=BG_TAB, font=('Segoe UI', 11))
    style.configure("Custom.Treeview.Heading", background=BG_HEADER, foreground="white", font=('Segoe UI', 11, "bold"))
    style.map('TButton', background=[('active', BG_HEADER), ('!active', BG_HEADER)])

    # Etiquetas y campos (añade aquí tus campos extra)
    labels = [
        'Nombre', 'Apellidos', 'DNI', 'Teléfono', 'Mail',
        'Fecha nacimiento (dd-mm-yyyy)', 'Fecha finalización (dd-mm-yyyy)', 'Curso',
        'Familia curso', 'Código curso', 'Estudios completados', 'Grado curso', 'Ocupación'
    ]
    keys = [
        'nombre', 'apellidos', 'dni', 'telefono', 'mail',
        'fecha_nac', 'fecha_fin', 'curso',
        'familia_curso', 'codigo_curso', 'estudios_completados', 'grado_curso', 'ocupacion'
    ]
    campos = {}

    form = ttk.LabelFrame(frame, text="Datos del Alumno", padding=(18, 10), style="Custom.TLabelframe")
    form.grid(row=0, column=0, sticky='nw', rowspan=3, pady=10)

    # Campos normales + desplegables
    for i, (label, key) in enumerate(zip(labels, keys)):
        ttk.Label(form, text=label + ":", anchor='w', style="Custom.TLabel").grid(row=i, column=0, pady=4, sticky='e')
        if key == "grado_curso":
            campo = ttk.Combobox(form, values=[1, 2, 3, 4], width=22, state="readonly")
        elif key == "ocupacion":
            campo = ttk.Combobox(form, values=["Empleado", "Desempleado"], width=22, state="readonly")
        else:
            campo = ttk.Entry(form, width=24, font=('Segoe UI', 12))
        campo.grid(row=i, column=1, pady=4, padx=7, sticky='w')
        campos[key] = campo

    # Botones CRUD
    btns = ttk.Frame(form, style="Custom.TFrame")
    btns.grid(row=len(labels), column=0, columnspan=2, pady=(14, 7))

    def limpiar_formulario():
        for key, campo in campos.items():
            if key in ["grado_curso", "ocupacion"]:
                campo.set("")
            else:
                campo.delete(0, tk.END)

    pagina_actual = [0]
    PAGINA_TAMANO = 25

    def cargar_y_actualizar():
        for fila in tree.get_children():
            tree.delete(fila)
        alumnos = obtener_alumnos(dbname)
        inicio = pagina_actual[0] * PAGINA_TAMANO
        fin = inicio + PAGINA_TAMANO
        alumnos_pagina = alumnos[inicio:fin]
        for i, alumno in enumerate(alumnos_pagina):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert('', tk.END, values=alumno, tags=(tag,))
        tree.tag_configure('evenrow', background='#eaf3fc')
        tree.tag_configure('oddrow', background='#d6e6f5')
        max_pagina = max(0, (len(alumnos) - 1) // PAGINA_TAMANO)
        btn_ant.config(state=tk.NORMAL if pagina_actual[0] > 0 else tk.DISABLED)
        btn_sig.config(state=tk.NORMAL if pagina_actual[0] < max_pagina else tk.DISABLED)
        lbl_pag.config(text=f"Página {pagina_actual[0]+1} de {max_pagina+1}")

    def guardar():
        vals = []
        for key in keys:
            v = campos[key].get() if hasattr(campos[key], 'get') else ""
            vals.append(v)
        if not vals[0] or not vals[1]:
            messagebox.showwarning("Atención", "Nombre y apellidos obligatorios.")
            return
        try:
            fecha_nac_db = _parse_fecha(vals[5])
            fecha_fin_db = _parse_fecha(vals[6]) if vals[6] else None
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto (usa dd-mm-yyyy).")
            return
        try:
            agregar_alumno(dbname, *vals[:5], fecha_nac_db, fecha_fin_db, *vals[7:])
            pagina_actual[0] = 0
            cargar_y_actualizar()
            limpiar_formulario()
            messagebox.showinfo("Éxito", "Alumno agregado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar: {e}")

    def actualizar():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona un alumno de la tabla.")
            return
        id_alum = tree.item(sel, 'values')[0]
        vals = []
        for key in keys:
            v = campos[key].get() if hasattr(campos[key], 'get') else ""
            vals.append(v)
        try:
            fecha_nac_db = _parse_fecha(vals[5])
            fecha_fin_db = _parse_fecha(vals[6]) if vals[6] else None
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto (usa dd-mm-yyyy).")
            return
        try:
            actualizar_alumno(dbname, id_alum, *vals[:5], fecha_nac_db, fecha_fin_db, *vals[7:])
            cargar_y_actualizar()
            limpiar_formulario()
            messagebox.showinfo("Éxito", "Alumno actualizado.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {e}")

    def borrar():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona un alumno de la tabla.")
            return
        id_alum = tree.item(sel, 'values')[0]
        if messagebox.askyesno("Confirmar", "¿Seguro que quieres borrar este alumno?"):
            try:
                borrar_alumno(dbname, id_alum)
                cargar_y_actualizar()
                limpiar_formulario()
                messagebox.showinfo("Éxito", "Alumno borrado.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo borrar: {e}")

    def seleccionar_fila(event):
        item = tree.focus()
        if item:
            datos = tree.item(item, 'values')
            for key, entry, value in zip(keys, campos.values(), datos[1:]):
                if hasattr(entry, "set"):
                    entry.set(value)
                else:
                    entry.delete(0, tk.END)
                    entry.insert(0, value)

    ttk.Button(btns, text="💾 Guardar", command=guardar).pack(side='left', padx=7)
    ttk.Button(btns, text="✏️ Actualizar", command=actualizar).pack(side='left', padx=7)
    ttk.Button(btns, text="🗑️ Borrar", command=borrar).pack(side='left', padx=7)
    ttk.Button(btns, text="🧹 Limpiar", command=limpiar_formulario).pack(side='left', padx=7)
    ttk.Button(btns, text="📥 Importar Excel", command=lambda: importar_alumnos_desde_excel(dbname, cargar_y_actualizar, root)).pack(side='left', padx=7)

    # Tabla de alumnos (ahora con 25 filas de altura)
    cols = (
        'ID', 'Nombre', 'Apellidos', 'DNI', 'Teléfono', 'Mail',
        'Fecha nacimiento', 'Fecha finalización', 'Curso',
        'Familia curso', 'Código curso', 'Estudios completados', 'Grado curso', 'Ocupación'
    )
    tree = ttk.Treeview(frame, columns=cols, show='headings', height=25, style="Custom.Treeview")
    for i, col in enumerate(cols):
        tree.heading(col, text=col)
        ancho = 60 if i==0 else 110 if i in (6,7) else 105
        tree.column(col, width=ancho, anchor='center')
    tree.grid(row=0, column=1, padx=(32, 5), pady=10, sticky='n')
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.grid(row=0, column=2, sticky='ns', pady=10)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.bind('<<TreeviewSelect>>', seleccionar_fila)

    # Paginación
    paginacion = ttk.Frame(frame, style="Custom.TFrame")
    paginacion.grid(row=2, column=1, pady=8, sticky='w')
    btn_ant = ttk.Button(paginacion, text="◀ Anterior", command=lambda: _cambiar_pagina(pagina_actual, -1, cargar_y_actualizar))
    btn_ant.pack(side='left', padx=4)
    btn_sig = ttk.Button(paginacion, text="Siguiente ▶", command=lambda: _cambiar_pagina(pagina_actual, 1, cargar_y_actualizar))
    btn_sig.pack(side='left', padx=4)
    lbl_pag = ttk.Label(paginacion, text="Página 1", style="Custom.TLabel")
    lbl_pag.pack(side='left', padx=12)

    # Email masivo a seleccionados
    btn_email = ttk.Button(frame, text="Enviar email a seleccionados", command=lambda: _enviar_email_a_seleccionados(tree, dbname, root))
    btn_email.grid(row=1, column=1, pady=(4,8), sticky="w")

    cargar_y_actualizar()


# --------- Imprimir y exportar PDF ---------
def imprimir_alumnos(dbname):
    datos = obtener_alumnos(dbname)
    contenido = (
        "Listado de Alumnos\n\n"
        "Nombre | Apellidos | DNI | Teléfono | Mail | Fecha nacimiento | Fecha finalización | Curso | "
        "Familia curso | Código curso | Estudios completados | Grado curso | Ocupación\n"
        + "-"*160 + "\n"
    )
    for a in datos:
        contenido += (
            f"{a[1]} | {a[2]} | {a[3]} | {a[4]} | {a[5]} | {a[6]} | {a[7]} | {a[8]} | "
            f"{a[9]} | {a[10]} | {a[11]} | {a[12]} | {a[13]}\n"
        )
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
        f.write(contenido)
        temp_file = f.name
    if platform.system() == "Windows":
        os.startfile(temp_file, "print")
    elif platform.system() == "Linux":
        os.system(f"lpr {temp_file}")
    else:
        messagebox.showinfo("Imprimir", f"Archivo guardado en: {temp_file}")

def exportar_pdf(dbname):
    try:
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.pdfgen import canvas as pdfcanvas
    except ImportError:
        messagebox.showerror("Falta módulo", "Instala reportlab: pip install reportlab")
        return
    datos = obtener_alumnos(dbname)
    filename = simpledialog.askstring("Guardar PDF", "Nombre del archivo PDF (sin .pdf):")
    if not filename:
        return
    pdf_file = f"{filename}.pdf"
    c = pdfcanvas.Canvas(pdf_file, pagesize=landscape(letter))
    y = 540
    c.setFont("Helvetica-Bold", 9)
    headers = [
        "Nombre", "Apellidos", "DNI", "Teléfono", "Mail",
        "Fecha nacimiento", "Fecha finalización", "Curso",
        "Familia curso", "Código curso", "Estudios completados",
        "Grado curso", "Ocupación"
    ]
    # Imprime cabecera
    x_positions = [25, 105, 210, 275, 340, 420, 510, 600, 690, 780, 860, 980, 1040]
    for i, head in enumerate(headers):
        c.drawString(x_positions[i], y, head)
    y -= 18
    c.setFont("Helvetica", 8)
    for a in datos:
        fila = [
            a[1], a[2], a[3], a[4], a[5],
            str(a[6]), str(a[7]), a[8], a[9], a[10], a[11], str(a[12]), a[13]
        ]
        for i, val in enumerate(fila):
            c.drawString(x_positions[i], y, str(val)[:18])  # corta largo excesivo
        y -= 14
        if y < 40:
            c.showPage()
            c.setFont("Helvetica-Bold", 9)
            for i, head in enumerate(headers):
                c.drawString(x_positions[i], 540, head)
            c.setFont("Helvetica", 8)
            y = 522
    c.save()
    messagebox.showinfo("PDF", f"PDF guardado como {pdf_file}")


# --------- Utilidades internas ---------
def _animar_prisma(canvas, scale=1, offset_x=None, offset_y=None):
    center_x = (offset_x if offset_x else canvas.winfo_width()//2)
    center_y = (offset_y if offset_y else canvas.winfo_height()//2)
    size = 60 * scale
    angle = [0]
    def draw(a):
        canvas.delete("pyramid")
        base_coords = [(-size, size), (size, size), (0, -size)]
        apex = (0, -size * 1.5)
        def rotate(x, y, angle_deg):
            rad = math.radians(angle_deg)
            xr = x * math.cos(rad) - y * math.sin(rad)
            yr = x * math.sin(rad) + y * math.cos(rad)
            return xr, yr
        rotated_base = [rotate(x, y, a) for x, y in base_coords]
        rotated_apex = rotate(*apex, a)
        points_base = [(center_x + x, center_y + y) for x, y in rotated_base]
        apex_abs = (center_x + rotated_apex[0], center_y + rotated_apex[1])
        for i in range(3):
            p1 = points_base[i]
            p2 = points_base[(i + 1) % 3]
            canvas.create_polygon(p1, p2, apex_abs, fill="#4f8a8b", outline="#ffffff", tags="pyramid")
        canvas.create_polygon(*points_base, fill="#36608a", outline="#ffffff", tags="pyramid")
    def animar():
        draw(angle[0])
        angle[0] += 2
        canvas.after(40, animar)
    animar()

def _parse_fecha(txt):
    if not txt:
        return None
    d, m, y = map(int, txt.split("-"))
    return datetime.date(y, m, d)

def _cambiar_pagina(pagina_actual, delta, cargar_func):
    pagina_actual[0] += delta
    cargar_func()

from email_dialog import ventana_redactar_email

def _enviar_email_a_seleccionados(tree, dbname, parent):
    seleccionados = [tree.item(iid, "values") for iid in tree.selection()]
    if not seleccionados:
        messagebox.showwarning("Sin selección", "Selecciona alumnos de la tabla para enviarles email.", parent=parent)
        return
    emails = [alum[5] for alum in seleccionados if alum[5]]
    if not emails:
        messagebox.showwarning("Sin emails", "Ningún alumno seleccionado tiene email.", parent=parent)
        return
    ventana_redactar_email(parent, emails)





