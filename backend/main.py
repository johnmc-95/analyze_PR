from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from graph import review_graph
from schemas import Finding, Metadata, ReviewRequest, ReviewResponse, Summary

# Inicializar FastAPI
app = FastAPI()

# Permite peticiones desde el frontend en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint para comprobar que la API funciona correctamente
@app.get("/health")
async def health():
    return {"status": "Ok"}

# Recibe la URL del Pull Request, ejecuta el grafo LangGraph y devuelve los hallazgos.
@app.post("/review/initiate", response_model=ReviewResponse)
async def initiate_review(request: ReviewRequest) -> ReviewResponse:
    # Estado inicial que recorre todos los nodos del grafo.
    initial_state = {
        "pr_url": str(request.pr_url),
        "raw_diff": "",
        "files_count": 0,
        "changed_lines": 0,
        "bug_issues": [],
        "security_issues": [],
        "style_issues": [],
        "final_report": {},
        "status": "init",
        "error_message": None,
        "error_status": None,
        "error_code": None,
    }

    result = review_graph.invoke(initial_state)

    # Si algún nodo registró un error (descarga, límites, GitHub, Groq...), lo
    # propagamos con el código HTTP adecuado (RF-08). El detail es siempre el
    # mensaje seguro para el usuario; nunca detalles técnicos internos.
    if result.get("error_message"):
        raise HTTPException(
            status_code=result.get("error_status") or 500,
            detail=result["error_message"],
        )

    # Consolidar los hallazgos de los tres agentes en una sola lista.
    all_findings = (
        result.get("bug_issues", [])
        + result.get("security_issues", [])
        + result.get("style_issues", [])
    )

    findings = [Finding(**f) for f in all_findings]
    total = len(findings)

    return ReviewResponse(
        summary=Summary(
            status="issues_found" if total > 0 else "clean",
            total_issues=total,
            global_comment=(
                f"Se encontraron {total} hallazgos en el Pull Request."
                if total > 0
                else "No se encontraron problemas en el Pull Request."
            ),
        ),
        findings=findings,
        metadata=Metadata(
            model="llama-3.3-70b-versatile",
            files_processed=result.get("files_count", 0),
            changed_lines=result.get("changed_lines", 0),
        ),
    )
