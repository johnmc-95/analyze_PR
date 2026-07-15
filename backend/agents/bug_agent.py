from agents.groq_runner import run_groq_analysis
from schemas import Finding


def analyze_bugs(raw_diff: str) -> list[Finding]:
    """
    Analiza el diff de un Pull Request para detectar bugs, errores lógicos y problemas de rendimiento.
    Conecta con la API de Groq utilizando el modelo llama-3.3-70b-versatile en formato JSON estructurado.

    Args:
        raw_diff (str): El contenido del diff del Pull Request.

    Returns:
        list[Finding]: Una lista de objetos Finding validados mediante Pydantic.
    """
    # Si el diff está vacío, no hay nada que analizar
    if not raw_diff or not raw_diff.strip():
        return []

    # Definir el System Prompt en español con instrucciones detalladas de análisis
    system_prompt = (
        "Eres un experto en revisión de código y aseguramiento de calidad (QA).\n"
        "Tu única tarea es analizar el diff de un Pull Request proporcionado y detectar bugs, errores lógicos y problemas de rendimiento.\n\n"
        "Debes responder ESTRICTAMENTE con un objeto JSON que contenga un campo raíz llamado 'findings', el cual debe ser una lista de objetos.\n"
        "Cada objeto en la lista representa un hallazgo de error y debe cumplir con la estructura del modelo Pydantic 'Finding':\n"
        "- id (str): Identificador único y corto para el hallazgo (ej. 'BUG-001', 'BUG-002', ...)\n"
        "- file_name (str): Nombre del archivo donde se localiza el error (extraído del diff, ej. 'backend/main.py')\n"
        "- line_number (int | null): Número de línea de inicio aproximado donde se encuentra el error (null si no se puede determinar)\n"
        "- category (str): Debe ser estrictamente la cadena 'bug'\n"
        "- severity (str): Nivel de severidad, debe ser uno de: 'critical', 'high', 'medium', 'low'\n"
        "- explanation (str): Explicación detallada en español de cuál es el error lógico, bug o cuello de botella de rendimiento y por qué ocurre\n"
        "- bad_example (str | null): Fragmento exacto o simplificado de la línea o líneas de código problemáticas del diff\n"
        "- refactor_suggestion (str): Sugerencia clara y concisa en español sobre cómo solucionar o refactorizar el código para resolver el problema\n"
        "- code_fix (str | null): Fragmento de código corregido de manera limpia que reemplaza directamente al código problemático\n\n"
        "REGLAS CRÍTICAS:\n"
        "1. No reportes problemas de estilo, legibilidad o seguridad (ej. contraseñas expuestas). Céntrate solo en bugs, errores de ejecución, lógica errónea o problemas graves de rendimiento.\n"
        "2. Si el diff no presenta ningún bug real, error lógico crítico ni problema grave de rendimiento, devuelve la lista vacía: {\"findings\": []}. NO inventes bugs.\n"
        "3. La salida debe ser estrictamente un JSON válido. No incluyes bloques de markdown (como ```json) ni explicaciones de texto fuera del JSON.\n"
        "4. No reportes problemas hipotéticos de escalabilidad extrema o consumo de memoria (ej. fallos por memoria al usar 'set()' o listas) a menos que sea evidente que se procesan grandes volúmenes de datos masivos.\n"
        "5. No exijas manejar casos 'vacíos' u 'opcionales' (ej. verificaciones redundantes de variables) si el contexto o el flujo principal ya es funcional. NO asumas que las variables de entorno o estados faltarán si el código está validado por Tipos o esquemas Pydantic / TypedDict.\n"
        "6. PENALIZACIÓN: Serás penalizado si reportas falsos positivos o problemas teóricos improbables. Ante la duda, no lo reportes."
    )

    # El User Prompt contiene el diff a analizar
    user_prompt = f"Aquí está el diff del Pull Request a analizar:\n\n{raw_diff}"

    # El helper ejecuta la llamada a Groq y traduce cualquier error externo (RF-08).
    return run_groq_analysis(system_prompt, user_prompt, category="bug")
