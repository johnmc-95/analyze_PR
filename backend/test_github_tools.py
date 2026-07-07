import httpx
import pytest
from unittest.mock import MagicMock, patch

from errors import ExternalServiceError
from tools.github_tools import get_pr_diff, _parse_pr_url

PR_URL = "https://github.com/example/project/pull/42"


def _respuesta(status_code: int, *, headers: dict | None = None, text: str = "") -> MagicMock:
    """Crea una respuesta HTTP simulada de httpx."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.headers = headers or {}
    resp.text = text
    return resp


@patch("tools.github_tools.httpx.get")
def test_get_pr_diff_success(mock_get):
    """Un 200 devuelve el texto del diff tal cual."""
    mock_get.return_value = _respuesta(200, text="diff --git a/x b/x\n+linea")
    assert get_pr_diff(PR_URL) == "diff --git a/x b/x\n+linea"


@patch("tools.github_tools.httpx.get")
def test_get_pr_diff_404_pr_not_found(mock_get):
    mock_get.return_value = _respuesta(404)
    with pytest.raises(ExternalServiceError) as excinfo:
        get_pr_diff(PR_URL)
    assert excinfo.value.error_code == "PR_NOT_FOUND"
    assert excinfo.value.status_code == 404


@patch("tools.github_tools.httpx.get")
def test_get_pr_diff_403_sin_rate_limit_es_forbidden(mock_get):
    """Un 403 con cuota disponible se interpreta como repo privado / sin permisos."""
    mock_get.return_value = _respuesta(403, headers={"X-RateLimit-Remaining": "58"})
    with pytest.raises(ExternalServiceError) as excinfo:
        get_pr_diff(PR_URL)
    assert excinfo.value.error_code == "REPO_FORBIDDEN"
    assert excinfo.value.status_code == 403


@patch("tools.github_tools.httpx.get")
def test_get_pr_diff_403_con_cuota_agotada_es_rate_limit(mock_get):
    """Un 403 con 'X-RateLimit-Remaining: 0' es rate limit primario de GitHub."""
    mock_get.return_value = _respuesta(403, headers={"X-RateLimit-Remaining": "0"})
    with pytest.raises(ExternalServiceError) as excinfo:
        get_pr_diff(PR_URL)
    assert excinfo.value.error_code == "GITHUB_RATE_LIMIT"
    assert excinfo.value.status_code == 429


@patch("tools.github_tools.httpx.get")
def test_get_pr_diff_429_es_rate_limit(mock_get):
    mock_get.return_value = _respuesta(429)
    with pytest.raises(ExternalServiceError) as excinfo:
        get_pr_diff(PR_URL)
    assert excinfo.value.error_code == "GITHUB_RATE_LIMIT"
    assert excinfo.value.status_code == 429


@patch("tools.github_tools.httpx.get")
def test_get_pr_diff_otro_status_es_unavailable(mock_get):
    mock_get.return_value = _respuesta(500)
    with pytest.raises(ExternalServiceError) as excinfo:
        get_pr_diff(PR_URL)
    assert excinfo.value.error_code == "GITHUB_UNAVAILABLE"
    assert excinfo.value.status_code == 502


@patch("tools.github_tools.httpx.get")
def test_get_pr_diff_timeout(mock_get):
    mock_get.side_effect = httpx.TimeoutException("agotado")
    with pytest.raises(ExternalServiceError) as excinfo:
        get_pr_diff(PR_URL)
    assert excinfo.value.error_code == "GITHUB_TIMEOUT"
    assert excinfo.value.status_code == 504


@patch("tools.github_tools.httpx.get")
def test_get_pr_diff_connection_error(mock_get):
    mock_get.side_effect = httpx.ConnectError("sin red")
    with pytest.raises(ExternalServiceError) as excinfo:
        get_pr_diff(PR_URL)
    assert excinfo.value.error_code == "GITHUB_UNAVAILABLE"
    assert excinfo.value.status_code == 502


@patch("tools.github_tools.httpx.get")
def test_get_pr_diff_no_filtra_detalles_tecnicos(mock_get):
    """El mensaje de usuario nunca debe exponer trazas ni internals."""
    mock_get.side_effect = httpx.ConnectError("Connection refused 127.0.0.1:443")
    with pytest.raises(ExternalServiceError) as excinfo:
        get_pr_diff(PR_URL)
    assert "127.0.0.1" not in excinfo.value.user_message


def test_parse_pr_url_valid():
    """
    Verifica que la función interna _parse_pr_url extraiga correctamente 
    el owner, repo y número de PR de una URL estándar de GitHub.
    Es vital para garantizar que las peticiones a la API de GitHub apunten al lugar correcto.
    """
    owner, repo, pr_number = _parse_pr_url("https://github.com/example-owner/example-repo/pull/123")
    assert owner == "example-owner"
    assert repo == "example-repo"
    assert pr_number == "123"


def test_parse_pr_url_with_trailing_slash():
    """
    Comprueba la resiliencia de la extracción ante URLs que terminan con una barra (/).
    Evitamos que el sistema rechace peticiones válidas solo por un error tipográfico
    menor al copiar y pegar la URL.
    """
    owner, repo, pr_number = _parse_pr_url("https://github.com/example-owner/example-repo/pull/123/")
    assert owner == "example-owner"
    assert repo == "example-repo"
    assert pr_number == "123"


def test_parse_pr_url_invalid():
    """
    Asegura que se arroje de inmediato un ValueError si la URL introducida no
    tiene la estructura estricta esperada (por ejemplo apuntar a un /issue/ en vez de /pull/).
    De esta forma prevenimos fallos silenciosos y llamadas innecesarias a la API externa.
    """
    with pytest.raises(ValueError, match="URL de PR no válida"):
        _parse_pr_url("https://github.com/example-owner/example-repo/issues/123")

