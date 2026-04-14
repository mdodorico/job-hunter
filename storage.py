# ============================================================
# STORAGE - Manejo de ofertas vistas usando Google Sheets
# ============================================================

import gspread
from google.oauth2.service_account import Credentials
import os
import json
from datetime import datetime

# ── Configuración de Google Sheets ───────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_NAME = "job-hunter-vistos"
SHEET_CONFIG = "job-hunter-config"
CREDENTIALS_FILE = "google-credentials.json"


def get_sheet():
    """
    Conecta con Google Sheets y devuelve la hoja de trabajo.
    Funciona tanto en local (archivo JSON) como en Railway (variable de entorno).
    """
    try:
        google_creds_env = os.getenv("GOOGLE_CREDENTIALS")

        if google_creds_env:
            # ── Railway: credenciales desde variable de entorno ──
            creds_dict = json.loads(google_creds_env)
            creds = Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES
            )
        else:
            # ── Local: credenciales desde archivo ───────────────
            creds = Credentials.from_service_account_file(
                CREDENTIALS_FILE, scopes=SCOPES
            )

        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        return sheet

    except Exception as e:
        print(f"❌ Error conectando con Google Sheets: {e}")
        return None


def cargar_vistos():
    """
    Carga los IDs de ofertas ya notificadas desde Google Sheets.
    Retorna None si no se pudo conectar, para evitar enviar duplicados.
    """
    try:
        sheet = get_sheet()
        if not sheet:
            print("❌ No se pudo conectar con Google Sheets. Abortando para evitar duplicados.")
            return None

        ids = sheet.col_values(1)
        return set(ids[1:]) if len(ids) > 1 else set()

    except Exception as e:
        print(f"❌ Error cargando vistos desde Sheets: {e}")
        return None


def get_client():
    try:
        google_creds_env = os.getenv("GOOGLE_CREDENTIALS")
        if google_creds_env:
            creds = Credentials.from_service_account_info(json.loads(google_creds_env), scopes=SCOPES)
        else:
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"❌ Error conectando con Google: {e}")
        return None


def cargar_config() -> dict:
    """
    Carga la configuración guardada desde Google Sheets.
    Retorna None si no hay configuración guardada.
    """
    try:
        client = get_client()
        if not client:
            return None
        try:
            sheet = client.open(SHEET_CONFIG).sheet1
        except Exception:
            return None
        valor = sheet.cell(1, 1).value
        if not valor:
            return None
        return json.loads(valor)
    except Exception as e:
        print(f"❌ Error cargando config: {e}")
        return None


def guardar_config(config: dict):
    """
    Guarda la configuración en Google Sheets como JSON.
    Crea la hoja si no existe.
    """
    try:
        client = get_client()
        if not client:
            return False
        spreadsheet = client.open(SHEET_NAME)
        try:
            sheet = spreadsheet.worksheet(SHEET_CONFIG)
        except Exception:
            sheet = spreadsheet.add_worksheet(title=SHEET_CONFIG, rows=10, cols=2)
        sheet.update("A1", json.dumps(config, ensure_ascii=False))
        print("✅ Configuración guardada en Google Sheets")
        return True
    except Exception as e:
        print(f"❌ Error guardando config: {e}")
        return False


def guardar_vistos(nuevos_ids: list):
    """
    Agrega los nuevos IDs de ofertas vistas a Google Sheets.
    """
    try:
        sheet = get_sheet()
        if not sheet:
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filas = [[id, fecha] for id in nuevos_ids]
        sheet.append_rows(filas)

        print(f"✅ {len(nuevos_ids)} IDs guardados en Google Sheets")

    except Exception as e:
        print(f"❌ Error guardando en Sheets: {e}")