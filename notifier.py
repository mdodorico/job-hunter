# ============================================================
# NOTIFIER - Envío de emails con las alertas de trabajo
# ============================================================

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_REMITENTE = os.getenv("EMAIL_REMITENTE")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def enviar_email(destinatario: str, oferta: dict):
    """
    Envía un email con los datos de una oferta laboral.
    oferta = {
        "titulo": str,
        "empresa": str,
        "ubicacion": str,
        "url": str,
        "fuente": str,
        "descripcion": str (opcional)
    }
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚀 Nueva oferta: {oferta['titulo']} en {oferta['empresa']}"
        msg["From"] = EMAIL_REMITENTE
        msg["To"] = destinatario

        # ── Cuerpo del email en HTML ─────────────────────────
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
            <div style="background-color: #4A90D9; padding: 20px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0;">🎯 Job Hunter</h1>
                <p style="color: #e8f4fd; margin: 5px 0 0 0;">Nueva oferta detectada</p>
            </div>
            <div style="border: 1px solid #ddd; padding: 25px; border-radius: 0 0 8px 8px;">
                <h2 style="color: #2c3e50;">{oferta['titulo']}</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #7f8c8d; width: 120px;">🏢 Empresa</td>
                        <td style="padding: 8px 0; font-weight: bold;">{oferta['empresa']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #7f8c8d;">📍 Ubicación</td>
                        <td style="padding: 8px 0;">{oferta['ubicacion']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #7f8c8d;">🌐 Fuente</td>
                        <td style="padding: 8px 0;">{oferta['fuente']}</td>
                    </tr>
                </table>

                {f'<p style="color: #555; margin-top: 15px;">{oferta["descripcion"]}</p>' 
                 if oferta.get('descripcion') else ''}

                <div style="margin-top: 25px; text-align: center;">
                    <a href="{oferta['url']}" 
                       style="background-color: #4A90D9; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; font-size: 16px;">
                        Ver oferta completa →
                    </a>
                </div>
            </div>
            <p style="color: #bdc3c7; font-size: 12px; text-align: center; margin-top: 15px;">
                Job Hunter · Alerta automática de empleo
            </p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

       # ── Envío via Gmail SMTP ─────────────────────────────
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
            server.sendmail(EMAIL_REMITENTE, destinatario, msg.as_string())

        print(f"✅ Email enviado: {oferta['titulo']} en {oferta['empresa']}")
        return True

    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False


def enviar_email_resumen(destinatario: str, ofertas: list):
    """
    Envía un resumen con múltiples ofertas encontradas en una misma ejecución.
    """
    if not ofertas:
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚀 Job Hunter — {len(ofertas)} nuevas ofertas encontradas"
        msg["From"] = EMAIL_REMITENTE
        msg["To"] = destinatario

        filas = ""
        for o in ofertas:
            filas += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 12px 8px;">
                    <a href="{o['url']}" style="color: #4A90D9; font-weight: bold; 
                       text-decoration: none;">{o['titulo']}</a>
                </td>
                <td style="padding: 12px 8px;">{o['empresa']}</td>
                <td style="padding: 12px 8px;">{o['ubicacion']}</td>
                <td style="padding: 12px 8px; color: #7f8c8d;">{o['fuente']}</td>
            </tr>
            """

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto;">
            <div style="background-color: #4A90D9; padding: 20px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0;">🎯 Job Hunter</h1>
                <p style="color: #e8f4fd; margin: 5px 0 0 0;">
                    {len(ofertas)} nuevas ofertas detectadas
                </p>
            </div>
            <div style="border: 1px solid #ddd; padding: 25px; border-radius: 0 0 8px 8px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 10px 8px; text-align: left;">Puesto</th>
                            <th style="padding: 10px 8px; text-align: left;">Empresa</th>
                            <th style="padding: 10px 8px; text-align: left;">Ubicación</th>
                            <th style="padding: 10px 8px; text-align: left;">Fuente</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas}
                    </tbody>
                </table>
            </div>
            <p style="color: #bdc3c7; font-size: 12px; text-align: center; margin-top: 15px;">
                Job Hunter · Alerta automática de empleo
            </p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        # ── Envío via Gmail SMTP ─────────────────────────────
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
            server.sendmail(EMAIL_REMITENTE, destinatario, msg.as_string())

        print(f"✅ Resumen enviado: {len(ofertas)} ofertas")
        return True

    except Exception as e:
        print(f"❌ Error enviando resumen: {e}")
        return False