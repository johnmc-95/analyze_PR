# 🤖 Code Review Agent — Plan MVP (3 Semanas / 5 Personas)

## 📌 Información General

**Stack Tecnológico**

* Backend: FastAPI
* Orquestación IA: LangChain + LangGraph
* LLM: Groq (Llama 3.3 70B)
* Integración: GitHub API
* Frontend: React + Vite + Tailwind CSS

**Duración:** 3 semanas

**Dedicación estimada:** 1–2 horas diarias por integrante

**Equipo:** 5 integrantes

**Objetivo del MVP**

Desarrollar una aplicación web que permita a un desarrollador pegar la URL de un Pull Request (PR) de GitHub y recibir un informe visual e interactivo con:

* Bugs potenciales
* Problemas de seguridad
* Incumplimientos de convenciones y estilo de código

---

# 📊 Entregables del Proyecto

## E1 — Documento de Especificación de Requisitos

Definición de:

* Requisitos funcionales
* Requisitos no funcionales
* Casos de uso
* Restricciones del sistema

---

## E2 — Documento de Arquitectura y Diseño

Incluye:

* Arquitectura del sistema
* Diagramas de componentes
* Flujo de información
* Diseño conceptual de LangGraph

---

## E3 — Estado del Arte e Investigación

Incluye:

* Comparativa de tecnologías
* Investigación de herramientas IA
* Benchmark de soluciones similares
* Cronograma y distribución de tareas

---

## E4 — Entrega Final

Incluye:

* Código fuente completo
* Batería de pruebas ejecutadas
* Documentación técnica
* Evidencias de despliegue
* Manual de uso

---

# 🚧 Fase 1 — Especificación, Diseño y Estructura Core

## Semana 1

### Objetivos

* Completar E1, E2 y E3.
* Crear la base del Frontend y Backend.
* Conseguir que un agente analice un PR y devuelva un JSON estructurado.

---

## Día 1

### Todo el equipo

* Redacción del documento de requisitos (E1).
* Investigación tecnológica y estado del arte (E3).
* Definición del alcance del MVP.

---

## Día 2

### Todo el equipo

* Diseño conceptual del sistema.
* Diagramas de arquitectura.
* Diseño del flujo de LangGraph.
* Redacción del documento E2.

---

## Día 3

### Frontend

* Inicialización de proyecto React con Vite.
* Configuración de Tailwind CSS.
* Definición de estructura de carpetas.

### Backend

* Configuración inicial de FastAPI.
* Definición de modelos Pydantic.

### IA 1

* Integración con GitHub API.
* Obtención del diff de un Pull Request.

### IA 2

* Diseño de prompts iniciales.
* Primeras pruebas con Groq (Llama 3.3 70B).

### DevOps

* Configuración del repositorio.
* GitFlow.
* Protección de rama `develop`.
* Configuración del entorno local.

---

## Día 4

### Frontend

* Desarrollo del formulario principal.
* Campo para URL del Pull Request.

### Backend

* Endpoint:

```http
POST /review/initiate
```

* Validación de URL de GitHub.

### IA 1

* Implementación de Tool:

```python
get_pr_diff(url)
```

### IA 2

* Configuración inicial del Agente 1:

  * Bugs
  * Seguridad

### DevOps

* Integración de LangSmith para observabilidad.

---

## Día 5

### Frontend

* Pantalla de carga.
* Spinner de análisis.

### Backend

* Integración inicial del agente dentro del endpoint.

### IA 1 + IA 2

* Conexión:

  * GitHub Tool
  * Agente de análisis

### DevOps

* Scripts iniciales de testing local.

---

## ✅ Checkpoint Semana 1

El sistema debe permitir:

1. Recibir una URL de PR vía HTTP.
2. Descargar el diff.
3. Analizarlo mediante IA.
4. Devolver un JSON estructurado.

Además:

* E1 completado.
* E2 completado.
* E3 completado.

---

# 🚧 Fase 2 — Orquestación de Agentes y Conexión Web

## Semana 2

### Objetivos

* Implementar LangGraph.
* Ejecutar agentes en paralelo.
* Conectar Frontend y Backend.

---

## Día 6

### Frontend

* Diseño de tarjetas visuales.

| Severidad  | Color       |
| ---------- | ----------- |
| Crítico    | 🔴 Rojo     |
| Medio      | 🟡 Amarillo |
| Convención | 🔵 Azul     |

### Backend

* Adaptar endpoint para respuesta combinada.

### IA 1

* Desarrollo del Agente 2:

  * Convenciones
  * Estilo

### IA 2

* Configuración del grafo LangGraph.

### DevOps

