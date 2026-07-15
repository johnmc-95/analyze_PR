from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from tools.github_tools import get_pr_diff
from agents.bug_agent import analyze_bugs
from agents.security_agent import analyze_security
from agents.style_agent import analyze_style
from errors import ExternalServiceError, constraints_exceeded
from observability import log_external_error
from schemas import Finding, Metadata, ReviewResponse, Summary


# Límites del MVP definidos en los requisitos (RS-01 y RS-02).
LIMITE_ARCHIVOS = 5
LIMITE_LINEAS = 1000


def _conservar_primer_error(existente, nuevo):
    """
    Reducer para las claves de error del estado.

    Los nodos de análisis (bug/security/style) se ejecutan en paralelo. Si un
    servicio externo cae, los tres pueden fallar en el mismo superstep y escribir
    estas claves a la vez. Sin un reducer, LangGraph aborta con InvalidUpdateError.
    Nos quedamos con el primer error registrado (todos describen la misma causa).
    """
    return existente if existente is not None else nuevo


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
    # Claves de error (RF-08) con reducer para tolerar fallos simultáneos de los
    # nodos paralelos: mensaje seguro, código HTTP y código estable de error.
    error_message: Annotated[str | None, _conservar_primer_error]
    error_status: Annotated[int | None, _conservar_primer_error]
    error_code: Annotated[str | None, _conservar_primer_error]


