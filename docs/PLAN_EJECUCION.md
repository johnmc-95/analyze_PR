# 📋 Plan de Ejecución — AI Code Review Agent

**Proyecto:** AI Code Review Agent (Web MVP)
**Inicio:** 26 de junio de 2026
**Entrega:** 16 de julio de 2026
**Duración:** 3 semanas (15 días hábiles)
**Equipo:** 7 integrantes

---

## Equipo y Roles

| Código | Rol | Integrante |
|--------|-----|-----------|
| P1 | Tech Lead / Full-stack | Miguel |
| P2 | Frontend Lead | — |
| P3 | Frontend Support | — |
| P4 | Backend Lead | — |
| P5 | AI Lead | — |
| P6 | AI Support / GitHub Integration | — |
| P7 | DevOps / QA | — |

> Ver `docs/ROLES.md` para descripción detallada de cada rol.

---

## Calendario

| Semana | Días hábiles | Fechas |
|--------|-------------|--------|
| Semana 1 | Días 1–5 | 26 jun – 2 jul |
| Semana 2 | Días 6–10 | 3 jul – 9 jul |
| Semana 3 | Días 11–15 | 10 jul – 16 jul |

| Día | Fecha | Evento |
|-----|-------|--------|
| Día 1 | Jue 26 jun | Inicio del proyecto |
| Día 2 | Vie 27 jun | |
| Día 3 | Lun 30 jun | |
| Día 4 | Mar 1 jul | |
| Día 5 | Mié 2 jul | ✅ Checkpoint Semana 1 |
| Día 6 | Jue 3 jul | |
| Día 7 | Vie 4 jul | |
| Día 8 | Lun 7 jul | |
| Día 9 | Mar 8 jul | |
| Día 10 | Mié 9 jul | ✅ Checkpoint Semana 2 |
| Día 11 | Jue 10 jul | |
| Día 12 | Vie 11 jul | |
| Día 13 | Lun 14 jul | 🔒 Code Freeze |
| Día 14 | Mar 15 jul | |
| Día 15 | Mié 16 jul | 🚀 Entrega Final |

---

# Semana 1 — Base del Sistema

**Objetivo:** El backend recibe una URL, descarga el diff de GitHub y devuelve un JSON básico desde el primer agente IA.

---

## Días 1–2 — Todo el equipo (26–27 jun)

> Sesión grupal obligatoria. Base conceptual del proyecto.

| Integrante | Tarea |
|-----------|-------|
| P1 | Liderar redacción E1, E2 y E3 · Tomar decisiones de arquitectura final |
| P2 | Participar en redacción E1/E2/E3 |
| P3 | Participar en redacción E1/E2/E3 |
| P4 | Participar en redacción E1/E2/E3 |
| P5 | Participar en redacción E1/E2/E3 |
| P6 | Participar en redacción E1/E2/E3 |
| P7 | Configurar repositorio · GitFlow · Protección de ramas · Plantilla `.env` |

Entregables:
- E1, E2 y E3 finalizados
- Repositorio configurado con ramas `main` y `develop`

---

## Día 3 — Configuración inicial (30 jun)

> Sesión grupal al inicio: revisión de estructura de carpetas y acuerdos de naming.

| Integrante | Tarea |
|-----------|-------|
| P1 | Validar estructura de carpetas · Resolver dudas de setup |
| P2 | Inicializar proyecto React + Vite · Configurar Tailwind CSS · Definir estructura de carpetas frontend |
| P3 | Crear primeras pantallas con Tailwind (wireframe en código) |
| P4 | Inicializar FastAPI · Crear modelos Pydantic base · Endpoint vacío `POST /review/initiate` |
| P5 | Diseñar `StateSchema` de LangGraph · Crear primer nodo vacío del grafo |
| P6 | Conectar con GitHub API · Obtener diff de un PR de prueba con `get_pr_diff(url)` |
| P7 | Configurar LangSmith · Crear `requirements.txt` · Preparar `docker-compose` o script de instalación local |

---

## Día 4 — Funcionalidad base (1 jul)

| Integrante | Tarea |
|-----------|-------|
| P1 | Code review de los PRs del Día 3 · Pair programming donde haya bloqueos |
| P2 | Desarrollar formulario principal: campo de URL + botón "Analizar" |
| P3 | Implementar spinner de carga · Pantalla de estado inicial |
| P4 | Validación de URL de GitHub en FastAPI · Respuesta de errores básicos |
| P5 | Primer agente de bugs con prompt básico conectado a Groq |
| P6 | Implementar `get_pr_diff(url)` como Tool de LangGraph |
| P7 | Configurar GitHub Actions inicial (lint + health check) |

---

## Día 5 — Primera integración vertical (2 jul)

> Sesión grupal al cierre: validar que el flujo extremo a extremo funciona.

