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

from email_utils import enviar_email_masivo
import platform
import math
import datetime
import webbrowser
import tempfile
import os

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
    ttk.Button(botones, text="Cerrar sesión", command=lambda: [root.destroy(), pantalla_inicio()]).pack(side='left', padx=16)

    tk.Label(root, text="© 2025 PRACTICADORES.DEV", bg=TAB_COLOR, fg="#375aab", font=("Segoe UI", 11, "italic")).pack(side='bottom', pady=4)
    root.mainloop()

# --------- Contenido de la pestaña de alumnos ---------
def contenido_alumnos(tab, dbname, root):
    frame = ttk.Frame(tab, padding=18)
    frame.pack(fill='both', expand=True, padx=24, pady=16)

    labels = [
        'Nombre', 'Apellidos', 'DNI', 'Teléfono', 'Mail',
        'Fecha nacimiento (dd-mm-yyyy)', 'Fecha finalización (dd-mm-yyyy)', 'Curso'
    ]
    keys = ['nombre', 'apellidos', 'dni', 'telefono', 'mail', 'fecha_nac', 'fecha_fin', 'curso']
    campos = {}

    form = ttk.LabelFrame(frame, text="Datos del Alumno", padding=(18,10))
    form.grid(row=0, column=0, sticky='nw', rowspan=3, pady=10)

    for i, (label, key) in enumerate(zip(labels, keys)):
        ttk.Label(form, text=label + ":", anchor='w').grid(row=i, column=0, pady=7, sticky='e')
        entry = ttk.Entry(form, width=24, font=('Segoe UI', 12))
        entry.grid(row=i, column=1, pady=7, padx=7, sticky='w')
        campos[key] = entry

    # Botones CRUD
    btns = ttk.Frame(form)
    btns.grid(row=8, column=0, columnspan=2, pady=(18, 8))

    def limpiar_formulario():
        for campo in campos.values():
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
        tree.tag_configure('oddrow', background='#f7fbff')
        max_pagina = max(0, (len(alumnos) - 1) // PAGINA_TAMANO)
        btn_ant.config(state=tk.NORMAL if pagina_actual[0] > 0 else tk.DISABLED)
        btn_sig.config(state=tk.NORMAL if pagina_actual[0] < max_pagina else tk.DISABLED)
        lbl_pag.config(text=f"Página {pagina_actual[0]+1} de {max_pagina+1}")

    def guardar():
        vals = [campos[k].get() for k in keys]
        if not vals[0] or not vals[1]:
            messagebox.showwarning("Atención", "Nombre y apellidos obligatorios.")
            return
        # Validar fechas
        try:
            fecha_nac_db = _parse_fecha(vals[5])
            fecha_fin_db = _parse_fecha(vals[6]) if vals[6] else None
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto (usa dd-mm-yyyy).")
            return
        try:
            agregar_alumno(dbname, vals[0], vals[1], vals[2], vals[3], vals[4], fecha_nac_db, fecha_fin_db, vals[7])
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
        vals = [campos[k].get() for k in keys]
        try:
            fecha_nac_db = _parse_fecha(vals[5])
            fecha_fin_db = _parse_fecha(vals[6]) if vals[6] else None
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto (usa dd-mm-yyyy).")
            return
        try:
            actualizar_alumno(dbname, id_alum, vals[0], vals[1], vals[2], vals[3], vals[4], fecha_nac_db, fecha_fin_db, vals[7])
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
                entry.delete(0, tk.END)
                entry.insert(0, value)

    ttk.Button(btns, text="💾 Guardar", command=guardar).pack(side='left', padx=7)
    ttk.Button(btns, text="✏️ Actualizar", command=actualizar).pack(side='left', padx=7)
    ttk.Button(btns, text="🗑️ Borrar", command=borrar).pack(side='left', padx=7)
    ttk.Button(btns, text="🧹 Limpiar", command=limpiar_formulario).pack(side='left', padx=7)

    # Tabla de alumnos
    cols = ('ID', 'Nombre', 'Apellidos', 'DNI', 'Teléfono', 'Mail', 'Fecha nacimiento', 'Fecha finalización', 'Curso')
    tree = ttk.Treeview(frame, columns=cols, show='headings', height=16)
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
    paginacion = ttk.Frame(frame)
    paginacion.grid(row=2, column=1, pady=8, sticky='w')
    btn_ant = ttk.Button(paginacion, text="◀ Anterior", command=lambda: _cambiar_pagina(pagina_actual, -1, cargar_y_actualizar))
    btn_ant.pack(side='left', padx=4)
    btn_sig = ttk.Button(paginacion, text="Siguiente ▶", command=lambda: _cambiar_pagina(pagina_actual, 1, cargar_y_actualizar))
    btn_sig.pack(side='left', padx=4)
    lbl_pag = ttk.Label(paginacion, text="Página 1")
    lbl_pag.pack(side='left', padx=12)

    # Email masivo a seleccionados
    btn_email = ttk.Button(frame, text="Enviar email a seleccionados", command=lambda: _enviar_email_a_seleccionados(tree, dbname, root))
    btn_email.grid(row=1, column=1, pady=(4,8), sticky="w")

    cargar_y_actualizar()

# --------- Imprimir y exportar PDF ---------
def imprimir_alumnos(dbname):
    datos = obtener_alumnos(dbname)
    contenido = "Listado de Alumnos\n\n"
    for a in datos:
        contenido += f"{a[1]} {a[2]} | {a[3]} | {a[4]} | {a[5]} | {a[6]} | {a[7]} | {a[8]}\n"
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
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas as pdfcanvas
    except ImportError:
        messagebox.showerror("Falta módulo", "Instala reportlab: pip install reportlab")
        return
    datos = obtener_alumnos(dbname)
    filename = simpledialog.askstring("Guardar PDF", "Nombre del archivo PDF (sin .pdf):")
    if not filename:
        return
    pdf_file = f"{filename}.pdf"
    c = pdfcanvas.Canvas(pdf_file, pagesize=letter)
    y = 760
    c.setFont("Helvetica", 10)
    c.drawString(40, y, "Listado de Alumnos")
    y -= 20
    for a in datos:
        linea = f"{a[1]} {a[2]} | {a[3]} | {a[4]} | {a[5]} | {a[6]} | {a[7]} | {a[8]}"
        c.drawString(40, y, linea)
        y -= 14
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 760
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