def _registrar_error(err: Exception, *, pr_url: str, node: str) -> dict:
    """
    Traduce una excepción de un nodo a los campos de error del estado (RF-08).

    - Si es un ExternalServiceError, usa su código HTTP, su código estable y su
      mensaje seguro para el usuario.
    - Cualquier otra excepción se trata como error interno (500) con un mensaje
      genérico; el detalle real solo se registra en logging/LangSmith.

    No escribe 'status' para no colisionar entre los nodos paralelos; ese campo lo
    fija el nodo secuencial (download_diff) cuando corresponde. En ambos casos deja
    constancia del error en la trazabilidad.
    """
    if isinstance(err, ExternalServiceError):
        external = err
    else:
        external = ExternalServiceError(
            status_code=500,
            error_code="INTERNAL_ERROR",
            user_message=(
                "Ocurrió un error interno procesando la solicitud. "
                "Inténtalo de nuevo."
            ),
            technical_detail=f"{type(err).__name__}: {err}",
        )

    log_external_error(external, pr_url=pr_url, node=node)

    return {
        "error_message": external.user_message,
        "error_status": external.status_code,
        "error_code": external.error_code,
    }


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
        # download_diff es secuencial, así que aquí sí podemos fijar 'status'.
        return {
            "raw_diff": "",
            "status": "error",
            **_registrar_error(e, pr_url=state.get("pr_url", ""), node="download_diff"),
        }


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
        err = constraints_exceeded(
            user_message=(
                f"El Pull Request modifica {files_count} archivos y supera el "
                f"máximo de {LIMITE_ARCHIVOS} permitido (RS-01). Este límite existe "
                "porque el análisis con IA procesa el diff completo: con demasiados "
                "archivos se agota la ventana de contexto del modelo y se dispara el "
                "coste y el tiempo de respuesta. Divide el Pull Request en cambios "
                "más pequeños y vuelve a intentarlo."
            ),
            technical_detail=f"RS-01: {files_count} archivos > límite {LIMITE_ARCHIVOS}",
        )
        # Nodo secuencial: fijamos 'status' y registramos el error (logging/LangSmith).
        result["status"] = "error"
        result.update(
            _registrar_error(err, pr_url=state.get("pr_url", ""), node="validate_constraints")
        )
        return result

    # RS-02: máximo de líneas modificadas.
    if changed_lines > LIMITE_LINEAS:
        err = constraints_exceeded(
            user_message=(
                f"El Pull Request modifica {changed_lines} líneas y supera el "
                f"máximo de {LIMITE_LINEAS} permitido (RS-02). Este límite evita "
                "problemas de rendimiento y que el diff no quepa en la ventana de "
                "contexto del modelo. Divide el Pull Request en cambios más pequeños "
                "y vuelve a intentarlo."
            ),
            technical_detail=f"RS-02: {changed_lines} líneas > límite {LIMITE_LINEAS}",
        )
        result["status"] = "error"
        result.update(
            _registrar_error(err, pr_url=state.get("pr_url", ""), node="validate_constraints")
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
        # Capturamos cualquier error en la llamada o en la validación (RF-08).
        return {
            "bug_issues": [],
            **_registrar_error(e, pr_url=state.get("pr_url", ""), node="bug_analysis"),
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
        # Registrar cualquier error del agente dentro del estado del grafo (RF-08).
        return {
            "security_issues": [],
            **_registrar_error(
                e, pr_url=state.get("pr_url", ""), node="security_analysis"
            ),
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
        # Registrar cualquier error del agente dentro del estado del grafo (RF-08).
        return {
            "style_issues": [],
            **_registrar_error(e, pr_url=state.get("pr_url", ""), node="style_analysis"),
        }


def _normalizar_texto(value: str | None) -> str:
    """Normaliza texto para comparar hallazgos y detectar duplicados."""
    if not value:
        return ""
    return " ".join(value.lower().strip().split())


def _dedupe_findings(findings: list[dict]) -> list[dict]:
    """Elimina hallazgos duplicados conservando la primera aparición."""
    unique_findings = []
    seen_keys = set()

    for finding in findings:
        # Combinamos campos estables para detectar el mismo problema repetido.
        duplicate_key = (
            finding.get("file_name", "").lower().strip(),
            finding.get("line_number"),
            _normalizar_texto(finding.get("explanation")),
            _normalizar_texto(finding.get("bad_example")),
        )

        if duplicate_key in seen_keys:
            continue

        seen_keys.add(duplicate_key)
        unique_findings.append(finding)

    return unique_findings


def _build_global_comment(total_issues: int, findings: list[dict]) -> str:
    """Genera un resumen breve del resultado del análisis."""
    if total_issues == 0:
        return "¡Buen trabajo! El código analizado no presenta problemas relevantes."

    issues_by_category = {
        "bug": 0,
        "security": 0,
        "style": 0,
    }

    for finding in findings:
        category = finding.get("category")
        if category in issues_by_category:
            issues_by_category[category] += 1

    parts = []
    if issues_by_category["bug"]:
        parts.append(f"{issues_by_category['bug']} de bugs")
    if issues_by_category["security"]:
        parts.append(f"{issues_by_category['security']} de seguridad")
    if issues_by_category["style"]:
        parts.append(f"{issues_by_category['style']} de estilo")

    return f"Se detectaron {total_issues} hallazgos: " + ", ".join(parts) + "."


# Nodo final encargado de consolidar los resultados.
def consolidation(state: ReviewState) -> dict:
    """
    Unifica los hallazgos de los tres agentes, elimina duplicados,
    reasigna IDs únicos y construye el JSON final del contrato ReviewResponse.
    """
    # Unificar resultados de los tres agentes especializados.
    all_findings = (
        state.get("bug_issues", [])
        + state.get("security_issues", [])
        + state.get("style_issues", [])
    )

    # Eliminar duplicados entre agentes antes de generar IDs finales.
    unique_findings = _dedupe_findings(all_findings)

    final_findings = []
    for index, finding in enumerate(unique_findings, start=1):
        # Reasignar IDs secuenciales según el contrato final.
        normalized_finding = {
            **finding,
            "id": f"ISSUE-{index:03d}",
        }

        # Validar cada hallazgo contra el modelo Pydantic.
        final_findings.append(Finding(**normalized_finding).model_dump())

    total_issues = len(final_findings)
    status = "issues_found" if total_issues > 0 else "clean"

    # Construir respuesta final validada con Pydantic.
    final_report = ReviewResponse(
        summary=Summary(
            status=status,
            total_issues=total_issues,
            global_comment=_build_global_comment(total_issues, final_findings),
        ),
        findings=final_findings,
        metadata=Metadata(
            model="llama-3.3-70b-versatile",
            files_processed=state.get("files_count", 0),
            changed_lines=state.get("changed_lines", 0),
        ),
    ).model_dump()

    return {
        "final_report": final_report,
        "status": status,
    }


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
