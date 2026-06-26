# Roles del Equipo — AI Code Review Agent

**Equipo:** 7 integrantes
**Proyecto:** AI Code Review Agent (Web MVP)

---

## P1 — Tech Lead / Full-stack

- Toma decisiones técnicas cuando hay dudas del equipo
- Hace code review de los PRs antes de mergear a `develop`
- Lidera las sesiones grupales cuando hay área nueva (ej. primera vez con LangGraph)
- Conecta las piezas cuando algo no encaja entre frontend y backend
- Lidera la redacción del E4 al final
- Es el único que toca todas las capas del sistema

---

## P2 — Frontend Lead

- Construye todos los componentes visuales en React + Tailwind
- Formulario de URL, botón de analizar, dark mode
- Tarjetas de resultados (severidad: crítica / alta / media / baja)
- Pantalla de "código limpio" (RF-06)
- Diseña la estructura de carpetas del frontend
- No necesita saber IA, solo React y Tailwind

---

## P3 — Frontend Support

- Trabaja junto a P2 pero enfocado en la conexión con el backend
- Hace las llamadas HTTP (`fetch` / `axios`) al endpoint del backend
- Maneja los estados: cargando, error, éxito
- Implementa los mensajes de error amigables para el usuario (RF-08)
- Prueba el frontend con respuestas reales
- No necesita saber IA, solo React y cómo consumir APIs

---

## P4 — Backend Lead

- Crea y mantiene FastAPI con todos sus endpoints
- Define los modelos Pydantic (contrato JSON del E2 §4)
- Valida la URL del PR antes de enviarlo al agente
- Maneja los errores de GitHub y Groq y los convierte en respuestas HTTP claras
- Conecta FastAPI con LangGraph (llama al grafo)
- Necesita Python, no necesita saber de IA en profundidad

---

## P5 — AI Lead

- Diseña y construye el grafo LangGraph completo
- Define el `StateSchema` (estado compartido entre agentes)
- Implementa el `consolidation_node` (dedup, severidad, JSON final)
- Optimiza los prompts usando LangSmith para reducir falsos positivos
- Es el rol con más curva de aprendizaje — LangGraph requiere entenderlo bien
- Trabaja muy de la mano con P6

---

## P6 — AI Support / GitHub Integration

- Implementa la herramienta GitHub (`get_pr_diff`) que descarga el diff
- Implementa los 3 agentes especializados: bugs, seguridad, estilo
- Escribe los prompts de cada agente en español
- Conecta los agentes al grafo que construye P5
- Prueba los agentes con PRs reales que tengan vulnerabilidades o bugs
- Trabaja muy de la mano con P5

---

## P7 — DevOps / QA

- Configura el repositorio: GitFlow, ramas protegidas, `.gitignore`
- Crea scripts de instalación para que todos puedan levantar el proyecto localmente
- Configura LangSmith para monitorear los agentes
- Gestiona las variables de entorno (`GROQ_API_KEY`, `GITHUB_TOKEN`, `LANGSMITH_KEY`)
- Configura GitHub Actions (CI: tests automáticos en cada PR)
- Despliega backend y frontend (Render, Railway u otro)
- Escribe los tests con `pytest`
- No necesita saber IA, necesita saber de Git, CI/CD y un poco de Python para tests

---

## Resumen

| Rol | Necesita saber | Dificultad |
|-----|---------------|------------|
| P1 — Tech Lead | Todo un poco | Alta |
| P2 — Frontend Lead | React + Tailwind | Media |
| P3 — Frontend Support | React + fetch/axios | Media-baja |
| P4 — Backend Lead | Python + FastAPI | Media |
| P5 — AI Lead | Python + LangGraph | Alta |
| P6 — AI Support | Python + prompts + GitHub API | Media-alta |
| P7 — DevOps / QA | Git + CI/CD + pytest | Media |
