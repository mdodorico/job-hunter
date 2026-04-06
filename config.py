# ============================================================
# JOB HUNTER - Archivo de configuración
# Modificá estos valores para adaptar el sistema a cualquier persona
# ============================================================

# ── DATOS PERSONALES ────────────────────────────────────────
NOMBRE = "Mariana D'Odorico"
EMAIL_DESTINO = "mariana8390@gmail.com"

# ── CONFIGURACIÓN DE BÚSQUEDA ────────────────────────────────
INTERVALO_SEGUNDOS = 3600

# ── SITIOS ACTIVOS ───────────────────────────────────────────
SITIOS = {
    "computrabajo": True,
    "linkedin": True,
    "empleosit": True,
}

# ── KEYWORDS DE BÚSQUEDA ─────────────────────────────────────
KEYWORDS = [
    # QA / Testing
    "QA", "Tester", "Analista QA", "Control de Calidad", "Testing",
    "QA Analyst", "QA Engineer", "Software Tester", "Quality Assurance",

    # Project Manager
    "Project Manager", "Gestor de Proyectos", "Junior PM",

    # Technical Support
    "Soporte Técnico", "Mesa de Ayuda", "Help Desk", "Soporte IT",
    "Technical Support", "IT Support", "Service Desk",

    # Analista Funcional
    "Analista Funcional", "Analista de Sistemas",
    "Functional Analyst", "Systems Analyst",

    # Knowledge Management
    "Knowledge Manager", "Knowledge Management Specialist",
    "Gestor del Conocimiento", "Knowledge Management",

    # Prompt Engineer
    "Prompt Engineer", "Prompt Engineering",

    # Information Manager
    "Information Manager", "Gestor de Información", "Gestor de Informacion",

    # Documentation Specialist
    "Documentation Specialist", "Documentación Técnica", "Documentacion Tecnica",
    "Technical Writer",

    # Frontend / Angular
    "Frontend Developer", "Front-end Developer", "Desarrollador Frontend",
    "Angular Developer", "Angular",
]

# ── KEYWORDS PARA URLs DE BÚSQUEDA ───────────────────────────
KEYWORDS_URL = [
    "qa", "tester", "quality-assurance",
    "project-manager",
    "soporte-tecnico", "help-desk",
    "analista-funcional",
    "knowledge-manager",
    "prompt-engineer",
    "frontend-developer",
    "angular-developer",
]

# ── NIVELES DE SENIORITY ─────────────────────────────────────
NIVELES_ACEPTADOS = [
    "junior", "jr", "jr.", " jr ",
    "trainee", "pasante", "pasantía", "pasantia",
    "intern", "internship", "entry", "entry-level",
    "entry level", "sin experiencia", "no experience",
    "recién graduado", "recien graduado", "recent graduate",
]

NIVELES_EXCLUYENTES = [
    "senior", "sr.", "sr ", " sr",
    "semi-senior", "semisenior", "ssr", "ssr.",
    "lead", "tech lead", "architect", "arquitecto",
    "director", "head of", "principal",
    "experto", "expert",
]

# ── UBICACIONES ACEPTADAS ─────────────────────────────────────
UBICACIONES_ACEPTADAS = [
    # Buenos Aires general
    "buenos aires", "bs. as.", "bs as", "bsas", "b.a.",
    "caba", "capital federal", "capital",
    # GBA norte
    "gran buenos aires", "gba",
    "san isidro", "vicente lópez", "vicente lopez",
    "tigre", "olivos", "florida", "martínez", "martinez",
    "zona norte",
    # 48 barrios oficiales de CABA
    "agronomía", "agronomia", "almagro", "balvanera", "once",
    "barracas", "belgrano", "boedo", "caballito", "chacarita",
    "coghlan", "colegiales", "constitución", "constitucion",
    "flores", "floresta", "la boca", "liniers", "mataderos",
    "microcentro", "monserrat", "montserrat", "monte castro",
    "nueva pompeya", "núñez", "nunez", "palermo",
    "parque avellaneda", "parque chacabuco", "parque chas",
    "parque patricios", "paternal", "puerto madero", "recoleta",
    "retiro", "saavedra", "san cristóbal", "san cristobal",
    "san nicolás", "san nicolas", "san telmo",
    "vélez sarsfield", "velez sarsfield", "versalles",
    "villa crespo", "villa del parque", "villa devoto",
    "villa general mitre", "villa lugano", "villa luro",
    "villa ortúzar", "villa ortuzar", "villa pueyrredón",
    "villa pueyrredon", "villa real", "villa riachuelo",
    "villa santa rita", "villa soldati", "villa urquiza",
    # Remoto y modalidades
    "remoto", "remote", "híbrido", "hibrido", "hybrid",
    "home office", "teletrabajo", "trabajo remoto",
    "modalidad remota", "100% remoto", "full remote",
    "trabajo desde casa", "work from home",
]

# ── INDICADORES DE UBICACIÓN ──────────────────────────────────
INDICADORES_UBICACION = [
    "ubicación", "ubicacion", "localidad", "localización",
    "localizacion", "ciudad", "provincia", "zona", "barrio",
    "lugar de trabajo", "lugar de residencia", "domicilio",
    "presencial", "oficina", "sucursal", "sede",
    "in-office", "on-site", "onsite", "on site",
]

# ── PERFILES IT ACEPTADOS ─────────────────────────────────────
PERFILES_IT = [
    # Carreras
    "sistemas", "informática", "informatica",
    "programación", "programacion", "programador",
    "tecnología de la información", "tecnologia de la informacion",
    "ingeniería en sistemas", "ingenieria en sistemas",
    "ciencias de la computación", "ciencias de la computacion",
    "desarrollo de software", "ingeniería informática",
    "ingenieria informatica", "computación", "computacion",
    # Tecnologías y roles IT
    "software", "it", " ti ", "tech", "tecnología", "tecnologia",
    "angular", "javascript", "typescript", "python", "java",
    "frontend", "front-end", "prompt",
    "qa", "tester", "testing", "scrum", "agile", "kanban",
    "soporte", "helpdesk", "help desk",
    "knowledge management", "documentation",
    # Estudiantes y graduados
    "estudiante", "estudiantes", "graduado", "graduados",
    "recién graduado", "recien graduado", "recent graduate",
    "carrera afín", "carrera afin", "carrera relacionada",
    "carrera de sistemas", "carrera it",
    # Experiencia
    "experiencia en it", "experiencia en tecnología",
    "conocimientos en sistemas", "perfil it", "perfil técnico",
    "perfil tecnico",
]