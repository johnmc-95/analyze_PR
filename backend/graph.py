from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from tools.github_tools import get_pr_diff
from agents.bug_agent import analyze_bugs
from agents.security_agent import analyze_security
from agents.style_agent import analyze_style


# Límites del MVP definidos en los requisitos (RS-01 y RS-02).
LIMITE_ARCHIVOS = 5
LIMITE_LINEAS = 1000


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


# Cuenta archivos y líneas modificadas a partir del diff unificado de GitHub.
def _contar_cambios(raw_diff: str) -> tuple[int, int]:
    """
    Recorre el diff en formato unified y devuelve (archivos, líneas_modificadas).

    - Cada archivo del diff empieza por una cabecera 'diff --git ...'.
    - Las líneas modificadas son las añadidas ('+') más las borradas ('-'),
      excluyendo las cabeceras de fichero ('+++' y '---').
    """
    files_count = 0
    changed_lines = 0

    for line in raw_diff.splitlines():
        if line.startswith("diff --git "):
            files_count += 1
        elif line.startswith("+") and not line.startswith("+++"):
            changed_lines += 1
        elif line.startswith("-") and not line.startswith("---"):
            changed_lines += 1

    return files_count, changed_lines


# Nodo encargado de validar límites del MVP (RS-01 y RS-02).
def validate_constraints(state: ReviewState) -> dict:
    """
    Cuenta los archivos y las líneas modificadas del diff descargado y detiene
    el flujo con un mensaje de error si se superan los límites del MVP.

    Guarda siempre 'files_count' y 'changed_lines' en el estado para que la
    metadata y la consolidación posteriores puedan reutilizarlos.
    """
    # Si un nodo anterior ya registró un error (p.ej. fallo al descargar el diff),
    # no tiene sentido seguir validando.
    if state.get("error_message"):
        return {}

    raw_diff = state.get("raw_diff", "")
    files_count, changed_lines = _contar_cambios(raw_diff)

    # Métricas que se guardan pase lo que pase.
    result: dict = {
        "files_count": files_count,
        "changed_lines": changed_lines,
    }

    # RS-01: máximo de archivos modificados.
    if files_count > LIMITE_ARCHIVOS:
        result["status"] = "error"
        result["error_message"] = (
            f"El Pull Request modifica {files_count} archivos y supera el "
            f"máximo de {LIMITE_ARCHIVOS} permitido (RS-01). Este límite existe "
            "porque el análisis con IA procesa el diff completo: con demasiados "
            "archivos se agota la ventana de contexto del modelo y se dispara el "
            "coste y el tiempo de respuesta. Divide el Pull Request en cambios "
            "más pequeños y vuelve a intentarlo."
        )
        return result

    # RS-02: máximo de líneas modificadas.
    if changed_lines > LIMITE_LINEAS:
        result["status"] = "error"
        result["error_message"] = (
            f"El Pull Request modifica {changed_lines} líneas y supera el "
            f"máximo de {LIMITE_LINEAS} permitido (RS-02). Este límite evita "
            "problemas de rendimiento y que el diff no quepa en la ventana de "
            "contexto del modelo. Divide el Pull Request en cambios más pequeños "
            "y vuelve a intentarlo."
        )
        return result

    # Dentro de los límites: el flujo puede continuar hacia los agentes.
    result["status"] = "constraints_validated"
    return result


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
        return {"bug_issues": []}
    
    try:
        # Ejecutar el análisis con el agente de bugs conectado a Groq
        findings = analyze_bugs(raw_diff)
        # Guardamos los findings serializados a diccionarios en bug_issues
        bug_issues_dicts = [finding.model_dump() for finding in findings]
        return {"bug_issues": bug_issues_dicts}
    except Exception as e:
        # Capturamos cualquier error en la llamada o en la validación
        return {
            "bug_issues": [],
            "error_message": f"Error en bug_analysis node: {str(e)}"
        }


# Nodo reservado para el análisis de seguridad.
def security_analysis(state: ReviewState) -> dict:
    """
    Ejecuta el agente de seguridad sobre el diff del PR y guarda los hallazgos
    serializados en la clave 'security_issues' del estado.
    """
    # Si ya hay un error previo registrado en el estado, evitamos ejecutar el análisis.
    if state.get("error_message"):
        return {}

    raw_diff = state.get("raw_diff", "")
    if not raw_diff or not raw_diff.strip():
        return {"security_issues": []}

    try:
        # Ejecutar el análisis con el agente de seguridad conectado a Groq.
        findings = analyze_security(raw_diff)

        # Guardar los findings como diccionarios para que viajen bien por el grafo.
        security_issues_dicts = [finding.model_dump() for finding in findings]

        return {"security_issues": security_issues_dicts}
    except Exception as e:
        # Registrar cualquier error del agente dentro del estado del grafo.
        return {
            "security_issues": [],
            "error_message": f"Error en security_analysis node: {str(e)}",
        }


# Nodo reservado para el análisis de estilo y mantenibilidad.
def style_analysis(state: ReviewState) -> dict:
    """
    Ejecuta el agente de estilo sobre el diff del PR y guarda los hallazgos
    serializados en la clave 'style_issues' del estado.
    """
    # Si ya hay un error previo registrado en el estado, evitamos ejecutar el análisis.
    if state.get("error_message"):
        return {}

    raw_diff = state.get("raw_diff", "")
    if not raw_diff or not raw_diff.strip():
        return {"style_issues": []}

    try:
        # Ejecutar el análisis con el agente de estilo conectado a Groq.
        findings = analyze_style(raw_diff)

        # Guardar los findings como diccionarios para que viajen bien por el grafo.
        style_issues_dicts = [finding.model_dump() for finding in findings]

        return {"style_issues": style_issues_dicts}
    except Exception as e:
        # Registrar cualquier error del agente dentro del estado del grafo.
        return {
            "style_issues": [],
            "error_message": f"Error en style_analysis node: {str(e)}",
        }

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