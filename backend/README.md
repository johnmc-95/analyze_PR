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

Los tres nodos de análisis (`bug_analysis`, `security_analysis`, `style_analysis`) están operativos y conectados a la API de Groq (`llama-3.3-70b-versatile`). Se ejecutan en paralelo y sus resultados se unen en `consolidation`.

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

## Manejo de errores de servicios externos (RF-08)

Todos los errores de **GitHub** y **Groq** se traducen a una respuesta HTTP con el código adecuado y un mensaje claro para el usuario, **sin exponer detalles técnicos internos**. Además, cada error queda registrado para trazabilidad.

### Archivos implicados

- **`errors.py`** — define la excepción `ExternalServiceError` (con `status_code`, `error_code`, `user_message` y `technical_detail`) y las fábricas por caso. **Aquí viven todos los mensajes seguros de usuario**, centralizados en un solo sitio.
- **`observability.py`** — `log_external_error(...)` registra el error **siempre** en el logging estándar y, si hay `LANGSMITH_API_KEY`, además lo envía a **LangSmith**. Sin key funciona igual (no rompe dev ni tests).
- **`agents/groq_runner.py`** — helper compartido `run_groq_analysis(...)` que ejecuta la llamada a Groq para los 3 agentes (elimina la duplicación) y traduce los errores de Groq a `ExternalServiceError`.
- **`tools/github_tools.py`** — traduce los errores de la API de GitHub (404, 403, 429, timeout, conexión).
- **`graph.py`** — los nodos capturan las excepciones y guardan los metadatos de error en el estado (`error_message`, `error_status`, `error_code`) mediante `_registrar_error(...)`. Las claves de error usan un *reducer* para tolerar que los 3 nodos paralelos fallen a la vez.
- **`main.py`** — devuelve `HTTPException(status_code=error_status, detail=error_message)`; el `detail` es siempre el mensaje seguro.

### Taxonomía de errores

| Origen | Situación | HTTP | `error_code` |
|--------|-----------|------|--------------|
| GitHub | PR inexistente | 404 | `PR_NOT_FOUND` |
| GitHub | Repo privado / sin permisos | 403 | `REPO_FORBIDDEN` |
| GitHub | Rate limit (429 o 403 con cuota agotada) | 429 | `GITHUB_RATE_LIMIT` |
| GitHub | Timeout | 504 | `GITHUB_TIMEOUT` |
| GitHub | Conexión / otro error | 502 | `GITHUB_UNAVAILABLE` |
| Groq | Timeout | 504 | `GROQ_TIMEOUT` |
| Groq | Fallo de inferencia | 502 | `GROQ_INFERENCE_ERROR` |
| Groq | Respuesta inválida (no parseable) | 502 | `GROQ_INVALID_RESPONSE` |
| Límites RS-01 / RS-02 | PR demasiado grande | 422 | `CONSTRAINTS_EXCEEDED` |
| Inesperado | Error interno no controlado | 500 | `INTERNAL_ERROR` |

> El `technical_detail` (excepción real, cuerpo de la respuesta, etc.) **solo** va a logging/LangSmith, **nunca** al `detail` HTTP que ve el usuario.

### API keys (sin cambios)

Las claves siguen saliendo del `.env` local de cada persona (`GROQ_API_KEY`, `GITHUB_TOKEN`, `LANGSMITH_API_KEY`). La única diferencia es que la key de Groq ahora se lee una sola vez en `agents/groq_runner.py` en lugar de repetirse en cada agente. `LANGSMITH_API_KEY` es **opcional**: sin ella, los errores se registran solo por logging.

### En el frontend

El backend envía en `detail` un mensaje claro; `analisisService.js` lo lanza como `Error`, `App.jsx` lo guarda y `EstadoError.jsx` lo muestra al usuario (con un fallback genérico si no hubiera mensaje).

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