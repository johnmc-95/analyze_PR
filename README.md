# AI Code Review Agent

Herramienta web que analiza Pull Requests de GitHub mediante agentes de IA especializados y genera un informe visual con bugs, vulnerabilidades y problemas de estilo.

**Stack:** FastAPI · LangGraph · Groq (Llama 3.3 70B) · React + Vite · Tailwind CSS

---

## Levantar el proyecto completo

Necesitas dos terminales abiertas en paralelo.

### Terminal 1 — Backend

```bash
cd backend
python3 -m venv venv

# Mac/Linux
source venv/bin/activate
# Windows CMD: venv\Scripts\activate.bat
# Windows PowerShell: venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn main:app --reload
```

Verifica en `http://localhost:8000/health` → `{ "status": "Ok" }`

### Terminal 2 — Frontend

```bash
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173` en el navegador.

> Para instrucciones detalladas de cada capa ver `backend/README.md` y `frontend/README.md`.

---

## Ejecutar el demo

El script `demo.py` descarga el diff de un PR público y lo analiza con Groq. Sirve para verificar que las API keys funcionan correctamente.

### 1. Clonar el repositorio

```bash
git clone https://github.com/maykmbs/code-review-dataquantum.git
cd code-review-dataquantum
```

### 2. Crear el entorno virtual

**Mac / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (CMD)**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell)**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install httpx groq python-dotenv
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Abre `.env` y rellena tus keys:

| Variable | Dónde obtenerla |
|----------|----------------|
| `GROQ_API_KEY` | console.groq.com → API Keys |
| `GITHUB_TOKEN` | github.com/settings/tokens → Generate new token (classic) → marcar `public_repo` |
| `LANGSMITH_API_KEY` | smith.langchain.com → Settings → API Keys |

### 5. Ejecutar el demo

```bash
python demo.py
```

Deberías ver el diff descargado desde GitHub y el análisis generado por el modelo.

### 6. Ejecutar verificación del agente de bugs (LangGraph)

Además del script básico `demo.py`, puedes probar la ejecución paralela del grafo de LangGraph y del agente de detección de bugs corriendo:

```bash
# Probar el grafo completo de LangGraph con un PR real
python verify_bug_agent.py

# Probar la detección estructurada del agente con un diff que contiene bugs simulados
python verify_with_bug.py
```

---

## Documentación

| Documento | Descripción |
|-----------|-------------|
| `docs/E1_Documento_De_Especificacion_De_Requisitos.md` | Requisitos funcionales, no funcionales y casos de uso |
| `docs/E2_Arquitectura_Diseño.md` | Arquitectura del sistema y diseño de LangGraph |
| `docs/E3_Estado_del_Arte_e_Investigacion.md` | Benchmark, justificación del stack y cronograma |
| `docs/ROLES.md` | Roles y responsabilidades del equipo |
| `docs/PLAN_EJECUCION.md` | Plan de ejecución día a día |
