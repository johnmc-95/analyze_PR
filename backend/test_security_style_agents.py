from unittest.mock import MagicMock, patch

from agents.security_agent import analyze_security
from agents.style_agent import analyze_style
from graph import ReviewState, security_analysis, style_analysis
from schemas import Finding


def _estado(raw_diff: str = "some diff content") -> ReviewState:
    """Crea un estado base del grafo para probar los nodos de agentes."""
    return {
        "pr_url": "https://github.com/example/project/pull/1",
        "raw_diff": raw_diff,
        "files_count": 1,
        "changed_lines": 10,
        "bug_issues": [],
        "security_issues": [],
        "style_issues": [],
        "final_report": {},
        "status": "constraints_validated",
        "error_message": None,
    }


@patch("agents.security_agent.Groq")
def test_analyze_security_success(mock_groq_class):
    """Comprueba que el agente de seguridad convierte JSON válido en Finding."""
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client

    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(
            message=MagicMock(
                content="""{
                    "findings": [
                        {
                            "id": "SEC-001",
                            "file_name": "backend/main.py",
                            "line_number": 12,
                            "category": "security",
                            "severity": "critical",
                            "explanation": "Token expuesto en el código fuente.",
                            "bad_example": "API_KEY = 'secret'",
                            "refactor_suggestion": "Mover el secreto a variables de entorno.",
                            "code_fix": "API_KEY = os.getenv('API_KEY')"
                        }
                    ]
                }"""
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_completion

    results = analyze_security("dummy diff")

    assert len(results) == 1
    assert isinstance(results[0], Finding)
    assert results[0].category == "security"
    assert results[0].id == "SEC-001"


@patch("agents.style_agent.Groq")
def test_analyze_style_success(mock_groq_class):
    """Comprueba que el agente de estilo convierte JSON válido en Finding."""
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client

    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(
            message=MagicMock(
                content="""{
                    "findings": [
                        {
                            "id": "STYLE-001",
                            "file_name": "frontend/src/App.jsx",
                            "line_number": 30,
                            "category": "style",
                            "severity": "medium",
                            "explanation": "La función mezcla responsabilidades y reduce la mantenibilidad.",
                            "bad_example": "function App() { /* demasiada lógica */ }",
                            "refactor_suggestion": "Extraer la lógica a funciones o componentes más pequeños.",
                            "code_fix": null
                        }
                    ]
                }"""
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_completion

    results = analyze_style("dummy diff")

    assert len(results) == 1
    assert isinstance(results[0], Finding)
    assert results[0].category == "style"
    assert results[0].id == "STYLE-001"


def test_analyze_security_empty_diff():
    """Si no hay diff, el agente de seguridad devuelve una lista vacía."""
    assert analyze_security("") == []
    assert analyze_security("   ") == []


def test_analyze_style_empty_diff():
    """Si no hay diff, el agente de estilo devuelve una lista vacía."""
    assert analyze_style("") == []
    assert analyze_style("   ") == []


@patch("graph.analyze_security")
def test_security_analysis_node_success(mock_analyze_security):
    """El nodo de seguridad guarda los hallazgos serializados en el estado."""
    mock_analyze_security.return_value = [
        Finding(
            id="SEC-002",
            file_name="backend/auth.py",
            line_number=8,
            category="security",
            severity="high",
            explanation="Entrada de usuario sin validar antes de una consulta.",
            bad_example="query = f'SELECT * FROM users WHERE id={user_id}'",
            refactor_suggestion="Usar consultas parametrizadas.",
            code_fix="cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))",
        )
    ]

    result = security_analysis(_estado())

    mock_analyze_security.assert_called_once_with("some diff content")
    assert "status" not in result
    assert len(result["security_issues"]) == 1
    assert result["security_issues"][0]["category"] == "security"


@patch("graph.analyze_style")
def test_style_analysis_node_success(mock_analyze_style):
    """El nodo de estilo guarda los hallazgos serializados en el estado."""
    mock_analyze_style.return_value = [
        Finding(
            id="STYLE-002",
            file_name="backend/service.py",
            line_number=20,
            category="style",
            severity="low",
            explanation="Nombre de variable poco expresivo.",
            bad_example="x = get_data()",
            refactor_suggestion="Usar un nombre que describa el contenido.",
            code_fix="user_data = get_data()",
        )
    ]

    result = style_analysis(_estado())

    mock_analyze_style.assert_called_once_with("some diff content")
    assert "status" not in result
    assert len(result["style_issues"]) == 1
    assert result["style_issues"][0]["category"] == "style"


def test_security_and_style_nodes_skip_previous_error():
    """Los nodos no ejecutan agentes si el estado ya contiene un error."""
    state = _estado()
    state["status"] = "error"
    state["error_message"] = "Error previo"

    assert security_analysis(state) == {}
    assert style_analysis(state) == {}