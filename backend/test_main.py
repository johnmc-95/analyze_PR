import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

MOCK_STATE_CLEAN = {
    "pr_url": "https://github.com/example/project/pull/42",
    "raw_diff": "diff --git a/file.py b/file.py\n+linea nueva",
    "files_count": 1,
    "changed_lines": 1,
    "bug_issues": [],
    "security_issues": [],
    "style_issues": [],
    "final_report": {
        "summary": {
            "status": "clean",
            "total_issues": 0,
            "global_comment": "¡Buen trabajo! El código analizado no presenta problemas relevantes.",
        },
        "findings": [],
        "metadata": {
            "model": "llama-3.3-70b-versatile",
            "files_processed": 1,
            "changed_lines": 1,
        },
    },
    "status": "consolidation_completed",
    "error_message": None,
    "error_status": None,
    "error_code": None,
}

MOCK_STATE_WITH_FINDINGS = {
    **MOCK_STATE_CLEAN,
    "bug_issues": [
        {
            "id": "BUG-001",
            "file_name": "src/utils.py",
            "line_number": 10,
            "category": "bug",
            "severity": "high",
            "explanation": "División por cero potencial.",
            "bad_example": "return x / y",
            "refactor_suggestion": "Verificar que y != 0 antes de dividir.",
            "code_fix": "return x / y if y != 0 else 0",
        }
    ],
    "files_count": 2,
    "changed_lines": 15,
    "final_report": {
        "summary": {
            "status": "issues_found",
            "total_issues": 1,
            "global_comment": "Se detectaron 1 hallazgos: 1 de bugs.",
        },
        "findings": [
            {
                "id": "ISSUE-001",
                "file_name": "src/utils.py",
                "line_number": 10,
                "category": "bug",
                "severity": "high",
                "explanation": "División por cero potencial.",
                "bad_example": "return x / y",
                "refactor_suggestion": "Verificar que y != 0 antes de dividir.",
                "code_fix": "return x / y if y != 0 else 0",
            }
        ],
        "metadata": {
            "model": "llama-3.3-70b-versatile",
            "files_processed": 2,
            "changed_lines": 15,
        },
    },
    "status": "consolidation_completed",
}

MOCK_STATE_ERROR = {
    **MOCK_STATE_CLEAN,
    "status": "error",
    "error_message": "El Pull Request modifica 6 archivos y supera el máximo de 5 permitido (RS-01).",
    "error_status": 422,
    "error_code": "CONSTRAINTS_EXCEEDED",
}


