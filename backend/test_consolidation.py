from graph import ReviewState, consolidation
from schemas import ReviewResponse


def _base_state() -> ReviewState:
    """Crea un estado base con métricas del PR y listas vacías de hallazgos."""
    return {
        "pr_url": "https://github.com/example/project/pull/1",
        "raw_diff": "diff --git a/main.py b/main.py",
        "files_count": 2,
        "changed_lines": 25,
        "bug_issues": [],
        "security_issues": [],
        "style_issues": [],
        "final_report": {},
        "status": "constraints_validated",
        "error_message": None,
    }


def _finding(category: str, explanation: str, file_name: str = "backend/main.py") -> dict:
    """Construye un hallazgo válido para alimentar el nodo de consolidación."""
    return {
        "id": "TEMP-001",
        "file_name": file_name,
        "line_number": 10,
        "category": category,
        "severity": "high",
        "explanation": explanation,
        "bad_example": "codigo_problematico()",
        "refactor_suggestion": "Refactorizar el código problemático.",
        "code_fix": "codigo_corregido()",
    }


def test_consolidation_builds_valid_review_response_with_issues():
    """Unifica hallazgos, reasigna IDs y genera un ReviewResponse válido."""
    state = _base_state()
    state["bug_issues"] = [
        _finding("bug", "Posible división por cero."),
    ]
    state["security_issues"] = [
        _finding("security", "Credencial expuesta en el código."),
    ]
    state["style_issues"] = [
        _finding("style", "Nombre de variable poco descriptivo."),
    ]

    result = consolidation(state)
    final_report = result["final_report"]

    # Validar que el JSON final cumple el contrato Pydantic.
    response = ReviewResponse(**final_report)

    assert result["status"] == "issues_found"
    assert response.summary.status == "issues_found"
    assert response.summary.total_issues == 3
    assert len(response.findings) == 3
    assert [finding.id for finding in response.findings] == [
        "ISSUE-001",
        "ISSUE-002",
        "ISSUE-003",
    ]
    assert response.metadata.files_processed == 2
    assert response.metadata.changed_lines == 25


def test_consolidation_removes_duplicate_findings():
    """Elimina duplicados aunque vengan de agentes distintos."""
    duplicate = _finding("bug", "Mismo problema detectado por dos agentes.")

    state = _base_state()
    state["bug_issues"] = [duplicate]
    state["security_issues"] = [
        {
            **duplicate,
            "id": "SEC-999",
            "category": "security",
        }
    ]

    result = consolidation(state)
    response = ReviewResponse(**result["final_report"])

    assert response.summary.total_issues == 1
    assert len(response.findings) == 1
    assert response.findings[0].id == "ISSUE-001"


def test_consolidation_returns_clean_response_without_issues():
    """Si no hay hallazgos, genera una respuesta clean válida."""
    result = consolidation(_base_state())
    response = ReviewResponse(**result["final_report"])

    assert result["status"] == "clean"
    assert response.summary.status == "clean"
    assert response.summary.total_issues == 0
    assert response.findings == []
    assert "no presenta problemas relevantes" in response.summary.global_comment
