import pytest
from unittest.mock import MagicMock, patch

from agents.groq_runner import run_groq_analysis
from errors import ExternalServiceError
from schemas import Finding

SYSTEM_PROMPT = "system"
USER_PROMPT = "user"


def _completion(content: str) -> MagicMock:
    """Simula la respuesta de Groq con el contenido dado."""
    completion = MagicMock()
    completion.choices = [MagicMock(message=MagicMock(content=content))]
    return completion


@patch("agents.groq_runner.Groq")
def test_run_groq_analysis_success(mock_groq_class):
    """Un JSON válido se convierte en Finding con la categoría forzada."""
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    mock_client.chat.completions.create.return_value = _completion(
        """{"findings": [{
            "id": "BUG-001", "file_name": "a.py", "line_number": 1,
            "category": "algo_incorrecto", "severity": "low",
            "explanation": "x", "refactor_suggestion": "y"
        }]}"""
    )

    results = run_groq_analysis(SYSTEM_PROMPT, USER_PROMPT, category="bug")

    assert len(results) == 1
    assert isinstance(results[0], Finding)
    # La categoría se fuerza al valor pedido aunque el modelo devuelva otra cosa.
    assert results[0].category == "bug"


@patch("agents.groq_runner.Groq")
def test_run_groq_analysis_empty_content_returns_empty(mock_groq_class):
    """Si el modelo devuelve contenido vacío, no hay hallazgos."""
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    mock_client.chat.completions.create.return_value = _completion("")

    assert run_groq_analysis(SYSTEM_PROMPT, USER_PROMPT, category="bug") == []


@patch("agents.groq_runner.Groq")
def test_run_groq_analysis_timeout(mock_groq_class):
    """Un timeout del SDK se traduce a GROQ_TIMEOUT (504)."""
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client

    # El helper detecta el timeout por el nombre de la clase de la excepción.
    class APITimeoutError(Exception):
        pass

    mock_client.chat.completions.create.side_effect = APITimeoutError("agotado")

    with pytest.raises(ExternalServiceError) as excinfo:
        run_groq_analysis(SYSTEM_PROMPT, USER_PROMPT, category="bug")
    assert excinfo.value.error_code == "GROQ_TIMEOUT"
    assert excinfo.value.status_code == 504


@patch("agents.groq_runner.Groq")
def test_run_groq_analysis_inference_error(mock_groq_class):
    """Cualquier otro fallo de la llamada es GROQ_INFERENCE_ERROR (502)."""
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("boom interno")

    with pytest.raises(ExternalServiceError) as excinfo:
        run_groq_analysis(SYSTEM_PROMPT, USER_PROMPT, category="security")
    err = excinfo.value
    assert err.error_code == "GROQ_INFERENCE_ERROR"
    assert err.status_code == 502
    # El detalle técnico no debe filtrarse al usuario.
    assert "boom interno" not in err.user_message


@patch("agents.groq_runner.Groq")
def test_run_groq_analysis_invalid_json(mock_groq_class):
    """Una respuesta no parseable es GROQ_INVALID_RESPONSE (502)."""
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    mock_client.chat.completions.create.return_value = _completion("no soy json {")

    with pytest.raises(ExternalServiceError) as excinfo:
        run_groq_analysis(SYSTEM_PROMPT, USER_PROMPT, category="style")
    assert excinfo.value.error_code == "GROQ_INVALID_RESPONSE"
    assert "no soy json" not in excinfo.value.user_message
