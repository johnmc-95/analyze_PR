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
    "final_report": {},
    "status": "consolidation_completed",
    "error_message": None,
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
    "status": "consolidation_completed",
}

MOCK_STATE_ERROR = {
    **MOCK_STATE_CLEAN,
    "status": "error",
    "error_message": "El Pull Request modifica 6 archivos y supera el máximo de 5 permitido (RS-01).",
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
    assert body["findings"][0]["id"] == "BUG-001"
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