| Integrante | Tarea |
|-----------|-------|
| P1 | Coordinar la integración vertical del día · Resolver bloqueos entre capas |
| P2 | Conectar formulario al endpoint del backend (primer fetch real) |
| P3 | Manejo visual de errores básico (URL inválida, PR no encontrado) |
| P4 | Conectar FastAPI → LangGraph (llamar al grafo desde el endpoint) |
| P5 | LangGraph ejecuta el agente de bugs y devuelve JSON estructurado |
| P6 | Validación de restricciones: máx. 5 archivos y 1000 líneas (nodo `validate_constraints`) |
| P7 | Script de prueba local del flujo completo |

---

## ✅ Checkpoint Semana 1 — 2 de julio

El sistema debe cumplir:

- [ ] `POST /review/initiate` recibe una URL de PR válida
- [ ] Se descarga el diff desde GitHub API
- [ ] El primer agente (bugs) analiza el diff con Groq
- [ ] Se devuelve un JSON estructurado al frontend
- [ ] E1, E2 y E3 finalizados y mergeados en `develop`

---

# Semana 2 — Orquestación IA Completa + Conexión Web

**Objetivo:** Los 3 agentes paralelos funcionando, frontend mostrando resultados reales con tarjetas visuales.

---

## Día 6 — Agentes completos + UI de resultados (3 jul)

> Sesión grupal al inicio: revisar el contrato JSON del E2 §4 y alinear modelos Pydantic.

| Integrante | Tarea |
|-----------|-------|
| P1 | Revisar contrato JSON (E2 §4) · Ajustar modelos Pydantic si hay inconsistencias |
| P2 | Desarrollar tarjetas visuales por severidad (Crítica / Alta / Media / Baja) |
| P3 | Desarrollar vista de "código limpio" (RF-06) |
| P4 | Adaptar endpoint para recibir y devolver la respuesta consolidada completa |
| P5 | Configurar ejecución paralela en LangGraph (fan-out hacia los 3 agentes) |
| P6 | Implementar agente de seguridad + agente de estilo con prompts en español |
| P7 | Configurar CI/CD en Render o Railway · Primer deploy preview del backend |

---

## Día 7 — Manejo de errores + ejecución paralela (4 jul)

| Integrante | Tarea |
|-----------|-------|
| P1 | Pair programming P5 + P6 para el `consolidation_node` |
| P2 | Integrar fetch/axios en el frontend para llamar al endpoint real |
| P3 | Pantalla de error global con mensajes amigables (RF-08) |
| P4 | Manejo de errores externos: GitHub rate limit, PR inexistente, timeout Groq |
| P5 | Implementar fan-in: recoger resultados de los 3 agentes en el grafo |
| P6 | Pruebas de ejecución paralela de los 3 agentes con PR reales |
| P7 | Gestionar variables de entorno seguras en el deploy (`GROQ_API_KEY`, `GITHUB_TOKEN`, `LANGSMITH_KEY`) |

---

## Día 8 — Consolidación + renderizado dinámico (7 jul)

| Integrante | Tarea |
|-----------|-------|
| P1 | Validar el JSON final completo contra el contrato Pydantic |
| P2 | Renderizado dinámico de findings desde el JSON real |
| P3 | Pulido UX: transiciones, feedback visual, estados de carga |
| P4 | Optimización async del endpoint · CORS correctos |
| P5 | Implementar `consolidation_node`: dedup + clasificación de severidad + JSON final |
| P6 | Refinamiento de prompts con datos de LangSmith (reducir falsos positivos) |
| P7 | Tests E2E completos del flujo principal |

---

## Días 9–10 — Ajustes y estabilización (8–9 jul)

> Todo el equipo trabaja sobre incidencias detectadas.

| Integrante | Tarea |
|-----------|-------|
| P1 | Coordinación general · Decisiones de UX final |
| P2 | Ajustes Dark Mode · Polish visual general |
| P3 | Verificar comportamiento en resoluciones ≥ 1024px |
| P4 | Reducción tamaño del JSON · Headers HTTP correctos |
| P5 | Ajuste de prompts con métricas reales de LangSmith |
| P6 | Pruebas con código vulnerable y con código limpio |
| P7 | Monitoreo en LangSmith: latencias, errores, trazas de agentes |

---

## ✅ Checkpoint Semana 2 — 9 de julio

El sistema debe cumplir:

- [ ] Flujo completo operativo de extremo a extremo
- [ ] 3 agentes ejecutándose en paralelo (bugs, seguridad, estilo)
- [ ] Frontend muestra tarjetas visuales con resultados reales
- [ ] Frontend muestra pantalla de "código limpio" cuando no hay hallazgos
- [ ] Manejo de todos los errores externos (RF-08)
- [ ] Tiempo de respuesta < 20 segundos (RNF-01)
- [ ] Deploy preview funcionando

---

# Semana 3 — Testing, Estabilización y Entrega

**Objetivo:** MVP estable, testeado, documentado y desplegado en producción.

---

## Día 11 — Testing (10 jul)

