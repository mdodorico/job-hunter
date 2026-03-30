# ============================================================
# CV ADAPTER - Adapta un CV a un aviso de trabajo usando IA
# ============================================================

import anthropic
import requests
from bs4 import BeautifulSoup
import os
from io import BytesIO
from docx import Document
import pdfplumber
from fpdf import FPDF


def extraer_texto_pdf(file_bytes: bytes) -> str:
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        texto = ""
        for page in pdf.pages:
            texto += page.extract_text() or ""
    return texto.strip()


def extraer_texto_word(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])


def scrapear_aviso(url: str) -> str:
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        lineas = [l.strip() for l in soup.get_text(separator="\n").splitlines() if l.strip()]
        return "\n".join(lineas)[:8000]
    except Exception as e:
        print(f"❌ Error scrapeando aviso: {e}")
        return ""


def adaptar_cv(cv_texto: str, aviso_texto: str) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Eres un experto en recursos humanos y en optimización de CVs para sistemas ATS \
(Applicant Tracking Systems).

Tu tarea es adaptar el CV que te voy a pasar para que se ajuste mejor al aviso de trabajo, \
siguiendo estas reglas ESTRICTAS:

REGLAS:
1. NO inventar ni agregar información falsa. Solo trabajar con lo que está en el CV original.
2. NO alucinar experiencias, habilidades ni logros que no estén en el CV.
3. SÍ reorganizar y reformular el contenido existente para destacar lo más relevante.
4. SÍ incorporar palabras clave del aviso donde sean verdaderas y aplicables.
5. SÍ destacar habilidades blandas (comunicación, liderazgo, aprendizaje, adaptabilidad) \
cuando no haya coincidencia técnica exacta.
6. SÍ resaltar habilidades parciales: si el aviso pide A+B y el candidato tiene A, \
destacar A y mencionar disposición a aprender B.
7. Mantener la estructura general del CV original.
8. Devolver el CV adaptado completo, listo para usar.

AVISO DE TRABAJO:
{aviso_texto}

CV ORIGINAL:
{cv_texto}

Devolvé el CV adaptado completo. No incluyas explicaciones ni comentarios fuera del CV."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def generar_word(texto: str) -> bytes:
    doc = Document()
    for linea in texto.split("\n"):
        doc.add_paragraph(linea)
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def generar_pdf(texto: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    pdf.set_auto_page_break(auto=True, margin=15)
    for linea in texto.split("\n"):
        if linea.strip():
            pdf.multi_cell(0, 7, linea)
        else:
            pdf.ln(3)
    return bytes(pdf.output())
