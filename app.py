# ============================================================
# APP - Punto de entrada web para Railway
# Make llama a este endpoint cada hora para disparar la búsqueda
# ============================================================

from flask import Flask, jsonify
from main import ejecutar_busqueda
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "Job Hunter activo ✅"})

@app.route("/run", methods=["POST", "GET"])
def run():
    """
    Endpoint que Make llama cada hora para disparar la búsqueda.
    Corre en un thread separado para no bloquear la respuesta.
    """
    thread = threading.Thread(target=ejecutar_busqueda)
    thread.start()
    return jsonify({"status": "Búsqueda iniciada ✅"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)