| Integrante | Tarea |
|-----------|-------|
| P1 | Liderar sesión de bug fixing colectivo |
| P2 | Tests visuales de componentes |
| P3 | Pruebas de todos los flujos alternativos (CU-02, CU-03) |
| P4 | Tests unitarios FastAPI con pytest |
| P5 | Tests de cada agente individualmente |
| P6 | Tests de integración de la herramienta GitHub |
| P7 | Configurar GitHub Actions: tests automáticos en cada PR |

---

## Día 12 — Pruebas funcionales finales (11 jul)

> Todo el equipo prueba con PRs reales.

| Integrante | Tarea |
|-----------|-------|
| P1 | Coordinar pruebas con PRs reales conocidos |
| P2 | Revisión final UI con PRs que tienen bugs reales |
| P3 | Documentar todos los casos de prueba ejecutados |
| P4 | Validar todos los códigos de error HTTP devueltos |
| P5 | Pruebas con PR de "código limpio" y PR con vulnerabilidades |
| P6 | Pruebas de límites: PR con > 5 archivos y > 1000 líneas |
| P7 | Generar informe interno de bugs encontrados |

Casos de prueba obligatorios:

- [ ] PR público válido con bugs
- [ ] PR público válido con vulnerabilidades de seguridad
- [ ] PR público con malas prácticas de estilo
- [ ] PR con código limpio (sin hallazgos)
- [ ] URL inválida
- [ ] PR de repositorio privado
- [ ] PR con más de 5 archivos modificados
- [ ] PR con más de 1000 líneas modificadas

---

## Día 13 — Code Freeze (14 jul)

> 🔒 No se mergean nuevas funcionalidades. Solo corrección de bugs críticos.

| Integrante | Tarea |
|-----------|-------|
| P1 | Supervisar correcciones · Aprobar merges de hotfixes |
| P2 | Corregir bugs críticos de UI |
| P3 | Corregir bugs críticos de UX |
| P4 | Corregir bugs críticos de backend |
| P5 | Corregir fallos de prompts o del grafo |
| P6 | Corregir fallos de la herramienta GitHub |
| P7 | Estabilizar el deploy · Crear tag de release `v1.0.0` |

---

## Días 14–15 — Cierre y entrega (15–16 jul)

> Todo el equipo colabora en E4 y preparación de la demo.

| Integrante | Tarea |
|-----------|-------|
| P1 | Liderar redacción E4 · Revisión final del README |
| P2 | Sección UI/UX del E4 · Capturas de pantalla del sistema |
| P3 | Grabación del vídeo demostrativo |
| P4 | Sección backend del E4 · Arquitectura final implementada |
| P5 | Sección IA/LangGraph del E4 · Prompts finales utilizados |
| P6 | Manual de uso técnico · Guía de instalación local |
| P7 | Limpieza del repositorio · Verificación del deploy final |

---

## ✅ Checkpoint Final — 16 de julio

- [ ] Frontend desplegado y accesible públicamente
- [ ] Backend desplegado y accesible públicamente
- [ ] LangGraph con los 3 agentes operativos
- [ ] Tests superados en GitHub Actions
- [ ] E4 redactado y entregado
- [ ] README completo con instrucciones de instalación
- [ ] Vídeo demostrativo grabado
- [ ] Tag `v1.0.0` creado en el repositorio

---

# Estructura del Proyecto

```
code-review-agent/
│
├── backend/
│   ├── main.py
│   ├── graph.py
│   ├── schemas.py
│   ├── agents/
│   │   ├── bug_agent.py
│   │   ├── security_agent.py
│   │   └── style_agent.py
│   └── tools/
│       └── github_tools.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── public/
│   └── package.json
│
├── docs/
│   ├── E1_Documento_De_Especificacion_De_Requisitos.md
│   ├── E2_Arquitectura_Diseño.md
│   ├── E3_Estado_del_Arte_e_Investigacion.md
│   ├── ROLES.md
│   ├── PLAN_EJECUCION.md
│   └── PLAN_MVP_CODE_REVIEW_AGENT.md
│
└── README.md
```

---

# Normas de Trabajo

## Git

- Rama principal de desarrollo: `develop`
- Cada tarea se trabaja en una rama propia: `feature/nombre-tarea`
- Todo merge a `develop` requiere PR aprobado por P1
- Nadie hace push directo a `main` ni a `develop`
- Commits en español, descriptivos

## Sesiones grupales

Se realizan sesiones grupales cuando el equipo enfrenta una tecnología nueva por primera vez:

- Primera vez con LangGraph → sesión grupal antes del Día 3
- Primera integración frontend–backend → sesión grupal al cierre del Día 5
- Revisión del contrato JSON → sesión grupal al inicio del Día 6

## Variables de entorno

Nunca se suben al repositorio. Cada integrante configura su `.env` local usando `.env.example` como referencia.

```env
GROQ_API_KEY=
GITHUB_TOKEN=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
```
