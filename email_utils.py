# email_utils.py
import smtplib
from email.message import EmailMessage
import webbrowser

# ------- Configuración SMTP (ajústalo a tus necesidades) -------
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'tuemail@gmail.com'
SMTP_PASS = 'tu_clave_app_o_password'

def enviar_email_masivo(destinatarios, asunto, cuerpo, cc=None, adjuntos=None):
    enviados, errores = 0, 0
    msg = EmailMessage()
    msg['From'] = SMTP_USER
    msg['To'] = ', '.join(destinatarios)
    if cc:
        msg['Cc'] = ', '.join(cc)
    msg['Subject'] = asunto
    msg.set_content(cuerpo)
    # Adjuntos
    if adjuntos:
        for ruta in adjuntos:
            try:
                with open(ruta, 'rb') as f:
                    data = f.read()
                filename = ruta.split('/')[-1]
                msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=filename)
            except Exception as e:
                errores += 1
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
            enviados = len(destinatarios)
    except Exception as e:
        errores += len(destinatarios)
    return enviados, errores

def abrir_gestor_externo(to, subject, body, cc=None):
    import urllib.parse
    mailto = f"mailto:{urllib.parse.quote(to)}"
    params = []
    if cc:
        params.append("cc=" + urllib.parse.quote(cc))
    if subject:
        params.append("subject=" + urllib.parse.quote(subject))
    if body:
        params.append("body=" + urllib.parse.quote(body))
    url = mailto
    if params:
        url += '?' + '&'.join(params)
    webbrowser.open(url)
