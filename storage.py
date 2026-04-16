# ============================================================
# STORAGE - Manejo de ofertas vistas usando Google Sheets
# ============================================================

import gspread
from google.oauth2.service_account import Credentials
import os
import json
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

CREDENTIALS_FILE = "google-credentials.json"

# IDs de las hojas (evita búsqueda por Drive API)
SHEET_MAIN_ID   = os.getenv("SHEET_MAIN_ID", "")   # contiene vistos + config
SHEET_CONFIG_GID = 518422919                          # gid de la pestaña config
SHEET_USERS_ID  = os.getenv("SHEET_USERS_ID", "")   # archivo separado de usuarios


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


def _get_vistos_sheet():
    client = get_client()
    if not client:
        return None
    try:
        return client.open_by_key(SHEET_MAIN_ID).sheet1
    except Exception as e:
        print(f"❌ Error abriendo hoja de vistos: {e}")
        return None


def _get_config_sheet():
    client = get_client()
    if not client:
        return None
    try:
        return client.open_by_key(SHEET_MAIN_ID).get_worksheet_by_id(SHEET_CONFIG_GID)
    except Exception as e:
        print(f"❌ Error abriendo hoja de config: {e}")
        return None


def cargar_vistos():
    """
    Carga los IDs de ofertas ya notificadas desde Google Sheets.
    Retorna None si no se pudo conectar, para evitar enviar duplicados.
    """
    try:
        sheet = _get_vistos_sheet()
        if not sheet:
            print("❌ No se pudo conectar con Google Sheets. Abortando para evitar duplicados.")
            return None
        ids = sheet.col_values(1)
        return set(ids[1:]) if len(ids) > 1 else set()
    except Exception as e:
        print(f"❌ Error cargando vistos desde Sheets: {e}")
        return None


def guardar_vistos(nuevos_ids: list):
    """
    Agrega los nuevos IDs de ofertas vistas a Google Sheets.
    """
    try:
        sheet = _get_vistos_sheet()
        if not sheet:
            return
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filas = [[id, fecha] for id in nuevos_ids]
        sheet.append_rows(filas)
        print(f"✅ {len(nuevos_ids)} IDs guardados en Google Sheets")
    except Exception as e:
        print(f"❌ Error guardando en Sheets: {e}")


def cargar_config(user_id: str = "default") -> dict:
    """
    Carga la configuración del usuario desde Google Sheets.
    """
    try:
        sheet = _get_config_sheet()
        if not sheet:
            return None
        rows = sheet.get_all_records()
        for row in rows:
            if str(row.get("user_id")) == str(user_id):
                valor = row.get("config_json")
                if valor:
                    return json.loads(valor)
        return None
    except Exception as e:
        print(f"❌ Error cargando config: {e}")
        return None


def guardar_config(config: dict, user_id: str = "default"):
    """
    Guarda la configuración del usuario en Google Sheets.
    """
    try:
        sheet = _get_config_sheet()
        if not sheet:
            return False
        rows = sheet.get_all_records()
        config_json = json.dumps(config, ensure_ascii=False)
        for i, row in enumerate(rows):
            if str(row.get("user_id")) == str(user_id):
                sheet.update_cell(i + 2, 2, config_json)
                print("✅ Configuración actualizada en Google Sheets")
                return True
        sheet.append_row([str(user_id), config_json])
        print("✅ Configuración guardada en Google Sheets")
        return True
    except Exception as e:
        print(f"❌ Error guardando config: {e}")
        return False
