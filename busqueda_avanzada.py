# busqueda_avanzada.py
import tkinter as tk
from tkinter import ttk, messagebox
from models import filtrar_alumnos_avanzado
from email_dialog import ventana_redactar_email
import datetime

def abrir_busqueda_avanzada(dbname, root_parent):
    ventana = tk.Toplevel(root_parent)
    ventana.title("Búsqueda avanzada de alumnos")
    ventana.geometry("1300x680")
    ventana.configure(bg="#e7f0fb")

    # ---- Estilos colores ----
    style = ttk.Style(ventana)
    style.theme_use('default')
    style.configure("Filtros.TLabelframe", background="#eaf3fc", foreground="#234b80", font=('Segoe UI', 12, 'bold'))
    style.configure("Filtros.TLabel", background="#eaf3fc", foreground="#234b80", font=('Segoe UI', 11))
    style.configure("Custom.Treeview", background="#e6f2ff", fieldbackground="#e6f2ff", font=('Segoe UI', 10))
    style.configure("Custom.Treeview.Heading", background="#375aab", foreground="white", font=('Segoe UI', 10, "bold"))

    # ---- Filtros ----
    filtros = {
        'nombre': tk.StringVar(),
        'apellidos': tk.StringVar(),
        'fecha_nac': tk.StringVar(),
        'fecha_fin': tk.StringVar(),
        'curso': tk.StringVar(),
        'familia_curso': tk.StringVar(),
        'codigo_curso': tk.StringVar(),
        'estudios_completados': tk.StringVar(),
        'grado_curso': tk.StringVar(),
        'ocupacion': tk.StringVar(),
        'antiguedad': tk.StringVar(value="Todos"),  # Nuevo filtro
    }

    form = ttk.LabelFrame(ventana, text="Filtros", padding=(14, 10), style="Filtros.TLabelframe")
    form.pack(padx=20, pady=15, fill="x")

    # Primera fila de filtros
    ttk.Label(form, text="Nombre:", style="Filtros.TLabel").grid(row=0, column=0, padx=6, pady=7, sticky='e')
    ttk.Entry(form, textvariable=filtros['nombre'], width=14).grid(row=0, column=1, padx=6, pady=7)
    ttk.Label(form, text="Apellidos:", style="Filtros.TLabel").grid(row=0, column=2, padx=6, pady=7, sticky='e')
    ttk.Entry(form, textvariable=filtros['apellidos'], width=14).grid(row=0, column=3, padx=6, pady=7)
    ttk.Label(form, text="Fecha nac. (dd-mm-yyyy):", style="Filtros.TLabel").grid(row=0, column=4, padx=6, pady=7, sticky='e')
    ttk.Entry(form, textvariable=filtros['fecha_nac'], width=14).grid(row=0, column=5, padx=6, pady=7)
    ttk.Label(form, text="Fecha fin (dd-mm-yyyy):", style="Filtros.TLabel").grid(row=0, column=6, padx=6, pady=7, sticky='e')
    ttk.Entry(form, textvariable=filtros['fecha_fin'], width=14).grid(row=0, column=7, padx=6, pady=7)

    # Segunda fila de filtros
    ttk.Label(form, text="Curso:", style="Filtros.TLabel").grid(row=1, column=0, padx=6, pady=7, sticky='e')
    ttk.Entry(form, textvariable=filtros['curso'], width=14).grid(row=1, column=1, padx=6, pady=7)
    ttk.Label(form, text="Familia curso:", style="Filtros.TLabel").grid(row=1, column=2, padx=6, pady=7, sticky='e')
    ttk.Entry(form, textvariable=filtros['familia_curso'], width=14).grid(row=1, column=3, padx=6, pady=7)
    ttk.Label(form, text="Código curso:", style="Filtros.TLabel").grid(row=1, column=4, padx=6, pady=7, sticky='e')
    ttk.Entry(form, textvariable=filtros['codigo_curso'], width=14).grid(row=1, column=5, padx=6, pady=7)
    ttk.Label(form, text="Estudios completados:", style="Filtros.TLabel").grid(row=1, column=6, padx=6, pady=7, sticky='e')
    ttk.Entry(form, textvariable=filtros['estudios_completados'], width=14).grid(row=1, column=7, padx=6, pady=7)

    # Tercera fila: grado y ocupacion (desplegables)
    ttk.Label(form, text="Grado curso:", style="Filtros.TLabel").grid(row=2, column=0, padx=6, pady=7, sticky='e')
    grado_cb = ttk.Combobox(form, textvariable=filtros['grado_curso'], values=["", 1, 2, 3, 4], width=12, state="readonly")
    grado_cb.grid(row=2, column=1, padx=6, pady=7)
    ttk.Label(form, text="Ocupación:", style="Filtros.TLabel").grid(row=2, column=2, padx=6, pady=7, sticky='e')
    ocupacion_cb = ttk.Combobox(form, textvariable=filtros['ocupacion'], values=["", "Empleado", "Desempleado"], width=14, state="readonly")
    ocupacion_cb.grid(row=2, column=3, padx=6, pady=7)

    # --- Nueva fila: antigüedad de finalización ---
    ttk.Label(form, text="Antigüedad finalización:", style="Filtros.TLabel").grid(row=2, column=4, padx=6, pady=7, sticky='e')
    antiguedad_cb = ttk.Combobox(form, textvariable=filtros['antiguedad'],
                                 values=["Todos", "Más de 3 meses", "Más de 6 meses", "Más de 9 meses"],
                                 width=18, state="readonly")
    antiguedad_cb.grid(row=2, column=5, padx=6, pady=7)

    # Columnas
    cols = (
        'ID', 'Nombre', 'Apellidos', 'DNI', 'Teléfono', 'Mail',
        'Fecha nacimiento', 'Fecha finalización', 'Curso',
        'Familia curso', 'Código curso', 'Estudios completados', 'Grado curso', 'Ocupación'
    )
    tree = ttk.Treeview(ventana, columns=cols, show='headings', height=25, style="Custom.Treeview")
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

    # --- Funciones internas ---
    def parse_fecha(txt):
        if not txt:
            return None
        try:
            d, m, y = map(int, txt.split("-"))
            return f"{y:04d}-{m:02d}-{d:02d}"
        except Exception:
            return None

    def filtrar():
        antiguedad = filtros['antiguedad'].get()
        hoy = datetime.date.today()
        fecha_fin_desde = None
        fecha_fin_hasta = None

        if antiguedad == "Más de 3 meses":
            fecha_fin_desde = (hoy - datetime.timedelta(days=180)).isoformat()  # 6 meses atrás
            fecha_fin_hasta = (hoy - datetime.timedelta(days=90)).isoformat()   # 3 meses atrás
        elif antiguedad == "Más de 6 meses":
            fecha_fin_desde = (hoy - datetime.timedelta(days=270)).isoformat()  # 9 meses atrás
            fecha_fin_hasta = (hoy - datetime.timedelta(days=180)).isoformat()  # 6 meses atrás
        elif antiguedad == "Más de 9 meses":
            fecha_fin_hasta = (hoy - datetime.timedelta(days=270)).isoformat()  # 9 meses atrás
        # Si es "Todos", no se filtra por antigüedad

        res = filtrar_alumnos_avanzado(
            dbname,
            filtros['nombre'].get(),
            filtros['apellidos'].get(),
            parse_fecha(filtros['fecha_nac'].get()),
            None,  # fecha_nac_hasta
            filtros['curso'].get(),
            fecha_fin_desde,  # fecha_fin_desde
            fecha_fin_hasta,  # fecha_fin_hasta
            filtros['familia_curso'].get(),
            filtros['codigo_curso'].get(),
            filtros['estudios_completados'].get(),
            filtros['grado_curso'].get(),
            filtros['ocupacion'].get(),
        )
        for i in tree.get_children():
            tree.delete(i)
        # COLOREA registros según fecha_finalización
        for alum in res:
            tag = ''
            fecha_fin = alum[7]
            if fecha_fin:
                if isinstance(fecha_fin, str):
                    try:
                        fecha_fin_dt = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
                    except ValueError:
                        fecha_fin_dt = None
                else:
                    fecha_fin_dt = fecha_fin

                if fecha_fin_dt:
                    meses = (hoy.year - fecha_fin_dt.year) * 12 + hoy.month - fecha_fin_dt.month
                    if meses >= 9:
                        tag = 'rojo'
                    elif meses >= 6:
                        tag = 'azul'
                    elif meses >= 3:
                        tag = 'verde'

            tree.insert("", tk.END, values=alum, tags=(tag,))
        tree.tag_configure('verde', background='#ccffd8')
        tree.tag_configure('azul', background='#dde9ff')
        tree.tag_configure('rojo', background='#ffd6d6')

        lbl_total.config(text=f"Total: {len(res)} alumnos")

    def limpiar():
        for v in filtros.values():
            v.set("")
        filtros['antiguedad'].set("Todos")
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
        ventana_redactar_email(ventana, emails)

    ttk.Button(form, text="Buscar", command=filtrar).grid(row=3, column=0, padx=10, pady=10)
    ttk.Button(form, text="Limpiar", command=limpiar).grid(row=3, column=1, padx=10, pady=10)
    ttk.Button(ventana, text="Enviar email a seleccionados", command=enviar_email).pack(pady=7)

    filtrar()
