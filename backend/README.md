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
