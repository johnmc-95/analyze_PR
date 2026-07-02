import os
import re
import httpx
from dotenv import load_dotenv

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

    Lanza ValueError si la URL no es válida, y RuntimeError si la API
    devuelve un error (PR inexistente, repo privado, rate limit, etc.).
    """
    owner, repo, pr_number = _parse_pr_url(pr_url)

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff",
    }

    response = httpx.get(url, headers=headers)

    if response.status_code == 404:
        raise RuntimeError(f"PR no encontrado o repositorio privado: {pr_url}")
    if response.status_code == 403:
        raise RuntimeError("Rate limit de GitHub alcanzado o token sin permisos.")
    if response.status_code != 200:
        raise RuntimeError(f"Error de GitHub API: {response.status_code}")

    return response.text
