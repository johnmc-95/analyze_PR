import json
import os
from typing import Any
from dotenv import load_dotenv
from groq import Groq

from schemas import Finding

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API key de Groq desde el entorno
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


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

    # Inicializar el cliente de Groq.
    # Si no se proporciona explícitamente la API key, Groq la leerá de os.environ["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)

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
        "2. Si el diff no presenta ningún bug, error lógico ni problema de rendimiento, devuelve la lista vacía: {\"findings\": []}.\n"
        "3. La salida debe ser estrictamente un JSON válido. No incluyes bloques de markdown (como ```json) ni explicaciones de texto fuera del JSON."
    )

    # El User Prompt contiene el diff a analizar
    user_prompt = f"Aquí está el diff del Pull Request a analizar:\n\n{raw_diff}"

    # Realizar la llamada a Groq
    # Se utiliza response_format={"type": "json_object"} para forzar al modelo a responder con JSON válido.
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,  # Temperatura baja para mayor consistencia y menos creatividad lúdica
        )
    except Exception as e:
        # En producción o integraciones complejas, se podría propagar o manejar. Aquí lo reportamos en el log.
        raise RuntimeError(f"Error al llamar a la API de Groq: {str(e)}")

    response_text = response.choices[0].message.content
    if not response_text:
        return []

    # Parsear y validar los resultados usando Pydantic
    try:
        data = json.loads(response_text)
        raw_findings = data.get("findings", [])
        
        findings = []
        for raw_f in raw_findings:
            # Asegurar que la categoría siempre sea 'bug' en caso de que el modelo haya fallado en esta instrucción
            raw_f["category"] = "bug"
            # Validar y crear la instancia del modelo Pydantic 'Finding'
            findings.append(Finding(**raw_f))
            
        return findings
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        raise ValueError(f"La respuesta de Groq no se pudo procesar como un listado válido de Finding: {str(e)}. Contenido: {response_text}")
