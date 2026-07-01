from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas import Metadata, ReviewRequest, ReviewResponse, Summary

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


# Recibe la URL del Pull Request y devuelve una respuesta temporal.
# Cuando LangGraph este listo, el resultado real sustituira esta respuesta mock.
@app.post("/review/initiate", response_model=ReviewResponse)
async def initiate_review(request: ReviewRequest) -> ReviewResponse:
    return ReviewResponse(
        summary=Summary(
            status="clean",
            total_issues=0,
            global_comment=(
                f"La URL del PR {request.pr_url} es valida. "
                "El analisis con LangGraph aun no esta disponible."
            ),
        ),
        findings=[],
        metadata=Metadata(
            model="mock",
            files_processed=0,
            changed_lines=0,
        ),
    )
