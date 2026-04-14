# ============================================================
# APP - Punto de entrada web para Railway
# ============================================================

from flask import Flask, jsonify, request, render_template, send_file
from main import ejecutar_busqueda
from cv_adapter import (
    extraer_texto_pdf, extraer_texto_word,
    scrapear_aviso, adaptar_cv,
    generar_word, generar_pdf
)
import threading
import os
from io import BytesIO

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/adaptar", methods=["GET"])
def adaptar_page():
    return render_template("adaptar.html")


@app.route("/adaptar", methods=["POST"])
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


@app.route("/run", methods=["POST", "GET"])
def run():
    thread = threading.Thread(target=ejecutar_busqueda)
    thread.start()
    return jsonify({"status": "Búsqueda iniciada ✅"})


@app.route("/diagnostico", methods=["GET"])
def diagnostico():
    import requests
    from bs4 import BeautifulSoup

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resultado = {}

    # ── Test Computrabajo ────────────────────────────────────
    try:
        r = requests.get("https://ar.computrabajo.com/trabajo-de-qa", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.find_all("article")
        resultado["computrabajo"] = {
            "status_code": r.status_code,
            "articles_encontrados": len(articles),
            "primer_articulo_html": str(articles[0])[:600] if articles else "Sin articles",
        }
    except Exception as e:
        resultado["computrabajo"] = {"error": str(e)}

    # ── Test EmpleosIT ───────────────────────────────────────
    try:
        r = requests.get("https://www.empleosit.com.ar/find-jobs/Tester-QA/", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.find_all("article")
        divs_job = soup.find_all("div", class_=lambda x: x and "job" in str(x).lower())
        # Mostrar todos los tags de primer nivel para entender la estructura
        tags_body = [(tag.name, str(tag.get("class", ""))) for tag in soup.body.children if hasattr(tag, "name") and tag.name] if soup.body else []
        resultado["empleosit"] = {
            "status_code": r.status_code,
            "articles_encontrados": len(articles),
            "divs_job_encontrados": len(divs_job),
            "html_muestra": r.text[2000:4000],
        }
    except Exception as e:
        resultado["empleosit"] = {"error": str(e)}

    # ── Test Computrabajo con headers completos ───────────────
    try:
        headers_full = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        r2 = requests.get("https://ar.computrabajo.com/trabajo-de-qa", headers=headers_full, timeout=10)
        soup2 = BeautifulSoup(r2.text, "html.parser")
        articles2 = soup2.find_all("article")
        resultado["computrabajo_headers_completos"] = {
            "status_code": r2.status_code,
            "articles_encontrados": len(articles2),
            "html_muestra": r2.text[2000:4000],
        }
    except Exception as e:
        resultado["computrabajo_headers_completos"] = {"error": str(e)}

    return jsonify(resultado)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
