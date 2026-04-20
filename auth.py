# ============================================================
# AUTH - Manejo de usuarios y sesiones
# ============================================================

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from storage import get_client
import os
import json
import time

SHEET_USERS_ID = os.getenv("SHEET_USERS_ID", "")

_users_cache = {}       # {user_id: User}
_cache_ts = 0
_CACHE_TTL = 300        # segundos


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


def _cargar_cache():
    global _users_cache, _cache_ts
    try:
        sheet = _get_users_sheet()
        if not sheet:
            return
        rows = sheet.get_all_records()
        _users_cache = {
            str(r["id"]): User(str(r["id"]), r["email"], r["password_hash"])
            for r in rows
        }
        _cache_ts = time.time()
    except Exception as e:
        print(f"❌ Error cargando usuarios: {e}")


def _cache_vigente():
    return _users_cache and (time.time() - _cache_ts) < _CACHE_TTL


def cargar_todos_usuarios() -> list:
    if not _cache_vigente():
        _cargar_cache()
    return list(_users_cache.values())


def buscar_usuario_por_id(user_id: str):
    if not _cache_vigente():
        _cargar_cache()
    return _users_cache.get(str(user_id))


def buscar_usuario_por_email(email: str):
    if not _cache_vigente():
        _cargar_cache()
    email_lower = email.lower()
    for u in _users_cache.values():
        if u.email.lower() == email_lower:
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
        nuevo_usuario = User(nuevo_id, email, password_hash)
        sheet.append_row([nuevo_id, email, password_hash])
        _users_cache[nuevo_id] = nuevo_usuario
        return nuevo_usuario, None
    except Exception as e:
        return None, f"Error al registrar: {str(e)}"
