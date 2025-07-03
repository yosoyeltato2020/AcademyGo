# email_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from email_utils import enviar_email_masivo, abrir_gestor_externo

def ventana_redactar_email(parent, destinatarios):
    win = tk.Toplevel(parent)
    win.title("Redactar email a seleccionados")
    win.geometry("700x500")
    win.transient(parent)
    win.grab_set()
    win.resizable(True, True)

    to_var = tk.StringVar(value=", ".join(destinatarios))
    cc_var = tk.StringVar()
    asunto_var = tk.StringVar()
    adjuntos = []

    frame = ttk.Frame(win, padding=15)
    frame.grid(row=0, column=0, sticky='nsew')

    # Configurar filas y columnas para expansión
    win.grid_rowconfigure(0, weight=1)
    win.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(3, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    ttk.Label(frame, text="Para:", font=('Segoe UI', 11)).grid(row=0, column=0, sticky='e', padx=5, pady=5)
    entry_to = ttk.Entry(frame, textvariable=to_var)
    entry_to.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

    ttk.Label(frame, text="CC:", font=('Segoe UI', 11)).grid(row=1, column=0, sticky='e', padx=5, pady=5)
    entry_cc = ttk.Entry(frame, textvariable=cc_var)
    entry_cc.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

    ttk.Label(frame, text="Asunto:", font=('Segoe UI', 11)).grid(row=2, column=0, sticky='e', padx=5, pady=5)
    entry_asunto = ttk.Entry(frame, textvariable=asunto_var)
    entry_asunto.grid(row=2, column=1, sticky='ew', padx=5, pady=5)

    ttk.Label(frame, text="Mensaje:", font=('Segoe UI', 11)).grid(row=3, column=0, sticky='ne', padx=5, pady=5)
    text_cuerpo = tk.Text(frame, wrap='word')
    text_cuerpo.grid(row=3, column=1, sticky='nsew', padx=5, pady=5)

    lbl_adjuntos = ttk.Label(frame, text="Sin adjuntos")
    lbl_adjuntos.grid(row=4, column=1, sticky='w', padx=5, pady=(0,10))

    def añadir_adjunto():
        files = filedialog.askopenfilenames(parent=win, title="Selecciona archivos para adjuntar")
        if files:
            adjuntos.clear()
            adjuntos.extend(files)
            nombres = [f.split("/")[-1] for f in adjuntos]
            lbl_adjuntos.config(text="Adjuntos: " + ", ".join(nombres))

    btn_adj = ttk.Button(frame, text="Adjuntar archivo", command=añadir_adjunto)
    btn_adj.grid(row=4, column=0, sticky='e', padx=5, pady=(0,10))

    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=5, column=1, sticky='e', padx=5, pady=10)

    def enviar_smtp():
        to = entry_to.get().strip().replace(";", ",")
        cc = entry_cc.get().strip().replace(";", ",")
        asunto = entry_asunto.get().strip()
        cuerpo = text_cuerpo.get("1.0", "end-1c").strip()
        lista_to = [x.strip() for x in to.split(",") if x.strip()]
        lista_cc = [x.strip() for x in cc.split(",") if x.strip()]
        if not lista_to or not asunto or not cuerpo:
            messagebox.showwarning("Faltan campos", "Completa Para, Asunto y Mensaje.")
            return
        enviados, errores = enviar_email_masivo(lista_to, asunto, cuerpo, cc=lista_cc, adjuntos=adjuntos)
        messagebox.showinfo("Email", f"Emails enviados: {enviados}\nFallidos: {errores}")
        win.destroy()

    def abrir_en_gestor():
        to = entry_to.get().strip().replace(";", ",")
        cc = entry_cc.get().strip().replace(";", ",")
        asunto = entry_asunto.get().strip()
        cuerpo = text_cuerpo.get("1.0", "end-1c").strip()
        abrir_gestor_externo(to, asunto, cuerpo, cc)

    ttk.Button(btn_frame, text="Abrir en gestor externo", command=abrir_en_gestor).pack(side='left', padx=6)
    ttk.Button(btn_frame, text="Enviar desde AcademyGo", command=enviar_smtp).pack(side='left', padx=6)
    ttk.Button(btn_frame, text="Cancelar", command=win.destroy).pack(side='left', padx=6)

    win.wait_window()
