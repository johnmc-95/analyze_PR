from typing import TypedDict

from langgraph.graph import END, START, StateGraph


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
def download_diff(state: ReviewState) -> ReviewState:
    return state


# Nodo encargado de validar límites del MVP.
def validate_constraints(state: ReviewState) -> ReviewState:
    return state


# Nodo reservado para el análisis de bugs.
def bug_analysis(state: ReviewState) -> ReviewState:
    return state


# Nodo reservado para el análisis de seguridad.
def security_analysis(state: ReviewState) -> ReviewState:
    return state


# Nodo reservado para el análisis de estilo y mantenibilidad.
def style_analysis(state: ReviewState) -> ReviewState:
    return state


# Nodo final encargado de consolidar los resultados.
def consolidation(state: ReviewState) -> ReviewState:
    return state


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