@patch("main.review_graph.invoke", return_value=MOCK_STATE_CLEAN)
def test_initiate_review_clean_pr(mock_invoke):
    response = client.post(
        "/review/initiate",
        json={"pr_url": "https://github.com/example/project/pull/42"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["status"] == "clean"
    assert body["summary"]["total_issues"] == 0
    assert body["findings"] == []
    assert body["metadata"]["model"] == "llama-3.3-70b-versatile"
    assert body["metadata"]["files_processed"] == 1
    mock_invoke.assert_called_once()


@patch("main.review_graph.invoke", return_value=MOCK_STATE_WITH_FINDINGS)
def test_initiate_review_returns_findings(mock_invoke):
    response = client.post(
        "/review/initiate",
        json={"pr_url": "https://github.com/example/project/pull/42"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["status"] == "issues_found"
    assert body["summary"]["total_issues"] == 1
    assert len(body["findings"]) == 1
    assert body["findings"][0]["id"] == "ISSUE-001"
    assert body["metadata"]["files_processed"] == 2
    assert body["metadata"]["changed_lines"] == 15


@patch("main.review_graph.invoke", return_value=MOCK_STATE_ERROR)
def test_initiate_review_returns_422_on_graph_error(mock_invoke):
    response = client.post(
        "/review/initiate",
        json={"pr_url": "https://github.com/example/project/pull/42"},
    )

    assert response.status_code == 422
    assert "RS-01" in response.json()["detail"]


@patch("main.review_graph.invoke", return_value={**MOCK_STATE_CLEAN, "final_report": {}})
def test_initiate_review_returns_500_without_final_report(mock_invoke):
    response = client.post(
        "/review/initiate",
        json={"pr_url": "https://github.com/example/project/pull/42"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "El grafo no generó un reporte final."


def test_initiate_review_rejects_non_github_url():
    response = client.post(
        "/review/initiate",
        json={"pr_url": "https://example.com/owner/project/pull/42"},
    )

    assert response.status_code == 422
    assert "La URL debe tener el formato" in response.json()["detail"][0]["msg"]


def test_initiate_review_rejects_invalid_pull_request_path():
    response = client.post(
        "/review/initiate",
        json={"pr_url": "https://github.com/example/project/issues/42"},
    )

    assert response.status_code == 422
    assert "La URL debe tener el formato" in response.json()["detail"][0]["msg"]


# ── RF-08: cada error externo se traduce a su código HTTP y mensaje seguro ────

# (error_code, status_code, mensaje seguro de usuario) para cada caso externo.
CASOS_ERROR_EXTERNO = [
    ("PR_NOT_FOUND", 404, "No encontramos el Pull Request. Revisa que la URL sea correcta."),
    ("REPO_FORBIDDEN", 403, "No tenemos acceso al repositorio. Puede que sea privado."),
    ("GITHUB_RATE_LIMIT", 429, "GitHub ha limitado temporalmente las peticiones."),
    ("GITHUB_TIMEOUT", 504, "GitHub tardó demasiado en responder."),
    ("GITHUB_UNAVAILABLE", 502, "No pudimos conectar con GitHub."),
    ("GROQ_TIMEOUT", 504, "El servicio de análisis con IA tardó demasiado en responder."),
    ("GROQ_INFERENCE_ERROR", 502, "El servicio de análisis con IA no está disponible ahora mismo."),
    ("GROQ_INVALID_RESPONSE", 502, "El servicio de análisis devolvió una respuesta inesperada."),
]


@pytest.mark.parametrize("error_code, status_code, mensaje", CASOS_ERROR_EXTERNO)
def test_initiate_review_maps_external_error_to_http(error_code, status_code, mensaje):
    """
    El endpoint devuelve el código HTTP correcto y el mensaje seguro cuando el
    grafo registra un error externo. El detail nunca contiene detalles técnicos.
    """
    estado_error = {
        **MOCK_STATE_CLEAN,
        "status": "error",
        "error_message": mensaje,
        "error_status": status_code,
        "error_code": error_code,
    }

    with patch("main.review_graph.invoke", return_value=estado_error):
        response = client.post(
            "/review/initiate",
            json={"pr_url": "https://github.com/example/project/pull/42"},
        )

    assert response.status_code == status_code
    detail = response.json()["detail"]
    assert detail == mensaje
    # El mensaje no debe filtrar rastros técnicos internos.
    for fuga in ("Traceback", "Exception", "str(e)", "httpx", "groq.", "API key"):
        assert fuga not in detail


@patch(
    "main.review_graph.invoke",
    return_value={
        **MOCK_STATE_CLEAN,
        "status": "error",
        "error_message": "Ocurrió un error interno procesando la solicitud. Inténtalo de nuevo.",
        # Sin error_status → main debe caer al 500 por defecto.
        "error_status": None,
        "error_code": "INTERNAL_ERROR",
    },
)
def test_initiate_review_defaults_to_500_when_status_missing(mock_invoke):
    """Si no hay error_status, la API responde 500 con un mensaje genérico seguro."""
    response = client.post(
        "/review/initiate",
        json={"pr_url": "https://github.com/example/project/pull/42"},
    )

    assert response.status_code == 500
    assert "error interno" in response.json()["detail"]
