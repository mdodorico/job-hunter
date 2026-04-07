# ============================================================
# CV ADAPTER - Adapta un CV a un aviso de trabajo usando IA
# ============================================================

import re
import anthropic
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
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
    client = anthropic.Anthropic()

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


def _agregar_parrafo_con_negrita(doc, texto: str, justificado: bool = True):
    p = doc.add_paragraph()
    if justificado:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    partes = re.split(r'(\*\*[^*]+\*\*)', texto)
    for parte in partes:
        if parte.startswith('**') and parte.endswith('**'):
            run = p.add_run(parte[2:-2])
            run.bold = True
        elif parte:
            p.add_run(parte)
    return p


def generar_word(texto: str) -> bytes:
    doc = Document()

    # Estilo base
    estilo = doc.styles['Normal']
    estilo.font.name = 'Calibri'
    estilo.font.size = Pt(11)

    for linea in texto.split("\n"):
        linea_strip = linea.strip()

        # Separadores --- los ignoramos
        if linea_strip in ('---', '***', '___'):
            continue

        # Título principal (#)
        if linea_strip.startswith('# '):
            doc.add_heading(linea_strip[2:], level=1)

        # Subtítulo (##)
        elif linea_strip.startswith('## '):
            doc.add_heading(linea_strip[3:], level=2)

        # Sub-subtítulo (###)
        elif linea_strip.startswith('### '):
            doc.add_heading(linea_strip[4:], level=3)

        # Línea vacía
        elif not linea_strip:
            doc.add_paragraph('')

        # Párrafo normal (con soporte de negritas)
        else:
            _agregar_parrafo_con_negrita(doc, linea_strip)

    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def _limpiar_para_pdf(texto: str) -> str:
    reemplazos = {
        '\u2013': '-', '\u2014': '-',
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"',
        '\u2022': '-', '\u2026': '...',
        '\u00b7': '-', '\u2015': '-',
        '\u00e2': 'a', '\u20ac': 'EUR',
    }
    for char, reemplazo in reemplazos.items():
        texto = texto.replace(char, reemplazo)
    return texto.encode('latin-1', errors='ignore').decode('latin-1')


def generar_pdf(texto: str) -> bytes:
    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    pdf.set_auto_page_break(auto=True, margin=20)
    for linea in texto.split("\n"):
        linea = _limpiar_para_pdf(linea)
        try:
            if linea.strip():
                pdf.multi_cell(0, 7, linea)
            else:
                pdf.ln(3)
        except Exception:
            pdf.ln(3)
    return bytes(pdf.output())
