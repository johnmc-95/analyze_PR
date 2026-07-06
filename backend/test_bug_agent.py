import pytest
from unittest.mock import MagicMock, patch

from agents.bug_agent import analyze_bugs
from errors import ExternalServiceError
from graph import bug_analysis, ReviewState
from schemas import Finding


# ── Tests de la función analyze_bugs con Mock de Groq ─────────────────

# El cliente de Groq vive ahora en el helper compartido agents.groq_runner.
@patch("agents.groq_runner.Groq")
def test_analyze_bugs_success(mock_groq_class):
    """
    Verifica que la función analyze_bugs procese correctamente una respuesta JSON válida
    de Groq y la convierta en una lista de objetos Finding de Pydantic.
    """
    # Mock del cliente y de la respuesta de Groq
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_completion = MagicMock()
    # Respuesta simulada en formato JSON
    mock_completion.choices = [
        MagicMock(
            message=MagicMock(
                content='''{
                    "findings": [
                        {
                            "id": "BUG-001",
                            "file_name": "src/utils.py",
                            "line_number": 42,
                            "category": "bug",
                            "severity": "high",
                            "explanation": "División por cero si list está vacía.",
                            "bad_example": "return sum(x) / len(x)",
                            "refactor_suggestion": "Verificar longitud antes de dividir",
                            "code_fix": "return sum(x) / len(x) if len(x) > 0 else 0"
                        }
                    ]
                }'''
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_completion

    # Ejecutar la función con un diff ficticio
    raw_diff = "dummy diff"
    results = analyze_bugs(raw_diff)

    # Aserciones
    assert len(results) == 1
    finding = results[0]
    assert isinstance(finding, Finding)
    assert finding.id == "BUG-001"
    assert finding.file_name == "src/utils.py"
    assert finding.line_number == 42
    assert finding.category == "bug"
    assert finding.severity == "high"
    assert finding.explanation == "División por cero si list está vacía."
    assert finding.bad_example == "return sum(x) / len(x)"
    assert finding.refactor_suggestion == "Verificar longitud antes de dividir"
    assert finding.code_fix == "return sum(x) / len(x) if len(x) > 0 else 0"

    # Verificar que se llamó a Groq con los parámetros correctos
    mock_client.chat.completions.create.assert_called_once()
    kwargs = mock_client.chat.completions.create.call_args[1]
    assert kwargs["model"] == "llama-3.3-70b-versatile"
    assert kwargs["response_format"] == {"type": "json_object"}


@patch("agents.groq_runner.Groq")
def test_analyze_bugs_invalid_json(mock_groq_class):
    """
    Si la respuesta del modelo no es un JSON válido, se lanza un
    ExternalServiceError con código GROQ_INVALID_RESPONSE y mensaje seguro (RF-08).
    """
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client

    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(message=MagicMock(content="Texto plano que no es JSON válido"))
    ]
    mock_client.chat.completions.create.return_value = mock_completion

    with pytest.raises(ExternalServiceError) as excinfo:
        analyze_bugs("dummy diff")

    err = excinfo.value
    assert err.error_code == "GROQ_INVALID_RESPONSE"
    assert err.status_code == 502
    # El mensaje de usuario NO debe filtrar el contenido crudo de la respuesta.
    assert "Texto plano" not in err.user_message


def test_analyze_bugs_empty_diff():
    """
    Verifica que si el diff está vacío, analyze_bugs retorne una lista vacía
    de inmediato sin invocar a Groq.
    """
    assert analyze_bugs("") == []
    assert analyze_bugs("   ") == []


# ── Tests del nodo bug_analysis en el grafo de LangGraph ──────────────

@patch("graph.analyze_bugs")
def test_bug_analysis_node_success(mock_analyze_bugs):
    """
    Verifica que el nodo bug_analysis invoque al agente de bugs y guarde los
    hallazgos serializados (como diccionarios) en el estado.
    """
    # Crear un hallazgo simulado
    mock_finding = Finding(
        id="BUG-002",
        file_name="backend/main.py",
        line_number=15,
        category="bug",
        severity="critical",
        explanation="Variable de entorno no comprobada",
        bad_example="os.environ['API_KEY']",
        refactor_suggestion="Usar os.getenv()",
        code_fix="os.getenv('API_KEY')"
    )
    mock_analyze_bugs.return_value = [mock_finding]

    # Estado inicial de prueba
    initial_state: ReviewState = {
        "pr_url": "https://github.com/example/project/pull/1",
        "raw_diff": "some diff content",
        "files_count": 1,
        "changed_lines": 10,
        "bug_issues": [],
        "security_issues": [],
        "style_issues": [],
        "final_report": {},
        "status": "diff_downloaded",
        "error_message": None
    }

    # Ejecutar el nodo
    new_state = bug_analysis(initial_state)

    # Verificar que se llamó al agente con el diff correcto
    mock_analyze_bugs.assert_called_once_with("some diff content")

    # El nodo paralelo solo retorna bug_issues, sin actualizar status
    assert "status" not in new_state
    assert "error_message" not in new_state
    assert len(new_state["bug_issues"]) == 1
    
    # El hallazgo debe guardarse como diccionario serializado
    saved_finding = new_state["bug_issues"][0]
    assert isinstance(saved_finding, dict)
    assert saved_finding["id"] == "BUG-002"
    assert saved_finding["file_name"] == "backend/main.py"
    assert saved_finding["category"] == "bug"
    assert saved_finding["severity"] == "critical"


@patch("graph.analyze_bugs")
def test_bug_analysis_node_propagates_error(mock_analyze_bugs):
    """
    Si el agente de bugs lanza un ExternalServiceError, el nodo lo registra en el
    estado con su mensaje seguro, código HTTP y código de error (RF-08), sin tocar
    'status' (es un nodo paralelo) ni filtrar el detalle técnico.
    """
    from errors import groq_inference_error

    mock_analyze_bugs.side_effect = groq_inference_error("Conexión con Groq perdida")

    initial_state: ReviewState = {
        "pr_url": "https://github.com/example/project/pull/1",
        "raw_diff": "some diff content",
        "files_count": 1,
        "changed_lines": 10,
        "bug_issues": [],
        "security_issues": [],
        "style_issues": [],
        "final_report": {},
        "status": "diff_downloaded",
        "error_message": None,
    }

    new_state = bug_analysis(initial_state)

    # El nodo paralelo no escribe status; solo propaga los metadatos de error.
    assert "status" not in new_state
    assert new_state["error_status"] == 502
    assert new_state["error_code"] == "GROQ_INFERENCE_ERROR"
    assert "Conexión con Groq perdida" not in new_state["error_message"]
    assert new_state["bug_issues"] == []


def test_bug_analysis_node_skipped_if_previous_error():
    """
    Verifica que si el estado ya tiene un 'error_message', el nodo retorne el estado
    sin hacer nada.
    """
    initial_state: ReviewState = {
        "pr_url": "https://github.com/example/project/pull/1",
        "raw_diff": "some diff content",
        "files_count": 1,
        "changed_lines": 10,
        "bug_issues": [],
        "security_issues": [],
        "style_issues": [],
        "final_report": {},
        "status": "error",
        "error_message": "Error previo de descarga"
    }

    new_state = bug_analysis(initial_state)
    
    # Debe retornar un diccionario vacío indicando que no hay cambios
    assert new_state == {}
