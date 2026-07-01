# Backend — AI Code Review Agent

API REST construida con FastAPI que orquesta el análisis de Pull Requests mediante agentes de IA.

---

## Requisitos

- Python 3.11 o superior
- Las API keys configuradas en `.env`

---

## Instalación

### 1. Crear entorno virtual

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

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp ../.env.example ../.env
```

Abre `.env` en la raíz del proyecto y rellena tus keys:

```env
GROQ_API_KEY=tu_key_aqui
GITHUB_TOKEN=tu_token_aqui
LANGSMITH_API_KEY=tu_key_aqui
LANGSMITH_PROJECT=code-review-agent
```

---

## Levantar el servidor

```bash
uvicorn main:app --reload
```

El servidor quedará disponible en `http://localhost:8000`.

---

## Verificar que funciona

```bash
curl http://localhost:8000/health
```

Respuesta esperada:

```json
{ "status": "Ok" }
```

También puedes ver la documentación interactiva en `http://localhost:8000/docs`.

---

## Grafo de revisión con LangGraph

El archivo `graph.py` define el flujo que orquesta los agentes de análisis del Pull Request.

### Estado compartido

`ReviewState` es el estado común que viaja entre todos los nodos del grafo. Incluye la URL del PR, el diff descargado, métricas del cambio, resultados parciales de cada agente y el informe final.

### Flujo actual

```text
START
  -> download_diff
  -> validate_constraints
  -> bug_analysis / security_analysis / style_analysis
  -> consolidation
  -> END
```

Los nodos existen y devuelven el estado sin modificar. Esto permite tener la estructura del grafo compilada mientras se implementa la lógica real de cada agente en próximas tareas.

### Verificar compilación

Desde la raíz del proyecto, con el entorno virtual activado:

```bash
python -c "from backend.graph import review_graph; print('Grafo compilado correctamente')"
```

Si aparece el mensaje, LangGraph está instalado y el grafo se ha construido sin errores.
