# ============================================================
# APP - Punto de entrada web para Railway
# ============================================================

from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from main import ejecutar_busqueda
from cv_adapter import (
    extraer_texto_pdf, extraer_texto_word,
    scrapear_aviso, adaptar_cv,
    generar_word, generar_pdf
)
from auth import buscar_usuario_por_id, buscar_usuario_por_email, registrar_usuario
import threading
import os
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "job-hunter-secret-2024")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"


@login_manager.user_loader
def load_user(user_id):
    return buscar_usuario_por_id(user_id)


# ── Auth routes ──────────────────────────────────────────────

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    user = buscar_usuario_por_email(email)
    if not user or not user.check_password(password):
        return render_template("login.html", error="Email o contraseña incorrectos.")
    login_user(user)
    return redirect(url_for("home"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_page"))


@app.route("/registro", methods=["GET"])
def registro_page():
    return render_template("registro.html")


@app.route("/registro", methods=["POST"])
def registro_post():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    password2 = request.form.get("password2", "")
    if not email or not password:
        return render_template("registro.html", error="Completá todos los campos.")
    if password != password2:
        return render_template("registro.html", error="Las contraseñas no coinciden.")
    if len(password) < 6:
        return render_template("registro.html", error="La contraseña debe tener al menos 6 caracteres.")
    user, error = registrar_usuario(email, password)
    if error:
        return render_template("registro.html", error=error)
    login_user(user)
    return redirect(url_for("home"))


# ── App routes ───────────────────────────────────────────────

@app.route("/")
@login_required
def home():
    return render_template("index.html")


@app.route("/adaptar", methods=["GET"])
@login_required
def adaptar_page():
    return render_template("adaptar.html")


@app.route("/adaptar", methods=["POST"])
@login_required
def adaptar_cv_route():
    url = request.form.get("url", "").strip()
    formato = request.form.get("formato", "word")
    cv_file = request.files.get("cv")

    if not url or not cv_file:
        return jsonify({"error": "Faltan datos. Completá el link y subí tu CV."}), 400

    # ── Extraer texto del CV ─────────────────────────────────
    file_bytes = cv_file.read()
    filename = cv_file.filename.lower()

    if filename.endswith(".pdf"):
        cv_texto = extraer_texto_pdf(file_bytes)
    elif filename.endswith(".docx") or filename.endswith(".doc"):
        cv_texto = extraer_texto_word(file_bytes)
    else:
        return jsonify({"error": "Formato no soportado. Usá PDF, DOC o DOCX."}), 400

    if not cv_texto:
        return jsonify({"error": "No se pudo leer el contenido del CV."}), 400

    # ── Scrapear el aviso ────────────────────────────────────
    aviso_texto = scrapear_aviso(url)
    if not aviso_texto:
        return jsonify({"error": "No se pudo leer el aviso. Verificá que el link sea accesible."}), 400

    # ── Adaptar con IA ───────────────────────────────────────
    try:
        cv_adaptado = adaptar_cv(cv_texto, aviso_texto)
    except Exception as e:
        return jsonify({"error": f"Error al procesar con IA: {str(e)}"}), 500

    # ── Generar archivo de salida ────────────────────────────
    if formato == "pdf":
        output = generar_pdf(cv_adaptado)
        mimetype = "application/pdf"
        nombre_archivo = "cv_adaptado.pdf"
    else:
        output = generar_word(cv_adaptado)
        mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        nombre_archivo = "cv_adaptado.docx"

    return send_file(
        BytesIO(output),
        mimetype=mimetype,
        as_attachment=True,
        download_name=nombre_archivo
    )


@app.route("/configurar", methods=["GET"])
@login_required
def configurar_page():
    from storage import cargar_config
    from config import KEYWORDS as KEYWORDS_DEFAULT, KEYWORDS_URL as KEYWORDS_URL_DEFAULT
    config = cargar_config(user_id=current_user.id) or {
        "keywords": KEYWORDS_DEFAULT,
        "keywords_url": KEYWORDS_URL_DEFAULT,
    }
    return render_template("configurar.html", config=config)


@app.route("/configurar/generar", methods=["POST"])
@login_required
def configurar_generar():
    import anthropic, json
    data = request.get_json()
    puestos = data.get("puestos", "")

    if not puestos:
        return jsonify({"error": "Ingresá al menos un puesto."}), 400

    client = anthropic.Anthropic()
    prompt = f"""Sos un experto en búsqueda de empleo en Argentina.
El usuario quiere buscar trabajo en los siguientes puestos o áreas:

{puestos}

Generá dos listas en formato JSON:
1. "keywords": lista de términos de búsqueda completos (títulos de puestos, variantes en español e inglés)
2. "keywords_url": lista de los mismos términos en formato URL (minúsculas, palabras separadas por guiones, sin caracteres especiales)

Respondé ÚNICAMENTE con un JSON válido, sin explicaciones. Ejemplo de formato:
{{
  "keywords": ["QA Analyst", "Tester", "Analista QA"],
  "keywords_url": ["qa-analyst", "tester", "analista-qa"]
}}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        respuesta = message.content[0].text.strip()
        respuesta = respuesta.replace("```json", "").replace("```", "").strip()
        config_generada = json.loads(respuesta)
        return jsonify(config_generada)
    except Exception as e:
        return jsonify({"error": f"Error generando configuración: {str(e)}"}), 500


@app.route("/configurar/guardar", methods=["POST"])
@login_required
def configurar_guardar():
    from storage import guardar_config
    data = request.get_json()
    ok = guardar_config(data, user_id=current_user.id)
    if ok:
        return jsonify({"status": "Configuración guardada ✅"})
    return jsonify({"error": "No se pudo guardar la configuración."}), 500


@app.route("/run", methods=["POST", "GET"])
def run():
    thread = threading.Thread(target=ejecutar_busqueda)
    thread.start()
    return jsonify({"status": "Búsqueda iniciada ✅"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
