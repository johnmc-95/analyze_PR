from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from graph import review_graph
from schemas import ReviewRequest, ReviewResponse

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
    }

    result = review_graph.invoke(initial_state)

    # Si algún nodo registró un error (descarga, validación de límites, etc.), lo propagamos.
    if result.get("error_message"):
        raise HTTPException(status_code=422, detail=result["error_message"])

    # El nodo consolidation es responsable de deduplicar, reasignar IDs y generar el contrato final.
    final_report = result.get("final_report")
    if not final_report:
        raise HTTPException(
            status_code=500,
            detail="El grafo no generó un reporte final.",
        )

    return ReviewResponse(**final_report)
