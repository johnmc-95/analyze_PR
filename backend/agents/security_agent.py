from agents.groq_runner import run_groq_analysis
from schemas import Finding


def analyze_security(raw_diff: str) -> list[Finding]:
    """
    Analiza el diff de un Pull Request para detectar vulnerabilidades de seguridad.
    Devuelve una lista de Finding validados con Pydantic.
    """
    # Si el diff está vacío, no hay nada que analizar.
    if not raw_diff or not raw_diff.strip():
        return []

    # Prompt especializado en vulnerabilidades, OWASP Top 10 e inyecciones.
    system_prompt = (
        "Eres un experto en ciberseguridad y revisión segura de código.\n"
        "Tu única tarea es analizar el diff de un Pull Request y detectar vulnerabilidades de seguridad.\n\n"
        "Debes buscar especialmente problemas relacionados con OWASP Top 10, credenciales expuestas, "
        "inyecciones SQL/NoSQL/command injection, XSS, control de acceso roto, manejo inseguro de secretos, "
        "validación insuficiente de entradas, configuración insegura y uso inseguro de dependencias.\n\n"
        "Debes responder ESTRICTAMENTE con un objeto JSON que contenga un campo raíz llamado 'findings', "
        "que debe ser una lista de objetos compatibles con el modelo Pydantic 'Finding':\n"
        "- id (str): Identificador único y corto para el hallazgo, por ejemplo 'SEC-001'.\n"
        "- file_name (str): Archivo donde aparece el problema.\n"
        "- line_number (int | null): Línea aproximada del problema, o null si no se puede determinar.\n"
        "- category (str): Debe ser estrictamente 'security'.\n"
        "- severity (str): Uno de estos valores: 'critical', 'high', 'medium', 'low'.\n"
        "- explanation (str): Explicación en español del riesgo de seguridad y su impacto.\n"
        "- bad_example (str | null): Fragmento problemático del diff.\n"
        "- refactor_suggestion (str): Recomendación clara para mitigar el problema.\n"
        "- code_fix (str | null): Código corregido si se puede proponer de forma segura.\n\n"
        "REGLAS CRÍTICAS:\n"
        "1. No reportes problemas de estilo ni bugs generales si no tienen impacto de seguridad.\n"
        "2. Si no hay vulnerabilidades REALES, devuelve exactamente la lista vacía: {\"findings\": []}. NO inventes vulnerabilidades.\n"
        "3. La salida debe ser JSON válido, sin markdown ni texto adicional.\n"
        "4. Reporta estrictamente vulnerabilidades reales y aplicables al código del PR. No generes escenarios teóricos improbables basados en código inofensivo, ni exijas validaciones criptográficas excesivas para datos en memoria o en pruebas.\n"
        "5. PENALIZACIÓN: Serás penalizado fuertemente si reportas vulnerabilidades inventadas o de muy baja probabilidad."
    )

    # Prompt de usuario con el diff concreto a revisar.
    user_prompt = f"Aquí está el diff del Pull Request a analizar:\n\n{raw_diff}"

    # El helper ejecuta la llamada a Groq y traduce cualquier error externo (RF-08).
    return run_groq_analysis(system_prompt, user_prompt, category="security")