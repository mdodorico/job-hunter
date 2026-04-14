# ============================================================
# SCRAPER - Extracción de ofertas por sitio
# ============================================================

import requests
import time
import re
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
from config import (
    KEYWORDS as KEYWORDS_DEFAULT,
    KEYWORDS_URL as KEYWORDS_URL_DEFAULT,
    NIVELES_ACEPTADOS, NIVELES_EXCLUYENTES,
    UBICACIONES_ACEPTADAS, INDICADORES_UBICACION, PERFILES_IT, SITIOS
)
from storage import cargar_config

def _get_keywords():
    config = cargar_config()
    if config:
        return config.get("keywords", KEYWORDS_DEFAULT), config.get("keywords_url", KEYWORDS_URL_DEFAULT)
    return KEYWORDS_DEFAULT, KEYWORDS_URL_DEFAULT


def normalizar_id(url: str) -> str:
    """
    Genera un ID estable a partir de una URL eliminando parámetros de tracking.
    Para LinkedIn extrae solo el ID numérico de la oferta.
    """
    parsed = urlparse(url)
    if "linkedin.com" in parsed.netloc:
        match = re.search(r'/jobs/view/(\d+)', parsed.path)
        if match:
            return f"linkedin_{match.group(1)}"
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

# ── HEADERS para no ser bloqueados ──────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


# ============================================================
# FUNCIONES DE FILTRADO
# ============================================================

def oferta_es_relevante(titulo: str, descripcion: str = "") -> bool:
    """
    Verifica si una oferta es relevante usando coincidencia exacta
    y fuzzy matching. Excluye ofertas senior y similares.
    """
    texto = (titulo + " " + descripcion).lower()
    palabras = texto.split()

    # ── Excluyentes ──────────────────────────────────────────
    for termino in NIVELES_EXCLUYENTES:
        if termino in texto:
            return False

    # ── Keyword match ────────────────────────────────────────
    KEYWORDS, _ = _get_keywords()
    tiene_keyword = False
    for keyword in KEYWORDS:
        keyword_lower = keyword.lower()
        if keyword_lower in texto:
            tiene_keyword = True
            break
        if len(keyword_lower) > 4:
            for palabra in palabras:
                if fuzz.ratio(keyword_lower, palabra) >= 80:
                    tiene_keyword = True
                    break
        if tiene_keyword:
            break

    if not tiene_keyword:
        return False

    # ── Nivel ────────────────────────────────────────────────
    especifica_nivel = any(
        n in texto for n in NIVELES_ACEPTADOS + NIVELES_EXCLUYENTES
    )
    if especifica_nivel:
        return any(n in texto for n in NIVELES_ACEPTADOS)

    return True


def texto_menciona_ubicacion(texto: str) -> bool:
    """
    Detecta si un texto hace referencia a una ubicación geográfica.
    """
    return any(ind in texto for ind in INDICADORES_UBICACION)


def ubicacion_es_aceptada(texto: str) -> bool:
    """
    Verifica si el texto menciona al menos una ubicación aceptada.
    """
    return any(u in texto for u in UBICACIONES_ACEPTADAS)


