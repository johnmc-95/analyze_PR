from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_initiate_review_returns_mock_contract_for_valid_github_pr():
    response = client.post(
        "/review/initiate",
        json={"pr_url": "https://github.com/example/project/pull/42"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "summary": {
            "status": "clean",
            "total_issues": 0,
            "global_comment": (
                "La URL del PR https://github.com/example/project/pull/42 "
                "es valida. El analisis con LangGraph aun no esta disponible."
            ),
        },
        "findings": [],
        "metadata": {
            "model": "mock",
            "files_processed": 0,
            "changed_lines": 0,
        },
    }


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
