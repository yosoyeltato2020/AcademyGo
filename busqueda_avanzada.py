import tkinter as tk
from tkinter import ttk, messagebox
from models import filtrar_alumnos_avanzado
from email_dialog import ventana_redactar_email  # Ventana profesional para redactar email

def abrir_busqueda_avanzada(dbname, root_parent):
    ventana = tk.Toplevel(root_parent)
    ventana.title("Búsqueda avanzada de alumnos")
    ventana.geometry("950x600")
    ventana.configure(bg="#e9f0fb")

    filtros = {
        'nombre': tk.StringVar(),
        'apellidos': tk.StringVar(),
        'fecha_nac': tk.StringVar(),
        'fecha_fin': tk.StringVar(),
        'curso': tk.StringVar()
    }

    form = ttk.LabelFrame(ventana, text="Filtros", padding=(14,10))
    form.pack(padx=20, pady=15, fill="x")
    ttk.Label(form, text="Nombre:").grid(row=0, column=0, padx=6, pady=7, sticky='e')
    ttk.Entry(form, textvariable=filtros['nombre']).grid(row=0, column=1, padx=6, pady=7)
    ttk.Label(form, text="Apellidos:").grid(row=0, column=2, padx=6, pady=7, sticky='e')
    ttk.Entry(form, textvariable=filtros['apellidos']).grid(row=0, column=3, padx=6, pady=7)
    ttk.Label(form, text="Fecha nac. (dd-mm-yyyy):").grid(row=1, column=0, padx=6, pady=7, sticky='e')
    ttk.Entry(form, textvariable=filtros['fecha_nac']).grid(row=1, column=1, padx=6, pady=7)
    ttk.Label(form, text="Fecha fin (dd-mm-yyyy):").grid(row=1, column=2, padx=6, pady=7, sticky='e')
    ttk.Entry(form, textvariable=filtros['fecha_fin']).grid(row=1, column=3, padx=6, pady=7)
    ttk.Label(form, text="Curso:").grid(row=1, column=4, padx=6, pady=7, sticky='e')
    ttk.Entry(form, textvariable=filtros['curso']).grid(row=1, column=5, padx=6, pady=7)

    def parse_fecha(txt):
        if not txt:
            return None
        try:
            d, m, y = map(int, txt.split("-"))
            return f"{y:04d}-{m:02d}-{d:02d}"
        except Exception:
            return None

    def filtrar():
        res = filtrar_alumnos_avanzado(
            dbname,
            filtros['nombre'].get(),
            filtros['apellidos'].get(),
            parse_fecha(filtros['fecha_nac'].get()),
            parse_fecha(filtros['fecha_fin'].get()),
            filtros['curso'].get(),
        )
        for i in tree.get_children():
            tree.delete(i)
        for alum in res:
            tree.insert("", tk.END, values=alum)
        lbl_total.config(text=f"Total: {len(res)} alumnos")

    def limpiar():
        for v in filtros.values():
            v.set("")
        filtrar()

    def enviar_email():
        seleccionados = [tree.item(iid, "values") for iid in tree.selection()]
        if not seleccionados:
            messagebox.showwarning("Sin selección", "Selecciona alumnos de la tabla para enviarles email.", parent=ventana)
            return
        emails = [alum[5] for alum in seleccionados if alum[5]]
        if not emails:
            messagebox.showwarning("Sin emails", "Ningún alumno seleccionado tiene email.", parent=ventana)
            return
        # Abre la ventana profesional de redacción de email
        ventana_redactar_email(ventana, emails)

    ttk.Button(form, text="Buscar", command=filtrar).grid(row=2, column=0, padx=10, pady=10)
    ttk.Button(form, text="Limpiar", command=limpiar).grid(row=2, column=1, padx=10, pady=10)
    ttk.Button(ventana, text="Enviar email a seleccionados", command=enviar_email).pack(pady=7)

    cols = ('ID', 'Nombre', 'Apellidos', 'DNI', 'Teléfono', 'Mail', 'Fecha nacimiento', 'Fecha finalización', 'Curso')
    tree = ttk.Treeview(ventana, columns=cols, show='headings', height=16)
    for i, col in enumerate(cols):
        tree.heading(col, text=col)
        ancho = 60 if i==0 else 110 if i in (6,7) else 105
        tree.column(col, width=ancho, anchor='center')
    tree.pack(padx=20, pady=10, fill='both', expand=True)
    scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    lbl_total = ttk.Label(ventana, text="Total: 0 alumnos")
    lbl_total.pack(pady=(2,4), anchor="w", padx=28)

    filtrar()