* CI/CD automático en:

  * Render
  * Railway

---

## Día 7

### Frontend

* Integración API mediante:

  * fetch
  * axios

### Backend

* Manejo de errores:

  * PR inexistente
  * Repositorio privado
  * URL inválida
  * Timeouts

### IA 1 + IA 2

* Ejecución paralela de agentes.

### DevOps

* Variables de entorno seguras:

```env
GROQ_API_KEY=
GITHUB_TOKEN=
LANGSMITH_API_KEY=
```

---

## Día 8

### Frontend

* Renderizado dinámico de resultados.

### Backend

* Optimización de respuesta.
* Reducción del tamaño del JSON.

### IA 1

* Refinamiento de prompts.

### IA 2

* Nodo de consolidación:

```text
Agent Bugs/Security
         ↓
     Aggregator
         ↑
Agent Conventions
```

### DevOps

* Pruebas E2E completas.

---

## Día 9 y Día 10

### Todo el equipo

* Ajustes de UI/UX.
* Reducción de falsos positivos.
* Corrección de incidencias.
* Optimización general.

---

## ✅ Checkpoint Semana 2

Flujo completo operativo:

1. Usuario pega URL.
2. Frontend envía petición.
3. Backend ejecuta LangGraph.
4. Agentes analizan en paralelo.
5. Resultado mostrado visualmente.

**Tiempo objetivo:** menos de 30 segundos.

---

# 🚧 Fase 3 — Testing, Estabilización y Cierre

## Semana 3

### Objetivos

* Garantizar calidad.
* Ejecutar pruebas.
* Preparar entrega final.

---

## Día 11

### Frontend

* Manejo visual de errores.

### Backend + IA

* Tests unitarios con pytest.

### DevOps

* GitHub Actions.

Ejecutar pruebas automáticamente en cada Pull Request.

---

## Día 12

### Todo el equipo

Pruebas funcionales finales:

* Casos válidos.
* Casos inválidos.
* PRs con errores reales.
* PRs con vulnerabilidades.
* PRs con malas prácticas.

Generación de informe interno de bugs.

---

## Día 13

### Todo el equipo

* Corrección de incidencias.
* Congelación de versiones.
* Preparación de release.

---

## Día 14 y Día 15

### Todo el equipo

Redacción de E4:

* Memoria técnica.
* Manual de usuario.
* Arquitectura final.
* Resultados obtenidos.

Además:

* Grabación de vídeo demostrativo.
* Limpieza del repositorio.
* Revisión final del README.

---

## ✅ Checkpoint Final

### Entrega MVP Completa

* Frontend desplegado.
* Backend desplegado.
* LangGraph funcionando.
* Tests superados.
* Documentación entregada.

---

# 📁 Estructura del Proyecto

```text
code-review-agent/
│
├── backend/
│   ├── main.py
│   ├── graph.py
│   ├── schemas.py
│   │
│   ├── agents/
│   │   ├── bug_agent.py
│   │   └── convention_agent.py
│   │
│   └── tools/
│       └── github_tools.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
└── README.md
```

---

# 🔄 Flujo General del Sistema

```text
Usuario
   │
   ▼
Frontend (React + Vite)
   │
   ▼
FastAPI Endpoint
   │
   ▼
GitHub API
   │
   ▼
Obtención del Diff
   │
   ▼
LangGraph
 ┌───────────────┐
 │               │
 ▼               ▼
Agent 1      Agent 2
Bugs/Sec.    Convenciones
 │               │
 └───────┬───────┘
         ▼
 Consolidación
         ▼
 JSON Final
         ▼
 Frontend
```

---

# 🚀 Funcionalidades Fuera del MVP

## 1. Historial de Análisis

### Razón

Requiere:

* Base de datos persistente
* Autenticación
* Gestión de usuarios

Posible stack futuro:

* PostgreSQL
* Supabase

---

## 2. Sistema de Prompts Dinámicos

### Razón

Aumenta:

* Complejidad de UI
* Riesgo de inconsistencia

El MVP utilizará prompts fijos optimizados.

---

## 3. Integración Automática con GitHub

### Razón

Requiere:

* GitHub App
* Webhooks
* Infraestructura adicional

El MVP utilizará análisis manual mediante URL.

---

# 🎯 Resultado Esperado del MVP

Un desarrollador podrá:

1. Copiar la URL de un Pull Request.
2. Pegarla en la aplicación web.
3. Obtener un análisis automatizado del código.
4. Visualizar:

   * Bugs potenciales
   * Riesgos de seguridad
   * Problemas de estilo
5. Recibir recomendaciones organizadas por severidad en menos de 30 segundos.