def obtener_detalle_oferta(url: str) -> str:
    """
    Descarga el contenido completo de una oferta para análisis profundo.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return ""
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ").lower()
    except Exception:
        return ""


def oferta_pasa_filtro_profundo(titulo: str, url: str, ubicacion: str = "") -> bool:
    """
    Filtra por ubicación. Si el card ya tiene ubicación específica, la usa
    directamente sin descargar el cuerpo (mucho más rápido).
    """
    # ── Filtro 0: ubicación explícita del card ────────────────
    if ubicacion and ubicacion not in ("Ver oferta", "Argentina"):
        ub_lower = ubicacion.lower()
        if not ubicacion_es_aceptada(ub_lower):
            return False
        return True  # ubicación confirmada, no hace falta descargar el cuerpo

    # ── Filtro 1: título ─────────────────────────────────────
    titulo_lower = titulo.lower()

    entre_parentesis = re.findall(r'\(([^)]+)\)', titulo_lower)
    for fragmento in entre_parentesis:
        fragmento = fragmento.strip()
        if len(fragmento) > 3 and not ubicacion_es_aceptada(fragmento):
            palabras_ubicacion = [
                "ciudad", "provincia", "localidad", "barrio", "caba",
                "gba", "norte", "sur", "oeste", "este", "capital"
            ]
            if " " in fragmento or any(p in fragmento for p in palabras_ubicacion):
                return False
            if fragmento.replace(" ", "").isalpha() and len(fragmento) > 5:
                return False

    if texto_menciona_ubicacion(titulo_lower):
        if not ubicacion_es_aceptada(titulo_lower):
            return False

    # ── Filtro 2: cuerpo del aviso (solo si no hay ubicación del card) ───
    cuerpo = obtener_detalle_oferta(url)

    if cuerpo:
        if texto_menciona_ubicacion(cuerpo):
            if not ubicacion_es_aceptada(cuerpo):
                return False
        if not any(p in cuerpo for p in PERFILES_IT):
            return False

    return True


# ============================================================
# FUNCIONES DE SCRAPING
# ============================================================

def scrape_computrabajo() -> list:
    _, KEYWORDS_URL = _get_keywords()
    ofertas = []
    for keyword in KEYWORDS_URL:
        try:
            url = f"https://ar.computrabajo.com/trabajo-de-{keyword}"
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.find_all("article")

            for card in cards:
                try:
                    titulo_tag = card.find("h2") or card.find("h3")
                    link_tag = card.find("a", href=True)

                    # ── Empresa ──────────────────────────────
                    empresa = "No especificada"
                    empresa_tag = card.find("a", attrs={"offer-grid-article-company-url": True})
                    if empresa_tag:
                        empresa = empresa_tag.text.strip()

                    # ── Ubicación ─────────────────────────────
                    ubicacion = "Argentina"
                    ubicacion_tag = card.find("p", class_="fs16 fc_base mt5")
                    if ubicacion_tag:
                        span = ubicacion_tag.find("span")
                        if span:
                            ubicacion = span.text.strip()

                    titulo = titulo_tag.text.strip() if titulo_tag else ""
                    for palabra in ["Postulado Vista", "Postulado", "Vista"]:
                        titulo = titulo.replace(palabra, "").strip()

                    link = link_tag["href"] if link_tag else ""
                    if not link.startswith("http"):
                        link = "https://ar.computrabajo.com" + link

                    if titulo and oferta_es_relevante(titulo):
                        if oferta_pasa_filtro_profundo(titulo, link, ubicacion=ubicacion):
                            ofertas.append({
                                "titulo": titulo,
                                "empresa": empresa,
                                "ubicacion": ubicacion,
                                "url": link,
                                "fuente": "Computrabajo",
                                "descripcion": "",
                                "id": normalizar_id(link),
                            })
                            time.sleep(1)
                except Exception:
                    continue
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error scraping Computrabajo ({keyword}): {e}")

    print(f"✅ Computrabajo: {len(ofertas)} ofertas relevantes encontradas")
    return ofertas


def scrape_linkedin() -> list:
    _, KEYWORDS_URL = _get_keywords()
    ofertas = []
    searches = [f"{kw.replace('-', ' ').title()} Argentina" for kw in KEYWORDS_URL]

    for search in searches:
        try:
            query = search.replace(" ", "%20")
            url = (
                f"https://www.linkedin.com/jobs/search/?keywords={query}"
                f"&location=Argentina&f_TPR=r86400"
            )
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.find_all(
                "div", class_=lambda x: x and "job-search-card" in str(x).lower()
            )

            for card in cards:
                try:
                    titulo_tag = card.find("h3")
                    empresa_tag = card.find("h4")
                    ubicacion_tag = card.find(
                        "span", class_=lambda x: x and "location" in str(x).lower()
                    )
                    link_tag = card.find("a", href=True)

                    titulo = titulo_tag.text.strip() if titulo_tag else ""
                    empresa = empresa_tag.text.strip() if empresa_tag else "No especificada"
                    ubicacion = ubicacion_tag.text.strip() if ubicacion_tag else "Ver oferta"
                    link = link_tag["href"] if link_tag else ""

                    if titulo and oferta_es_relevante(titulo):
                        if oferta_pasa_filtro_profundo(titulo, link, ubicacion=ubicacion):
                            ofertas.append({
                                "titulo": titulo,
                                "empresa": empresa,
                                "ubicacion": ubicacion,
                                "url": link,
                                "fuente": "LinkedIn",
                                "descripcion": "",
                                "id": normalizar_id(link),
                            })
                            time.sleep(1)
                except Exception:
                    continue
            time.sleep(3)
        except Exception as e:
            print(f"❌ Error scraping LinkedIn ({search}): {e}")

    print(f"✅ LinkedIn: {len(ofertas)} ofertas relevantes encontradas")
    return ofertas


def scrape_empleosit() -> list:
    _, KEYWORDS_URL = _get_keywords()
    ofertas = []
    categorias = [
        "Tester-QA",
        "Analista-Funcional",
        "Analista-de-Procesos-Negocios",
        "Help-Desk-Soporte-Tecnico",
        "Gestor-de-Proyectos-IT",
        "Ciberseguridad-Seguridad-Informatica",
    ]

    for categoria in categorias:
        try:
            url = f"https://www.empleosit.com.ar/find-jobs/{categoria}/"
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.find_all("div", class_=lambda x: x and "job" in str(x).lower())
            if not cards:
                cards = soup.find_all("li", class_=lambda x: x and "job" in str(x).lower())
            if not cards:
                cards = soup.find_all("article")

            for card in cards:
                try:
                    titulo_tag = card.find("h2") or card.find("h3") or card.find("h4")
                    link_tag = card.find("a", href=True)
                    empresa_tag = card.find(
                        ["span", "p", "div"],
                        class_=lambda x: x and any(
                            c in str(x).lower() for c in ["company", "empresa", "employer"]
                        )
                    )

                    titulo = titulo_tag.text.strip() if titulo_tag else ""
                    empresa = empresa_tag.text.strip() if empresa_tag else "No especificada"
                    link = link_tag["href"] if link_tag else ""
                    if not link.startswith("http"):
                        link = "https://www.empleosit.com.ar" + link

                    if titulo and oferta_es_relevante(titulo):
                        if oferta_pasa_filtro_profundo(titulo, link):
                            ofertas.append({
                                "titulo": titulo,
                                "empresa": empresa,
                                "ubicacion": "Argentina",
                                "url": link,
                                "fuente": "EmpleosIT",
                                "descripcion": "",
                                "id": normalizar_id(link),
                            })
                            time.sleep(1)
                except Exception:
                    continue
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error scraping EmpleosIT ({categoria}): {e}")

    print(f"✅ EmpleosIT: {len(ofertas)} ofertas relevantes encontradas")
    return ofertas


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def obtener_todas_las_ofertas() -> list:
    todas = []

    if SITIOS.get("computrabajo"):
        todas += scrape_computrabajo()
    if SITIOS.get("linkedin"):
        todas += scrape_linkedin()
    if SITIOS.get("empleosit"):
        todas += scrape_empleosit()

    # Deduplicar por ID (una misma oferta puede aparecer en varias búsquedas)
    ids_vistos = set()
    unicas = []
    for oferta in todas:
        if oferta["id"] not in ids_vistos:
            ids_vistos.add(oferta["id"])
            unicas.append(oferta)

    print(f"\n📊 Total ofertas únicas encontradas: {len(unicas)}")
    return unicas