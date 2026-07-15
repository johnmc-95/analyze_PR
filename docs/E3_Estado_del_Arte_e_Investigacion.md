# 📄 E3 — Estado del Arte e Investigación

**Proyecto:** AI Code Review Agent (Web MVP)
**Fecha:** 25/06/2026
**Equipo:** 6–8 Integrantes

---

# 1. Benchmark de Soluciones Similares

Para fundamentar la viabilidad y el valor diferencial de la propuesta, se analiza el ecosistema actual de herramientas destinadas al aseguramiento de calidad del código.

Estas soluciones se dividen principalmente en dos categorías:

---

# 1.1 Analizadores Estáticos Tradicionales (Linters)

Ejemplos:

* SonarQube
* ESLint
* Pylint
* Flake8

## Ventajas

* Ejecución determinista.
* Alta velocidad de análisis.
* Bajo consumo de recursos.
* No requieren modelos de IA externos.

## Desventajas

* Funcionan mediante reglas predefinidas.
* Tienen comprensión limitada del contexto.
* No interpretan correctamente la intención del desarrollador.
* No generan explicaciones complejas en lenguaje natural.
* Sus sugerencias de refactorización son limitadas.

---

# 1.2 Asistentes Comerciales Basados en IA Generativa

Ejemplos:

* CodeRabbit
* GitHub Copilot
* Bito AI

## Ventajas

* Comprensión contextual del código.
* Capacidad de explicar problemas.
* Generación automática de soluciones.
* Integración con flujos de desarrollo modernos.

## Desventajas

* Dependencia de proveedores externos.
* Costes asociados al consumo de modelos.
* Algunas integraciones requieren configuraciones adicionales mediante GitHub Apps, Webhooks o servicios intermedios.
* Menor control sobre prompts y comportamiento interno del modelo.

---

# 1.3 Propuesta de Valor Diferencial del MVP

El proyecto propone combinar las ventajas del análisis tradicional y la IA generativa mediante un sistema web especializado.

## Interactividad Centralizada

El usuario no necesita instalar plugins ni configurar herramientas locales.

El análisis se realiza desde una interfaz web dedicada.

---

## Reportes en Español Orientados al Aprendizaje

El sistema genera explicaciones:

* Claras.
* Pedagógicas.
* Adaptadas al idioma español.
* Acompañadas de ejemplos y propuestas de refactorización.

---

## Arquitectura Basada en Agentes

A diferencia de herramientas simples, el sistema separa el análisis en agentes especializados:

* Bugs.
* Seguridad.
* Calidad y estilo.

Posteriormente un agente coordinador consolida los resultados.

---

## Uso Optimizado de Modelos IA

El MVP utiliza Groq como proveedor de inferencia debido a:

* Baja latencia.
* Compatibilidad con modelos abiertos.
* Integración sencilla mediante API.

El sistema queda sujeto a las cuotas y límites establecidos por el proveedor.

---

# 2. Comparativa de Tecnologías y Justificación del Stack

---

# 2.1 Backend: FastAPI

El backend será desarrollado utilizando FastAPI sobre Python.

Se selecciona frente a alternativas como Express o Django debido a:

---

## Compatibilidad con el Ecosistema IA

El ecosistema principal del proyecto utiliza:

* LangChain.
* LangGraph.
* Librerías de procesamiento IA en Python.

Esto evita dividir la lógica entre diferentes lenguajes.

---

## Asincronía y Concurrencia

El análisis depende de llamadas externas:

* GitHub API.
* Groq API.
* LangSmith.

FastAPI permite gestionar operaciones asíncronas evitando bloquear el servidor durante el procesamiento.

---

## Validación mediante Pydantic

Pydantic permite:

* Validar entradas.
* Garantizar contratos JSON.
* Evitar respuestas inconsistentes de los agentes.

Esto asegura compatibilidad con el frontend.

---

# 2.2 Frontend: React + Vite + Tailwind CSS

Se selecciona React con Vite en lugar de Next.js.

La decisión se basa en:

---

## Menor Curva de Aprendizaje

El equipo no necesita introducir complejidad adicional relacionada con:

* Server Side Rendering.
* Routing avanzado.
* Arquitecturas híbridas.

React permite centrarse en:

* Componentes.
* Estados.
* Peticiones HTTP.
* Renderizado de resultados.

---

## Desarrollo SPA

La aplicación funcionará como una Single Page Application orientada a escritorio.

Responsabilidades:

