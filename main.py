# ============================================================
# MAIN - Punto de entrada del sistema Job Hunter
# ============================================================

from datetime import datetime
from config import EMAIL_DESTINO
from scraper import obtener_todas_las_ofertas
from notifier import enviar_email_resumen
from storage import cargar_vistos, guardar_vistos, cargar_config


def guardar_log(mensaje: str):
    """
    Guarda un registro de actividad en logs/
    """
    try:
        import os
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
    if vistos is None:
        print("⚠️ Búsqueda cancelada: no se pudo acceder a Google Sheets.")
        return
    nuevas = [o for o in todas if o["id"] not in vistos]

    print(f"\n📬 Ofertas nuevas (no notificadas antes): {len(nuevas)}")

    if nuevas:
        # ── Determinar email destino ─────────────────────────
        config = cargar_config()
        if config and not config.get("alertas_activas", True):
            print("🔕 Alertas desactivadas. No se envía email.")
            guardar_vistos([o["id"] for o in nuevas])
            guardar_log("Búsqueda completada — alertas desactivadas")
            return
        destino = (config.get("email_alertas") if config and config.get("email_alertas") else EMAIL_DESTINO)

        # ── Enviar email con resumen ─────────────────────────
        enviar_email_resumen(destino, nuevas)

        # ── Guardar los nuevos IDs en Google Sheets ──────────
        guardar_vistos([o["id"] for o in nuevas])

        guardar_log(f"Búsqueda completada — {len(nuevas)} ofertas nuevas enviadas a {destino}")
    else:
        print("💤 No hay ofertas nuevas por ahora.")
        guardar_log("Búsqueda completada — sin ofertas nuevas")

    print("\n✅ Búsqueda finalizada.")


if __name__ == "__main__":
    ejecutar_busqueda()