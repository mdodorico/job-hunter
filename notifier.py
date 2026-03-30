# ============================================================
# NOTIFIER - Envío de emails con las alertas de trabajo
# ============================================================

import resend
from dotenv import load_dotenv
import os

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
EMAIL_REMITENTE = "Job Hunter <onboarding@resend.dev>"


def enviar_email_resumen(destinatario: str, ofertas: list):
    """
    Envía un resumen con múltiples ofertas encontradas en una misma ejecución.
    """
    if not ofertas:
        return

    try:
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

        resend.Emails.send({
            "from": EMAIL_REMITENTE,
            "to": destinatario,
            "subject": f"🚀 Job Hunter — {len(ofertas)} nuevas ofertas encontradas",
            "html": html,
        })

        print(f"✅ Resumen enviado: {len(ofertas)} ofertas")
        return True

    except Exception as e:
        print(f"❌ Error enviando resumen: {e}")
        return False