* Formulario de URL.
* Estados de carga.
* Visualización de resultados.
* Tarjetas de severidad.

---

## Tailwind CSS

Se utilizará para:

* Implementar Dark Mode.
* Crear componentes visuales rápidos.
* Mantener estilos consistentes.

---

# 3. Investigación de Herramientas de IA y Observabilidad

---

# 3.1 Orquestador de Flujos: LangGraph

Se selecciona LangGraph frente a cadenas secuenciales tradicionales debido a la necesidad de ejecutar análisis independientes.

La arquitectura utiliza un grafo con agentes especializados:

* Agente de Bugs.
* Agente de Seguridad.
* Agente de Calidad/Estilo.
* Agente Coordinador.

---

## Ventajas

Permite:

* Compartir estado entre agentes.
* Ejecutar ramas paralelas.
* Controlar errores.
* Consolidar resultados en un JSON final.

---

# 3.2 Modelo de Lenguaje: Groq + Llama 3.3 70B

El sistema utilizará:

```text
Llama-3.3-70B
```

mediante la API de Groq.

Razones:

* Buena capacidad de razonamiento sobre código.
* Baja latencia de inferencia.
* Compatibilidad con respuestas estructuradas.
* Buen desempeño en generación de explicaciones.

El uso está condicionado por los límites de cuota del proveedor.

---

# 3.3 Observabilidad: LangSmith

LangSmith se utilizará para monitorizar el comportamiento del sistema.

Permite:

* Revisar ejecuciones.
* Analizar prompts.
* Detectar errores.
* Medir latencias.
* Depurar respuestas de agentes.

Es especialmente importante debido a la naturaleza no determinista de los modelos generativos.

---

# 4. Metodología de Trabajo

## 4.1 Filosofía de Desarrollo

Debido al tamaño del equipo (6–8 integrantes), se adopta un enfoque colaborativo.

---

## Copropiedad del Código

Todos los integrantes tendrán conocimiento del flujo completo:

* Frontend.
* Backend.
* Agentes IA.
* Documentación.

---

## Pair Programming

Se utilizarán sesiones de programación conjunta para:

* Reducir errores.
* Transferir conocimiento.
* Acelerar aprendizaje.

---

## Daily Scrum

Reuniones breves orientadas a:

* Seguimiento.
* Bloqueos.
* Organización diaria.

---

# 5. Cronograma del Proyecto

---

# Semana 1 — Base del Sistema

## Días 1-2

* Finalización de E1, E2 y E3.
* Definición del diseño final.
* Configuración del repositorio.

---

## Día 3

Frontend:

* Inicialización React + Vite.
* Configuración Tailwind.

Backend:

* Creación FastAPI.
* Pruebas GitHub API.
* Configuración Groq.

---

## Día 4

Implementación:

* Formulario inicial.
* Endpoint:

```http
POST /review/initiate
```

* Extracción del diff.

---

## Día 5

Integración inicial:

* GitHub API.
* Primer agente IA.
* Configuración LangSmith.

---

# Semana 2 — Integración IA Completa

## Día 6

Implementación:

* Agente Bugs.
* Agente Seguridad.
* Agente Calidad/Estilo.

---

## Día 7

Integración frontend/backend:

* Peticiones HTTP.
* Pantallas de carga.
* Gestión de errores.

---

## Día 8

Implementación:

* Nodo de consolidación LangGraph.
* JSON final validado.

---

## Días 9-10

Refinamiento:

* Dark Mode.
* Tarjetas visuales.
* Mejora de prompts.
* Control de respuestas incorrectas.

---

# Semana 3 — QA y Entrega

## Día 11

Pruebas:

* Unitarias.
* Integración.
* Validación de endpoints.

Automatización mediante GitHub Actions.

---

## Día 12

Pruebas extremas:

* PRs con errores reales.
* Código vulnerable.
* Exceso de archivos.
* Exceso de líneas modificadas.

---

## Día 13

Code Freeze:

* Corrección final.
* Estabilización.

---

## Días 14-15

Cierre:

* Documentación final.
* README.
* Preparación de demostración.
* Entrega del proyecto.

---

# 6. Conclusión

El análisis del estado actual demuestra que existe una oportunidad para desarrollar una herramienta intermedia entre los analizadores estáticos tradicionales y los asistentes comerciales de IA.

El MVP propone una arquitectura basada en agentes especializados que permite generar revisiones automáticas, explicativas y orientadas a mejorar la calidad del código manteniendo un alcance viable dentro de tres semanas.
