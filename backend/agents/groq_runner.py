"""
Helper compartido para las llamadas a Groq de los agentes (RF-08).

Los tres agentes (bugs, seguridad, estilo) solo se diferencian en su
``system_prompt`` y en la ``category`` que fuerzan en los hallazgos. Toda la
mecánica común —crear el cliente, invocar el modelo, leer la respuesta, parsear
el JSON y validar cada ``Finding``— vive aquí para evitar triplicar el código y,
sobre todo, para centralizar la traducción de errores de Groq a
``ExternalServiceError`` con mensajes seguros para el usuario.
"""

import json
import os

from dotenv import load_dotenv
from groq import Groq

from errors import groq_inference_error, groq_invalid_response, groq_timeout
from schemas import Finding

# Cargar variables de entorno desde el archivo .env.
load_dotenv()

# API key usada por el cliente de Groq.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Modelo usado por todos los agentes.
GROQ_MODEL = "llama-3.3-70b-versatile"


def _es_timeout(error: Exception) -> bool:
    """
    Detecta si un error de Groq es un timeout de forma robusta.

    Se apoya en ``groq.APITimeoutError`` cuando está disponible y, como red de
    seguridad, comprueba el nombre de la clase para no depender de la versión
    exacta del SDK.
    """
    try:
        from groq import APITimeoutError

        if isinstance(error, APITimeoutError):
            return True
    except Exception:  # noqa: BLE001 - si el símbolo no existe, seguimos con el fallback
        pass

    return "timeout" in type(error).__name__.lower()


def run_groq_analysis(
    system_prompt: str, user_prompt: str, category: str
) -> list[Finding]:
    """
    Ejecuta un análisis contra Groq y devuelve una lista de ``Finding`` validados.

    Args:
        system_prompt: Instrucciones especializadas del agente.
        user_prompt: Mensaje de usuario (normalmente el diff a analizar).
        category: Categoría a forzar en cada hallazgo ('bug' | 'security' | 'style').

    Raises:
        ExternalServiceError: si Groq da timeout, falla la inferencia o devuelve
        una respuesta que no se puede procesar. El mensaje es seguro para el
        usuario; el detalle técnico queda solo para logging/trazabilidad.
    """
    # Cliente de Groq. Si la key es None, Groq intentará leer GROQ_API_KEY del entorno.
    client = Groq(api_key=GROQ_API_KEY)

    # Llamada al modelo forzando respuesta JSON.
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,  # Temperatura baja para mayor consistencia.
        )
    except Exception as e:  # noqa: BLE001 - traducimos cualquier error del SDK
        if _es_timeout(e):
            raise groq_timeout(f"Timeout en la inferencia de Groq: {e!r}")
        raise groq_inference_error(f"Fallo en la inferencia de Groq: {e!r}")

    response_text = response.choices[0].message.content
    if not response_text:
        return []

    # Parsear el JSON y validar cada hallazgo con el modelo Finding.
    try:
        data = json.loads(response_text)
        raw_findings = data.get("findings", [])

        findings = []
        for raw_f in raw_findings:
            # Forzamos la categoría correcta aunque el modelo se equivoque.
            raw_f["category"] = category
            findings.append(Finding(**raw_f))

        return findings
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        # El contenido crudo va SOLO al detalle técnico, nunca al usuario.
        raise groq_invalid_response(
            f"Respuesta de Groq no procesable: {e!r}. Contenido: {response_text}"
        )
