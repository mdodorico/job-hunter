# ============================================================
# MAIN - Punto de entrada del sistema Job Hunter
# ============================================================

import json
import os
import time
from datetime import datetime
from config import EMAIL_DESTINO, INTERVALO_SEGUNDOS, NOMBRE
from scraper import obtener_todas_las_ofertas
from notifier import enviar_email_resumen

# ── Archivo donde guardamos ofertas ya vistas ────────────────
ARCHIVO_VISTOS = os.path.join("data", "ofertas_vistas.json")


def cargar_vistos() -> set:
    """
    Carga los IDs de ofertas ya notificadas para no repetirlas.
    """
    if not os.path.exists(ARCHIVO_VISTOS):
        return set()
    try:
        with open(ARCHIVO_VISTOS, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def guardar_vistos(vistos: set):
    """
    Guarda los IDs de ofertas ya notificadas.
    """
    try:
        with open(ARCHIVO_VISTOS, "w", encoding="utf-8") as f:
            json.dump(list(vistos), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Error guardando vistos: {e}")


def guardar_log(mensaje: str):
    """
    Guarda un registro de actividad en logs/
    """
    try:
        archivo_log = os.path.join(
            "logs", f"log_{datetime.now().strftime('%Y%m')}.txt"
        )
        with open(archivo_log, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {mensaje}\n")
    except Exception:
        pass


def ejecutar_busqueda():
    """
    Ejecuta una búsqueda completa y notifica las ofertas nuevas.
    """
    print(f"\n{'='*50}")
    print(f"🔍 Iniciando búsqueda — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    # ── Obtener todas las ofertas ────────────────────────────
    todas = obtener_todas_las_ofertas()

    # ── Filtrar las que ya vimos ─────────────────────────────
    vistos = cargar_vistos()
    nuevas = [o for o in todas if o["id"] not in vistos]

    print(f"\n📬 Ofertas nuevas (no notificadas antes): {len(nuevas)}")

    if nuevas:
        # ── Enviar email con resumen ─────────────────────────
        enviar_email_resumen(EMAIL_DESTINO, nuevas)

        # ── Guardar los IDs como vistos ──────────────────────
        for o in nuevas:
            vistos.add(o["id"])
        guardar_vistos(vistos)

        guardar_log(f"Búsqueda completada — {len(nuevas)} ofertas nuevas enviadas a {EMAIL_DESTINO}")
    else:
        print("💤 No hay ofertas nuevas por ahora.")
        guardar_log("Búsqueda completada — sin ofertas nuevas")

    print(f"\n⏰ Próxima búsqueda en {INTERVALO_SEGUNDOS // 60} minutos")


def main():
    """
    Loop principal — ejecuta la búsqueda cada X minutos indefinidamente.
    """
    print(f"🚀 Job Hunter iniciado para {NOMBRE}")
    print(f"📧 Notificaciones a: {EMAIL_DESTINO}")
    print(f"⏰ Intervalo de búsqueda: {INTERVALO_SEGUNDOS // 60} minutos")

    while True:
        ejecutar_busqueda()
        time.sleep(INTERVALO_SEGUNDOS)


if __name__ == "__main__":
    main()