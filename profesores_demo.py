import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

class GestionProfesoresConAsistenciaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AcademyGo - Gestión de Profesores y Registro de Asistencia")
        self.geometry("950x540")
        self.resizable(False, False)

        # Datos simulados de profesores
        self.datos_profesores = [
            {"id": 1, "Nombre completo": "Juan García", "DNI": "12345678A", "Teléfono": "666112233", "Email": "juan@academygo.es", "Especialidad": "Matemáticas", "Fecha de alta": "2023-09-01", "Dirección": "C/ Mayor, 22", "Observaciones": "Muy buen docente."},
            {"id": 2, "Nombre completo": "Ana López", "DNI": "87654321B", "Teléfono": "699887766", "Email": "ana@academygo.es", "Especialidad": "Inglés", "Fecha de alta": "2022-10-15", "Dirección": "Avda. Sol, 10", "Observaciones": ""}
        ]
        self.asistencias = []  # Lista de dicts

        # ----------- PANEL IZQUIERDO: Lista profesores + búsqueda
        frame_izq = tk.Frame(self, bg="#f5f5f5")
        frame_izq.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        tk.Label(frame_izq, text="Profesores", font=("Arial", 14, "bold"), bg="#f5f5f5").pack(pady=(0,5))

        self.busqueda_var = tk.StringVar()
        entry_busqueda = tk.Entry(frame_izq, textvariable=self.busqueda_var, width=24)
        entry_busqueda.pack(pady=(0,8))
        entry_busqueda.bind("<KeyRelease>", self.filtrar_lista)

        self.lista_profesores = tk.Listbox(frame_izq, width=28, height=23, font=("Arial", 10))
        self.lista_profesores.pack()
        self.lista_profesores.bind("<<ListboxSelect>>", self.mostrar_profesor)

        btns_frame = tk.Frame(frame_izq, bg="#f5f5f5")
        btns_frame.pack(pady=8)
        tk.Button(btns_frame, text="Añadir", command=self.abrir_form_nuevo, width=8, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(btns_frame, text="Editar", command=self.abrir_form_editar, width=8, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(btns_frame, text="Eliminar", command=self.eliminar_profesor, width=8, bg="#F44336", fg="white").pack(side=tk.LEFT, padx=2)

        # ----------- PANEL DERECHO
        frame_der = tk.Frame(self, bg="#ffffff", bd=2, relief=tk.RIDGE)
        frame_der.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Ficha de profesor (arriba)
        tk.Label(frame_der, text="Ficha del Profesor", font=("Arial", 13, "bold"), bg="#ffffff").grid(row=0, column=0, columnspan=4, pady=7)
        etiquetas = ["Nombre completo", "DNI", "Teléfono", "Email", "Especialidad", "Fecha de alta", "Dirección", "Observaciones"]
        self.campos = {}
        for i, texto in enumerate(etiquetas):
            tk.Label(frame_der, text=texto+":", anchor="w", bg="#ffffff", font=("Arial", 10)).grid(row=i+1, column=0, sticky="e", pady=2, padx=(10,2))
            if texto == "Observaciones":
                self.campos[texto] = tk.Text(frame_der, width=38, height=2, font=("Arial", 10))
                self.campos[texto].grid(row=i+1, column=1, columnspan=3, pady=2, sticky="w")
            else:
                self.campos[texto] = tk.Entry(frame_der, width=40, font=("Arial", 10))
                self.campos[texto].grid(row=i+1, column=1, columnspan=3, pady=2, sticky="w")

        # -------------- REGISTRO DE ASISTENCIA (abajo)
        sep = ttk.Separator(frame_der, orient="horizontal")
        sep.grid(row=10, column=0, columnspan=4, sticky="ew", pady=(12,5))

        tk.Label(frame_der, text="Registro de asistencia", font=("Arial", 11, "bold"), bg="#ffffff").grid(row=11, column=0, columnspan=2, sticky="w", padx=(10,0), pady=(3,2))

        tk.Label(frame_der, text="Fecha:", bg="#ffffff", font=("Arial", 10)).grid(row=12, column=0, sticky="e", padx=(10,2))
        self.fecha_var = tk.StringVar(value=str(date.today()))
        tk.Entry(frame_der, textvariable=self.fecha_var, width=14).grid(row=12, column=1, sticky="w")

        tk.Label(frame_der, text="Estado:", bg="#ffffff", font=("Arial", 10)).grid(row=12, column=2, sticky="e")
        self.estado_var = tk.StringVar(value="Presente")
        estados = ["Presente", "Ausente", "Justificado", "Sustitución"]
        self.estado_cb = ttk.Combobox(frame_der, state="readonly", values=estados, textvariable=self.estado_var, width=13)
        self.estado_cb.grid(row=12, column=3, sticky="w")

        tk.Label(frame_der, text="Observaciones:", bg="#ffffff", font=("Arial", 10)).grid(row=13, column=0, sticky="ne", padx=(10,2))
        self.obs_text = tk.Text(frame_der, width=31, height=2, font=("Arial", 10))
        self.obs_text.grid(row=13, column=1, columnspan=3, sticky="w")

        tk.Button(frame_der, text="Registrar asistencia", bg="#4CAF50", fg="white", width=18, command=self.registrar_asistencia).grid(row=14, column=3, sticky="e", pady=(3,3))

        # Tabla asistencias
        tk.Label(frame_der, text="Asistencias recientes", font=("Arial", 10, "italic"), bg="#ffffff").grid(row=15, column=0, columnspan=2, sticky="w", padx=(10,0), pady=(10,0))
        self.tree = ttk.Treeview(frame_der, columns=("fecha", "estado", "obs"), show="headings", height=5)
        self.tree.grid(row=16, column=0, columnspan=4, sticky="w", padx=7)
        for col, w in zip(("fecha", "estado", "obs"), (95, 110, 240)):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=w)

        self.recargar_lista()

    def recargar_lista(self, filtro=""):
        self.lista_profesores.delete(0, tk.END)
        for profe in self.datos_profesores:
            if filtro.lower() in profe["Nombre completo"].lower():
                self.lista_profesores.insert(tk.END, profe["Nombre completo"])

    def filtrar_lista(self, event):
        texto = self.busqueda_var.get()
        self.recargar_lista(filtro=texto)

    def mostrar_profesor(self, event):
        idx = self.lista_profesores.curselection()
        if not idx:
            return
        profe = self.datos_profesores[idx[0]]
        for campo, widget in self.campos.items():
            if campo == "Observaciones":
                widget.delete("1.0", tk.END)
                widget.insert(tk.END, profe.get(campo, ""))
            else:
                widget.delete(0, tk.END)
                widget.insert(0, profe.get(campo, ""))
        self.refrescar_asistencias(profe["id"])

    def abrir_form_nuevo(self):
        self.abrir_formulario(edicion=False)

    def abrir_form_editar(self):
        idx = self.lista_profesores.curselection()
        if not idx:
            messagebox.showinfo("Editar", "Selecciona un profesor para editar.")
            return
        self.abrir_formulario(edicion=True, indice=idx[0])

    def abrir_formulario(self, edicion=False, indice=None):
        form = tk.Toplevel(self)
        form.title("Nuevo Profesor" if not edicion else "Editar Profesor")
        form.geometry("370x420")
        etiquetas = ["Nombre completo", "DNI", "Teléfono", "Email", "Especialidad", "Fecha de alta", "Dirección", "Observaciones"]
        entradas = {}
        for i, texto in enumerate(etiquetas):
            tk.Label(form, text=texto+":", anchor="w", font=("Arial", 10)).grid(row=i, column=0, sticky="e", pady=3, padx=3)
            if texto == "Observaciones":
                entradas[texto] = tk.Text(form, width=27, height=2, font=("Arial", 10))
                entradas[texto].grid(row=i, column=1, pady=3, sticky="w")
            else:
                entradas[texto] = tk.Entry(form, width=29, font=("Arial", 10))
                entradas[texto].grid(row=i, column=1, pady=3, sticky="w")

        if edicion and indice is not None:
            profe = self.datos_profesores[indice]
            for campo, widget in entradas.items():
                if campo == "Observaciones":
                    widget.delete("1.0", tk.END)
                    widget.insert(tk.END, profe.get(campo, ""))
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, profe.get(campo, ""))

        def guardar():
            nuevo = {}
            for campo, widget in entradas.items():
                if campo == "Observaciones":
                    nuevo[campo] = widget.get("1.0", tk.END).strip()
                else:
                    nuevo[campo] = widget.get().strip()
            if not nuevo["Nombre completo"]:
                messagebox.showwarning("Campos obligatorios", "El nombre es obligatorio.")
                return
            if edicion:
                nuevo["id"] = self.datos_profesores[indice]["id"]
                self.datos_profesores[indice] = nuevo
            else:
                nuevo["id"] = max([p["id"] for p in self.datos_profesores] or [0]) + 1
                self.datos_profesores.append(nuevo)
            self.recargar_lista()
            form.destroy()

        tk.Button(form, text="Guardar", command=guardar, bg="#4CAF50", fg="white", width=15).grid(row=len(etiquetas), column=1, pady=12)

    def eliminar_profesor(self):
        idx = self.lista_profesores.curselection()
        if not idx:
            messagebox.showinfo("Eliminar", "Selecciona un profesor para eliminar.")
            return
        nombre = self.datos_profesores[idx[0]]["Nombre completo"]
        if messagebox.askyesno("Eliminar", f"¿Seguro que deseas eliminar a '{nombre}'?"):
            del self.datos_profesores[idx[0]]
            self.recargar_lista()
            for widget in self.campos.values():
                if isinstance(widget, tk.Entry):
                    widget.delete(0, tk.END)
                else:
                    widget.delete("1.0", tk.END)
            self.tree.delete(*self.tree.get_children())

    def registrar_asistencia(self):
        idx = self.lista_profesores.curselection()
        if not idx:
            messagebox.showwarning("Falta profesor", "Selecciona un profesor.")
            return
        profe = self.datos_profesores[idx[0]]
        fecha = self.fecha_var.get()
        estado = self.estado_var.get()
        obs = self.obs_text.get("1.0", tk.END).strip()
        if not fecha:
            messagebox.showwarning("Falta fecha", "Introduce la fecha.")
            return
        registro = {
            "id_profesor": profe["id"],
            "fecha": fecha,
            "estado": estado,
            "observaciones": obs
        }
        self.asistencias.append(registro)
        self.obs_text.delete("1.0", tk.END)
        self.refrescar_asistencias(profe["id"])
        messagebox.showinfo("¡OK!", "Asistencia registrada.")

    def refrescar_asistencias(self, id_profesor):
        self.tree.delete(*self.tree.get_children())
        # Mostrar solo las últimas 6 asistencias del profesor seleccionado
        asist_prof = [a for a in self.asistencias if a["id_profesor"] == id_profesor]
        for reg in asist_prof[-6:][::-1]:
            self.tree.insert("", tk.END, values=(reg["fecha"], reg["estado"], reg["observaciones"]))

if __name__ == "__main__":
    app = GestionProfesoresConAsistenciaApp()
    app.mainloop()
