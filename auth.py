# ============================================================
# AUTH - Manejo de usuarios y sesiones
# ============================================================

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from storage import get_client
import os
import json

SHEET_USERS_ID = os.getenv("SHEET_USERS_ID", "")


class User(UserMixin):
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


def _get_users_sheet():
    client = get_client()
    if not client:
        return None
    try:
        return client.open_by_key(SHEET_USERS_ID).sheet1
    except Exception as e:
        print(f"❌ Error abriendo hoja de usuarios: {e}")
        return None


def cargar_todos_usuarios() -> list:
    try:
        sheet = _get_users_sheet()
        if not sheet:
            return []
        rows = sheet.get_all_records()
        return [User(str(r["id"]), r["email"], r["password_hash"]) for r in rows]
    except Exception as e:
        print(f"❌ Error cargando usuarios: {e}")
        return []


def buscar_usuario_por_id(user_id: str):
    usuarios = cargar_todos_usuarios()
    for u in usuarios:
        if u.id == str(user_id):
            return u
    return None


def buscar_usuario_por_email(email: str):
    usuarios = cargar_todos_usuarios()
    for u in usuarios:
        if u.email.lower() == email.lower():
            return u
    return None


def registrar_usuario(email: str, password: str):
    """
    Registra un nuevo usuario. Retorna (usuario, error).
    """
    if buscar_usuario_por_email(email):
        return None, "Ya existe una cuenta con ese email."

    try:
        sheet = _get_users_sheet()
        if not sheet:
            return None, "No se pudo conectar con la base de datos."

        rows = sheet.get_all_records()
        nuevo_id = str(len(rows) + 1)
        password_hash = generate_password_hash(password)
        sheet.append_row([nuevo_id, email, password_hash])

        return User(nuevo_id, email, password_hash), None
    except Exception as e:
        return None, f"Error al registrar: {str(e)}"
