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

El nodo `bug_analysis` está completamente operativo y conectado a la API de Groq (`llama-3.3-70b-versatile`). Los nodos `security_analysis` y `style_analysis` actualmente existen como stubs (devuelven diccionarios vacíos `{}`) listos para ser implementados en las siguientes tareas.

### Verificar compilación

Desde la raíz del proyecto, con el entorno virtual activado:

```bash
python -c "from backend.graph import review_graph; print('Grafo compilado correctamente')"
```

Si aparece el mensaje, LangGraph está instalado y el grafo se ha construido sin errores.

### Herramientas del grafo

La carpeta `tools/` contiene las funciones que usan los nodos internamente.

- `tools/github_tools.py` — descarga el diff de un PR desde la API de GitHub. Lo usa el nodo `download_diff`.

---

## Pruebas y Verificación del Agente de Bugs

### 1. Ejecutar las pruebas unitarias
Para comprobar que los validadores de Pydantic, la lógica de parseo del agente de bugs y los nodos del grafo responden correctamente (usando respuestas mockeadas de Groq):

```bash
# Desde la raíz del proyecto, con el entorno virtual activado:
pytest
```

### 2. Scripts de Validación Rápida (En la raíz del proyecto)
Para validar de extremo a extremo con llamadas reales a la API de Groq, disponemos de dos scripts de verificación en la raíz:

* **`verify_bug_agent.py`**: 
  Descarga el diff real del Pull Request utilizado en `demo.py` (el cual está limpio) y ejecuta todo el grafo de LangGraph de principio a fin. Sirve para validar que el flujo de los nodos en paralelo funcione perfectamente sin errores de concurrencia y que el agente de bugs retorne `0 hallazgos` ante código limpio.
  
* **`verify_with_bug.py`**:
  Ejecuta el agente con un diff simulado que contiene tres errores explícitos (división por cero potencial, variable indefinida e ineficiencia de rendimiento). Sirve para comprobar que el agente de Groq responda con la severidad, explicación y propuesta de refactorización correspondiente en formato estructurado JSON.