import os
import re
import httpx
from dotenv import load_dotenv

from errors import (
    github_forbidden,
    github_pr_not_found,
    github_rate_limit,
    github_timeout,
    github_unavailable,
)

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def _parse_pr_url(pr_url: str) -> tuple[str, str, str]:
    """
    Extrae el owner, el nombre del repo y el número de PR a partir de una URL de GitHub.

    Espera URLs con el formato: https://github.com/<owner>/<repo>/pull/<número>
    Usa una expresión regular para validar el formato antes de extraer los datos,
    lo que evita errores silenciosos si alguien pasa una URL mal formada.

    Devuelve una tupla (owner, repo, pr_number) como strings.
    Lanza ValueError si la URL no coincide con el patrón esperado.
    """
    pattern = r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.match(pattern, pr_url.rstrip("/"))
    if not match:
        raise ValueError(f"URL de PR no válida: {pr_url}")
    return match.group(1), match.group(2), match.group(3)


def get_pr_diff(pr_url: str) -> str:
    """
    Descarga el diff de un Pull Request público de GitHub.

    Lanza ValueError si la URL no es válida, y ExternalServiceError (RF-08) con
    el código HTTP y el mensaje de usuario adecuados ante cualquier error de la
    API de GitHub: PR inexistente (404), repo privado (403), rate limit (429 o
    403 con cuota agotada), timeout (504) o error de conexión (502).
    """
    owner, repo, pr_number = _parse_pr_url(pr_url)

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff",
    }

    # Errores de transporte: timeout y fallos de conexión antes de tener respuesta.
    try:
        response = httpx.get(url, headers=headers, timeout=10.0)
    except httpx.TimeoutException as e:
        raise github_timeout(f"Timeout al llamar a GitHub: {e!r}")
    except httpx.RequestError as e:
        raise github_unavailable(f"Error de conexión con GitHub: {e!r}")

    if response.status_code == 200:
        return response.text

    if response.status_code == 404:
        raise github_pr_not_found(f"GitHub 404 para {pr_url}")

    # GitHub usa 429 (secundario) o 403 con 'X-RateLimit-Remaining: 0' (primario)
    # para señalar rate limit. Un 403 con cuota disponible es falta de permisos.
    if response.status_code == 429:
        raise github_rate_limit("GitHub 429: límite de peticiones alcanzado")
    if response.status_code == 403:
        if response.headers.get("X-RateLimit-Remaining") == "0":
            raise github_rate_limit("GitHub 403: cuota de rate limit agotada")
        raise github_forbidden(f"GitHub 403 para {pr_url}: sin permisos o repo privado")

    raise github_unavailable(f"GitHub respondió {response.status_code}")
