from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
