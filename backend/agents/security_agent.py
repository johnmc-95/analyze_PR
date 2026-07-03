import json
import os

from dotenv import load_dotenv
from groq import Groq

from schemas import Finding


# Cargar variables de entorno desde el archivo .env.
load_dotenv()

# API key usada por el cliente de Groq.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def analyze_security(raw_diff: str) -> list[Finding]:
    """
    Analiza el diff de un Pull Request para detectar vulnerabilidades de seguridad.
    Devuelve una lista de Finding validados con Pydantic.
    """
    # Si el diff está vacío, no hay nada que analizar.
    if not raw_diff or not raw_diff.strip():
        return []

    # Cliente de Groq configurado con la API key del entorno.
    client = Groq(api_key=GROQ_API_KEY)

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
        "2. Si no hay vulnerabilidades, devuelve exactamente: {\"findings\": []}.\n"
        "3. La salida debe ser JSON válido, sin markdown ni texto adicional."
    )

    # Prompt de usuario con el diff concreto a revisar.
    user_prompt = f"Aquí está el diff del Pull Request a analizar:\n\n{raw_diff}"

    try:
        # Llamada al modelo forzando respuesta JSON.
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
    except Exception as e:
        # Propagamos un error claro para que el nodo del grafo lo registre.
        raise RuntimeError(f"Error al llamar a la API de Groq: {str(e)}")

    response_text = response.choices[0].message.content
    if not response_text:
        return []

    try:
        # Parsear JSON y validar cada hallazgo con el modelo Finding.
        data = json.loads(response_text)
        raw_findings = data.get("findings", [])

        findings = []
        for raw_f in raw_findings:
            # Forzamos la categoría correcta aunque el modelo se equivoque.
            raw_f["category"] = "security"
            findings.append(Finding(**raw_f))

        return findings
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        raise ValueError(
            "La respuesta de Groq no se pudo procesar como un listado válido "
            f"de Finding: {str(e)}. Contenido: {response_text}"
        )