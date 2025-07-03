import smtplib
from email.mime.text import MIMEText

# Modifica esto con tus datos reales si lo deseas
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USER = "tucuenta@example.com"
SMTP_PASS = "tucontraseña"

def enviar_email_masivo(destinatarios, asunto, mensaje):
    enviados = 0
    errores = 0
    # --- SIMULACIÓN: SOLO PRINT, CAMBIA A SMTP REAL SI LO DESEAS ---
    for dest in destinatarios:
        try:
            print(f"Enviando a: {dest}\nAsunto: {asunto}\nMensaje:\n{mensaje}\n")
            # Para producción descomenta y configura SMTP:
            # msg = MIMEText(mensaje)
            # msg["Subject"] = asunto
            # msg["From"] = SMTP_USER
            # msg["To"] = dest
            # with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            #     server.starttls()
            #     server.login(SMTP_USER, SMTP_PASS)
            #     server.sendmail(SMTP_USER, dest, msg.as_string())
            enviados += 1
        except Exception as e:
            print(f"Error enviando a {dest}: {e}")
            errores += 1
    return enviados, errores
