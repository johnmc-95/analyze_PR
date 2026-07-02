from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from tools.github_tools import get_pr_diff
from agents.bug_agent import analyze_bugs


# Estado compartido entre todos los nodos del grafo.
class ReviewState(TypedDict):
    pr_url: str
    raw_diff: str
    files_count: int
    changed_lines: int
    bug_issues: list
    security_issues: list
    style_issues: list
    final_report: dict
    status: str
    error_message: str | None


# Nodo encargado de descargar el diff del Pull Request.
def download_diff(state: ReviewState) -> dict:
    """
    Descarga el diff del PR indicado en el estado y lo guarda en raw_diff.
    Si ocurre cualquier error lo registra en error_message y marca el estado como fallido.
    """
    try:
        diff = get_pr_diff(state["pr_url"])
        return {"raw_diff": diff, "status": "diff_downloaded"}
    except Exception as e:
        return {"raw_diff": "", "status": "error", "error_message": str(e)}


# Nodo encargado de validar límites del MVP.
def validate_constraints(state: ReviewState) -> dict:
    return {}


# Nodo reservado para el análisis de bugs.
def bug_analysis(state: ReviewState) -> dict:
    """
    Nodo del grafo de revisión de código que se encarga de analizar el diff del PR
    en busca de bugs, errores lógicos y problemas de rendimiento.
    
    Llama al agente especializado 'analyze_bugs' y guarda la lista de hallazgos serializados (como diccionarios)
    en la clave 'bug_issues' del estado. En caso de error, actualiza 'error_message' y el 'status'.
    """
    # Si ya hay un error previo registrado en el estado, evitamos ejecutar el análisis
    if state.get("error_message"):
        return {}

    raw_diff = state.get("raw_diff", "")
    if not raw_diff or not raw_diff.strip():
        return {"bug_issues": [], "status": "bug_analysis_skipped"}
    
    try:
        # Ejecutar el análisis con el agente de bugs conectado a Groq
        findings = analyze_bugs(raw_diff)
        # Guardamos los findings serializados a diccionarios en bug_issues
        bug_issues_dicts = [finding.model_dump() for finding in findings]
        return {
            "bug_issues": bug_issues_dicts,
            "status": "bug_analysis_completed"
        }
    except Exception as e:
        # Capturamos cualquier error en la llamada o en la validación
        return {
            "bug_issues": [],
            "status": "error",
            "error_message": f"Error en bug_analysis node: {str(e)}"
        }


# Nodo reservado para el análisis de seguridad.
def security_analysis(state: ReviewState) -> dict:
    return {}


# Nodo reservado para el análisis de estilo y mantenibilidad.
def style_analysis(state: ReviewState) -> dict:
    return {}


# Nodo final encargado de consolidar los resultados.
def consolidation(state: ReviewState) -> dict:
    return {}


# Construye y compila el grafo de revisión.
def build_review_graph():
    graph = StateGraph(ReviewState)

    # Registro de nodos del flujo.
    graph.add_node("download_diff", download_diff)
    graph.add_node("validate_constraints", validate_constraints)
    graph.add_node("bug_analysis", bug_analysis)
    graph.add_node("security_analysis", security_analysis)
    graph.add_node("style_analysis", style_analysis)
    graph.add_node("consolidation", consolidation)

    # Flujo inicial secuencial.
    graph.add_edge(START, "download_diff")
    graph.add_edge("download_diff", "validate_constraints")

    # Ramas de análisis especializado.
    graph.add_edge("validate_constraints", "bug_analysis")
    graph.add_edge("validate_constraints", "security_analysis")
    graph.add_edge("validate_constraints", "style_analysis")

    # Unión de resultados antes del cierre.
    graph.add_edge("bug_analysis", "consolidation")
    graph.add_edge("security_analysis", "consolidation")
    graph.add_edge("style_analysis", "consolidation")

    # Fin del flujo.
    graph.add_edge("consolidation", END)

    return graph.compile()


# Grafo compilado y listo para ser importado por la API.
review_graph = build_review_graph()