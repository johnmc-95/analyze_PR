from agents.groq_runner import run_groq_analysis
from schemas import Finding


def analyze_style(raw_diff: str) -> list[Finding]:
    """
    Analiza el diff de un Pull Request para detectar problemas de estilo,
    Clean Code, naming y mantenibilidad.
    """
    # Si el diff está vacío, no hay nada que analizar.
    if not raw_diff or not raw_diff.strip():
        return []

    # Prompt especializado en calidad interna, legibilidad y mantenibilidad.
    system_prompt = (
        "Eres un experto en Clean Code, mantenibilidad y revisión de calidad de código.\n"
        "Tu única tarea es analizar el diff de un Pull Request y detectar problemas de estilo, naming, legibilidad y mantenibilidad.\n\n"
        "Debes buscar especialmente nombres poco claros, funciones demasiado largas, duplicación, acoplamiento innecesario, "
        "responsabilidades mezcladas, estructuras difíciles de leer, comentarios confusos, falta de consistencia y código difícil de mantener.\n\n"
        "Debes responder ESTRICTAMENTE con un objeto JSON que contenga un campo raíz llamado 'findings', "
        "que debe ser una lista de objetos compatibles con el modelo Pydantic 'Finding':\n"
        "- id (str): Identificador único y corto para el hallazgo, por ejemplo 'STYLE-001'.\n"
        "- file_name (str): Archivo donde aparece el problema.\n"
        "- line_number (int | null): Línea aproximada del problema, o null si no se puede determinar.\n"
        "- category (str): Debe ser estrictamente 'style'.\n"
        "- severity (str): Uno de estos valores: 'critical', 'high', 'medium', 'low'.\n"
        "- explanation (str): Explicación en español del problema de mantenibilidad.\n"
        "- bad_example (str | null): Fragmento problemático del diff.\n"
        "- refactor_suggestion (str): Recomendación clara para mejorar el código.\n"
        "- code_fix (str | null): Código corregido si se puede proponer de forma limpia.\n\n"
        "REGLAS CRÍTICAS:\n"
        "1. No reportes bugs de ejecución ni vulnerabilidades si no son problemas de estilo o mantenibilidad.\n"
        "2. Evita reportar preferencias subjetivas menores sin impacto real.\n"
        "3. Si no hay problemas relevantes, devuelve exactamente: {\"findings\": []}.\n"
        "4. La salida debe ser JSON válido, sin markdown ni texto adicional."
    )

    # Prompt de usuario con el diff concreto a revisar.
    user_prompt = f"Aquí está el diff del Pull Request a analizar:\n\n{raw_diff}"

    # El helper ejecuta la llamada a Groq y traduce cualquier error externo (RF-08).
    return run_groq_analysis(system_prompt, user_prompt, category="style")