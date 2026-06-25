🤖 Code Review Agent

> **Stack:** FastAPI + LangChain + LangGraph + Groq + GitHub API + Next.js
> 

> **Tiempo:** 3 semanas · 1-2h/día · en paralelo con DataQuantum
> 

> **Objetivo:** Un agente que analiza PRs de GitHub, detecta bugs y problemas de seguridad, y comenta directamente en el PR como GitHub Action.
> 

---

## 📊 Estado

🔜 En construcción

---

## 🚧 Fase 1 — MVP por CLI (Semana 1)

**Objetivo:** Un agente que analiza un PR de GitHub y devuelve un informe por terminal.

**Qué construyes:**

- Conectar GitHub API: obtener diff de un PR dado su URL
- Agente LangChain con tool `get_pr_diff(url)`
- El modelo analiza el diff y detecta bugs y problemas de seguridad
- Output: informe estructurado en JSON `{bugs[], security_issues[], severity}`
- Funciona por CLI: `python review.py https://github.com/user/repo/pull/123`

**Tecnologías:**

- LangChain: primer agente real con tool use
- GitHub API (PyGithub o requests)
- Groq: llama-3.3-70b-versatile
- Pydantic: validar el output estructurado

**✅ Checkpoint:** Le pasas la URL de un PR real y devuelve un informe con bugs y problemas de seguridad detectados.

---

## 🚧 Fase 2 — API + segundo agente (Semana 2)

**Objetivo:** Convertir el CLI en una API con FastAPI y añadir un agente especializado en convenciones de código.

**Qué construyes:**

- Backend FastAPI: `POST /review` recibe URL del PR y devuelve el informe
- Segundo agente especializado en convenciones de código (naming, estructura, duplicación)
- LangGraph: orquestar los 2 agentes en paralelo y combinar resultados
- Frontend mínimo en Next.js: pegar URL del PR y ver el informe
- Auth básica con API key

**Tecnologías:**

- LangGraph: primer grafo real con nodos paralelos
- FastAPI + Pydantic
- Next.js (mínimo, solo UI)

**✅ Checkpoint:** Pegas la URL de un PR en el frontend y ves un informe con bugs, seguridad y convenciones en menos de 30 segundos.

---

## 🚧 Fase 3 — GitHub Action (Semana 3)

**Objetivo:** El agente se ejecuta automáticamente en cada PR y comenta los resultados.

**Qué construyes:**

- GitHub Action: se dispara en cada `pull_request` event
- Llama a tu API de FastAPI con la URL del PR
- Publica el informe como comentario en el PR usando GitHub API
- LangSmith: conectar para ver trazas de cada análisis
- README profesional con demo GIF y arquitectura

**Tecnologías:**

- GitHub Actions (YAML workflow)
- LangSmith: observabilidad
- GitHub API: publicar comentarios

**✅ Checkpoint:** Abres un PR en tu repo, el agente lo analiza automáticamente y deja un comentario estructurado con los hallazgos en menos de 1 minuto.

---

## 📁 Estructura del proyecto

```
code-review-agent/
├── backend/
│   ├── main.py          # FastAPI
│   ├── agents/
│   │   ├── bug_agent.py
│   │   └── convention_agent.py
│   ├── tools/
│   │   └── github_tools.py
│   ├── graph.py         # LangGraph
│   └── schemas.py
├── frontend/
│   └── app/
└── .github/
    └── workflows/
        └── code-review.yml
```

---

## 📚 Recursos

- LangChain Docs: Tools
- LangGraph Docs
- PyGithub Docs
- GitHub Actions Docs
- LangSmith Docs
- AI Agents in LangGraph — DeepLearning.AI

---

## 📝 Notas y decisiones técnicas

- Usar Groq (llama-3.3-70b-versatile) por velocidad y coste cero
- Output siempre en JSON validado por Pydantic — nunca texto libre
- Fase 1 primero: no construir infraestructura hasta que el agente funcione
- El GitHub Action llama a la API deployada en Render — no ejecuta código local