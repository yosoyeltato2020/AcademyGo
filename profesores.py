import tkinter as tk
from tkinter import ttk, messagebox
from database import (
    obtener_profesores, agregar_profesor, actualizar_profesor, borrar_profesor,
    obtener_cursos_unicos_alumnos, asignar_cursos_a_profesor, obtener_cursos_de_profesor,
    crear_tablas_academia
)
import datetime

TAB_COLOR = "#e9f0fb"
HEADER_COLOR = "#375aab"
BG_FORM = "#eaf3fc"
COLOR_LABEL = "#234b80"

def ventana_gestion_profesores(dbname, parent=None):
    crear_tablas_academia(dbname)  # Asegura que las tablas necesarias existen
    win = tk.Toplevel(parent)
    win.title("Gestión de Profesores")
    win.configure(bg=TAB_COLOR)
    win.geometry("1020x660")
    win.resizable(True, True)
    win.transient(parent)
    win.grab_set()  # Modal
    win.update_idletasks()
    try:
        # Windows
        win.state('zoomed')
    except Exception:
        try:
            # Linux/Unix (Tk >= 8.5)
            win.attributes('-zoomed', True)
        except Exception:
            # Método manual: pantalla completa en cualquier SO
            w = win.winfo_screenwidth()
            h = win.winfo_screenheight()
            win.geometry(f"{w}x{h}+0+0")

    # ----- Header -----
    header = tk.Frame(win, bg=HEADER_COLOR)
    header.pack(fill="x")
    tk.Label(header, text="Gestión de Profesores", bg=HEADER_COLOR, fg="white", font=("Segoe UI", 21, "bold")).pack(pady=14)

    # ----- Frame principal -----
    main_frame = ttk.Frame(win, padding=20)
    main_frame.pack(fill="both", expand=True)

    # -------- Formulario lateral ---------
    form = ttk.LabelFrame(main_frame, text="Alta/Edición Profesor", padding=(16,12))
    form.grid(row=0, column=0, sticky="nw", rowspan=3, pady=6)
    campos = {}
    labels = [
        ("Nombre:", "nombre"),
        ("Apellidos:", "apellidos"),
        ("DNI:", "dni"),
        ("Teléfono:", "telefono"),
        ("Mail:", "mail"),
        ("Fecha nacimiento (dd-mm-yyyy):", "fecha_nacimiento"),
        ("Dirección:", "direccion"),
        ("Observaciones:", "observaciones")
    ]
    for i, (lbl, key) in enumerate(labels):
        ttk.Label(form, text=lbl, style="Custom.TLabel").grid(row=i, column=0, sticky="e", pady=4)
        entry = ttk.Entry(form, width=24)
        entry.grid(row=i, column=1, pady=4, padx=7, sticky='w')
        campos[key] = entry

    # Selector múltiple de cursos
    ttk.Label(form, text="Cursos:", style="Custom.TLabel").grid(row=len(labels), column=0, sticky="ne", pady=6)
    cursos_listbox = tk.Listbox(form, selectmode="multiple", width=24, height=7, exportselection=False)
    cursos_listbox.grid(row=len(labels), column=1, pady=6, padx=7, sticky="w")

    # Botones CRUD
    btns = ttk.Frame(form)
    btns.grid(row=len(labels)+2, column=0, columnspan=2, pady=14)
    btn_guardar = ttk.Button(btns, text="💾 Guardar")
    btn_actualizar = ttk.Button(btns, text="✏️ Actualizar")
    btn_borrar = ttk.Button(btns, text="🗑️ Borrar")
    btn_limpiar = ttk.Button(btns, text="🧹 Limpiar")
    btn_guardar.pack(side="left", padx=7)
    btn_actualizar.pack(side="left", padx=7)
    btn_borrar.pack(side="left", padx=7)
    btn_limpiar.pack(side="left", padx=7)

    # -------- Tabla central de profesores ---------
    cols = ('ID', 'Nombre', 'Apellidos', 'DNI', 'Mail', 'Teléfono', 'Cursos')
    tree = ttk.Treeview(main_frame, columns=cols, show='headings', height=25)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=120 if col!='Cursos' else 190, anchor="center")
    tree.grid(row=0, column=1, padx=(36,8), pady=6, sticky='n')

    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0, column=2, sticky='ns', pady=10)

    # --------- Funciones internas ---------
    def cargar_cursos_listbox():
        cursos = obtener_cursos_unicos_alumnos(dbname)
        cursos_listbox.delete(0, tk.END)
        for c in cursos:
            cursos_listbox.insert(tk.END, c)

    def limpiar_formulario():
        for entry in campos.values():
            entry.delete(0, tk.END)
        cursos_listbox.selection_clear(0, tk.END)
        tree.selection_remove(tree.selection())

    def cargar_profesores():
        tree.delete(*tree.get_children())
        profesores = obtener_profesores(dbname)
        for p in profesores:
            cursos = obtener_cursos_de_profesor(dbname, p[0])
            cursos_str = ", ".join(cursos)
            row = (p[0], p[1], p[2], p[3], p[5], p[4], cursos_str)
            tree.insert('', tk.END, values=row)

    def seleccionar_profesor(event):
        sel = tree.focus()
        if not sel:
            return
        datos = tree.item(sel, 'values')
        id_prof, nombre, apellidos, dni, mail, telefono, cursos_str = datos
        campos['nombre'].delete(0, tk.END)
        campos['nombre'].insert(0, nombre)
        campos['apellidos'].delete(0, tk.END)
        campos['apellidos'].insert(0, apellidos)
        campos['dni'].delete(0, tk.END)
        campos['dni'].insert(0, dni)
        campos['telefono'].delete(0, tk.END)
        campos['telefono'].insert(0, telefono)
        campos['mail'].delete(0, tk.END)
        campos['mail'].insert(0, mail)
        # Buscar datos completos del profesor para rellenar dirección, observaciones, fecha_nacimiento
        profesores = obtener_profesores(dbname, filtro=dni)
        if profesores:
            p = profesores[0]
            if p[6]: campos['direccion'].delete(0, tk.END); campos['direccion'].insert(0, p[6])
            if p[7]: campos['observaciones'].delete(0, tk.END); campos['observaciones'].insert(0, p[7])
            if p[5]:
                try:
                    campos['fecha_nacimiento'].delete(0, tk.END)
                    campos['fecha_nacimiento'].insert(0, p[5].strftime("%d-%m-%Y"))
                except Exception:
                    pass
        # Seleccionar los cursos asignados
        cursos_seleccionados = [c.strip() for c in cursos_str.split(",") if c.strip()]
        all_cursos = [cursos_listbox.get(i) for i in range(cursos_listbox.size())]
        cursos_indices = [idx for idx, c in enumerate(all_cursos) if c in cursos_seleccionados]
        cursos_listbox.selection_clear(0, tk.END)
        for idx in cursos_indices:
            cursos_listbox.selection_set(idx)

    def guardar_profesor():
        try:
            nombre = campos['nombre'].get().strip()
            apellidos = campos['apellidos'].get().strip()
            dni = campos['dni'].get().strip()
            telefono = campos['telefono'].get().strip()
            mail = campos['mail'].get().strip()
            fecha_nac = campos['fecha_nacimiento'].get().strip()
            direccion = campos['direccion'].get().strip()
            observaciones = campos['observaciones'].get().strip()
            if not nombre or not apellidos:
                messagebox.showwarning("Campos obligatorios", "Nombre y apellidos son obligatorios.")
                return
            fecha_nac_db = None
            if fecha_nac:
                try:
                    d, m, y = map(int, fecha_nac.split('-'))
                    fecha_nac_db = datetime.date(y, m, d)
                except Exception:
                    messagebox.showwarning("Fecha incorrecta", "Formato de fecha nacimiento: dd-mm-yyyy")
                    return
            seleccionados = cursos_listbox.curselection()
            lista_cursos = [cursos_listbox.get(i) for i in seleccionados]
            if not lista_cursos:
                messagebox.showwarning("Falta cursos", "Selecciona al menos un curso que imparte el profesor.")
                return
            prof_id = agregar_profesor(dbname, nombre, apellidos, dni, telefono, mail, fecha_nac_db, direccion, observaciones)
            asignar_cursos_a_profesor(dbname, prof_id, lista_cursos)
            cargar_profesores()
            limpiar_formulario()
            messagebox.showinfo("Éxito", "Profesor guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar profesor:\n{e}")

    def actualizar_profesor_fn():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona un profesor de la tabla.")
            return
        id_profesor = tree.item(sel, 'values')[0]
        try:
            nombre = campos['nombre'].get().strip()
            apellidos = campos['apellidos'].get().strip()
            dni = campos['dni'].get().strip()
            telefono = campos['telefono'].get().strip()
            mail = campos['mail'].get().strip()
            fecha_nac = campos['fecha_nacimiento'].get().strip()
            direccion = campos['direccion'].get().strip()
            observaciones = campos['observaciones'].get().strip()
            if not nombre or not apellidos:
                messagebox.showwarning("Campos obligatorios", "Nombre y apellidos son obligatorios.")
                return
            fecha_nac_db = None
            if fecha_nac:
                try:
                    d, m, y = map(int, fecha_nac.split('-'))
                    fecha_nac_db = datetime.date(y, m, d)
                except Exception:
                    messagebox.showwarning("Fecha incorrecta", "Formato de fecha nacimiento: dd-mm-yyyy")
                    return
            seleccionados = cursos_listbox.curselection()
            lista_cursos = [cursos_listbox.get(i) for i in seleccionados]
            if not lista_cursos:
                messagebox.showwarning("Falta cursos", "Selecciona al menos un curso que imparte el profesor.")
                return
            actualizar_profesor(dbname, id_profesor, nombre, apellidos, dni, telefono, mail, fecha_nac_db, direccion, observaciones)
            asignar_cursos_a_profesor(dbname, id_profesor, lista_cursos)
            cargar_profesores()
            limpiar_formulario()
            messagebox.showinfo("Éxito", "Profesor actualizado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar profesor:\n{e}")

    def borrar_profesor_fn():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona un profesor de la tabla.")
            return
        id_profesor = tree.item(sel, 'values')[0]
        if messagebox.askyesno("Confirmar", "¿Seguro que quieres borrar este profesor?"):
            try:
                borrar_profesor(dbname, id_profesor)
                cargar_profesores()
                limpiar_formulario()
                messagebox.showinfo("Éxito", "Profesor borrado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo borrar: {e}")

    def limpiar_fn():
        limpiar_formulario()

    btn_guardar.config(command=guardar_profesor)
    btn_actualizar.config(command=actualizar_profesor_fn)
    btn_borrar.config(command=borrar_profesor_fn)
    btn_limpiar.config(command=limpiar_fn)

    # Buscar profesores
    frame_buscar = ttk.Frame(main_frame)
    frame_buscar.grid(row=1, column=1, sticky="nw", pady=4)
    tk.Label(frame_buscar, text="Buscar:").pack(side="left", padx=4)
    entry_buscar = ttk.Entry(frame_buscar, width=24)
    entry_buscar.pack(side="left")
    def buscar():
        filtro = entry_buscar.get().strip()
        tree.delete(*tree.get_children())
        profesores = obtener_profesores(dbname, filtro)
        for p in profesores:
            cursos = obtener_cursos_de_profesor(dbname, p[0])
            cursos_str = ", ".join(cursos)
            row = (p[0], p[1], p[2], p[3], p[5], p[4], cursos_str)
            tree.insert('', tk.END, values=row)
    ttk.Button(frame_buscar, text="Buscar", command=buscar).pack(side="left", padx=4)

    tree.bind('<<TreeviewSelect>>', seleccionar_profesor)

    # Estilos
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Treeview", background="#e6f2ff", fieldbackground="#e6f2ff", font=("Segoe UI", 11))
    style.configure("Treeview.Heading", background=HEADER_COLOR, foreground="white", font=("Segoe UI", 11, "bold"))
    style.configure("TLabel", background=BG_FORM, foreground=COLOR_LABEL, font=('Segoe UI', 11))
    style.configure("TButton", font=('Segoe UI', 10, 'bold'), background="#4a90e2")
    style.configure("TFrame", background=BG_FORM)
    style.configure("TLabelframe", background=BG_FORM, foreground=COLOR_LABEL)

    cargar_cursos_listbox()
    cargar_profesores()
    limpiar_formulario()
    win.protocol("WM_DELETE_WINDOW", win.destroy)  # Cerrar ventana correctamente
    win.mainloop()  
