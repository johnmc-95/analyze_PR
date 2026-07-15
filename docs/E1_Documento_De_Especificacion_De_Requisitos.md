# 📄 E1 — Documento de Especificación de Requisitos

**Proyecto:** AI Code Review Agent (Web MVP)
**Fecha:** 25/06/2026
**Equipo:** 6–8 Integrantes

---

# 1. Requisitos Funcionales (RF)

Los requisitos funcionales describen los servicios, funciones y comportamientos que el sistema debe proveer de forma obligatoria.

## RF-01: Validación y Recepción de URL

El sistema debe disponer de un campo de entrada en la interfaz web para recibir la URL de un Pull Request (PR) de GitHub.

El sistema verificará que:

* La URL tenga un formato válido.
* Corresponda a un Pull Request existente.
* El repositorio sea público y accesible.
* El Pull Request pueda ser consultado mediante la API de GitHub.

En caso de incumplir alguna condición, el sistema mostrará un mensaje de error descriptivo.

---

## RF-02: Extracción del Código (Diff)

El sistema debe conectarse automáticamente a la API de GitHub para descargar las líneas de código modificadas (diff) asociadas al Pull Request proporcionado.

La extracción incluirá:

* Archivos modificados.
* Líneas agregadas.
* Líneas eliminadas.
* Información de contexto necesaria para el análisis.

---

## RF-03: Análisis Multicapa por IA

El sistema debe procesar el código mediante un flujo de agentes coordinados con LangGraph.

El análisis deberá ejecutarse mediante tres agentes especializados:

### Agente de Bugs y Errores Lógicos

Detectará:

* Posibles fallos de ejecución.
* Problemas de rendimiento.
* Errores de lógica de negocio.

### Agente de Seguridad

Detectará:

* Vulnerabilidades conocidas.
* Exposición de credenciales.
* Inyecciones y malas prácticas de seguridad.

### Agente de Calidad y Estilo

Detectará:

* Incumplimiento de principios Clean Code.
* Problemas de mantenibilidad.
* Violaciones de convenciones de estilo.

---

## RF-04: Consolidación de Hallazgos

Un agente coordinador deberá consolidar los resultados generados por los agentes especializados y producir una respuesta única, estructurada y libre de duplicados.

---

## RF-05: Generación de Reportes con Refactor

Para cada hallazgo detectado, la IA deberá generar un informe en español que incluya:

* Categoría del problema.
* Severidad.
* Línea o bloque de código afectado.
* Explicación del problema.
* Ejemplo del posible fallo.
* Sugerencia de corrección.
* Fragmento de código refactorizado.

---

## RF-06: Manejo de Código Limpio

Si el análisis no detecta problemas de seguridad, bugs ni incumplimientos de estilo, el sistema mostrará:

* Un mensaje visual de éxito:

  > "¡Buen trabajo! Código limpio."

* Un comentario positivo generado por la IA en función de la calidad y estructura del código analizado.

---

## RF-07: Interfaz Visual de Resultados

El frontend deberá transformar el JSON generado por el backend en componentes visuales interactivos.

Cada hallazgo deberá mostrarse mediante tarjetas clasificadas y ordenadas de mayor a menor severidad:

* 🔴 Crítica
* 🟠 Alta
* 🟡 Media
* 🟢 Baja

No se mostrará la respuesta de la IA como texto plano sin procesar.

---

## RF-08: Manejo de Errores Externos

El sistema deberá detectar y comunicar adecuadamente errores provenientes de servicios externos.

Entre ellos:

* Error de conexión con GitHub.
* Pull Request inexistente.
* Límite de cuota (Rate Limit) alcanzado.
* Error de inferencia del modelo.
* Timeout de servicios externos.

Los mensajes deberán ser comprensibles para usuarios no técnicos.

---

# 2. Requisitos No Funcionales (RNF)

Los requisitos no funcionales definen las propiedades, restricciones y estándares de calidad del sistema.

---

## RNF-01: Tiempo de Respuesta

El tiempo promedio de procesamiento completo de una solicitud no deberá superar los 20 segundos bajo condiciones normales de operación.

El tiempo incluye:

* Validación del PR.
* Descarga del diff.
* Ejecución de agentes.
* Generación del reporte.
* Renderizado de resultados.

---

## RNF-02: Diseño Desktop First

La interfaz web estará diseñada exclusivamente para resoluciones de escritorio iguales o superiores a 1024 px de ancho.

No se requiere soporte responsive para dispositivos móviles durante el MVP.

---

## RNF-03: Tema Visual

La aplicación utilizará modo oscuro (Dark Mode) como configuración visual predeterminada.

---

## RNF-04: Concurrencia

El sistema deberá soportar múltiples solicitudes simultáneas sin bloquear el servidor ni degradar significativamente los tiempos de respuesta.

---

## RNF-05: Mantenibilidad y Trazabilidad

Todo el flujo de agentes, prompts, ejecuciones y respuestas deberá estar integrado con LangSmith para facilitar:

* Auditoría.
* Observabilidad.
* Depuración.
* Optimización de prompts.

---

# 3. Restricciones del Sistema

Límites técnicos y operativos definidos para el alcance del MVP.

---

## RS-01: Límite de Archivos por Pull Request

El sistema procesará un máximo de 5 archivos modificados por Pull Request.

Si se supera dicho límite, el análisis será cancelado y se mostrará una advertencia al usuario.

---

## RS-02: Límite de Líneas Modificadas

El sistema procesará un máximo de 1000 líneas modificadas por Pull Request.

Si el límite es excedido, el sistema cancelará el análisis para evitar problemas de rendimiento y contexto del modelo.

---

## RS-03: Dependencia de Servicios Externos

El sistema depende de la disponibilidad y cuotas de:

* API de GitHub.
* API de inferencia de Groq (Llama 3.3 70B).

No se garantiza disponibilidad cuando dichos servicios presenten fallos externos.

---

## RS-04: Lenguajes Soportados

Durante el MVP, el análisis estará optimizado para:

* Python
* JavaScript
* TypeScript

Otros lenguajes podrán procesarse, pero sin garantía de calidad en los resultados.

---

## RS-05: Sin Persistencia de Datos

El MVP no contará con base de datos.

Todos los análisis serán ejecutados bajo demanda y se perderán al recargar la aplicación.

---

# 4. Casos de Uso (CU)

---

# CU-01: Analizar un Pull Request con Hallazgos

### Actor

Desarrollador

### Precondición

El usuario dispone de una URL válida de un Pull Request público que cumple los límites establecidos.

### Flujo Principal

1. El desarrollador introduce la URL del PR.
2. Pulsa el botón **"Analizar"**.
3. El sistema valida la URL.
4. Se muestra una pantalla de carga.
5. El backend descarga el diff desde GitHub.
6. Se ejecuta el flujo paralelo de agentes en LangGraph.
7. Los agentes detectan problemas de bugs, seguridad y estilo.
8. El agente coordinador consolida los hallazgos.
9. El frontend renderiza las tarjetas de resultados.
10. El usuario revisa las recomendaciones y refactors generados.

### Flujo Alternativo A — PR Sin Hallazgos

1. Los agentes no detectan problemas.
2. El sistema muestra una pantalla de éxito.
3. Se genera un comentario positivo sobre el código.

### Flujo Alternativo B — Validación Incorrecta

1. La URL es inválida, el repositorio es privado o el PR no existe.
2. El sistema cancela el análisis.
3. Se muestra una alerta descriptiva.
4. El usuario regresa a la pantalla inicial.

### Flujo Alternativo C — Exceso de Tamaño

1. El sistema detecta más de 5 archivos o más de 1000 líneas modificadas.
2. El análisis se cancela.
3. Se muestra una advertencia indicando el límite excedido.

---

# CU-02: Error de GitHub

### Actor

Sistema

### Flujo

1. El usuario inicia un análisis.
2. GitHub responde con un error o timeout.
3. El sistema cancela la ejecución.
4. Se informa al usuario que el servicio externo no está disponible.

---

# CU-03: Error del Modelo de IA

### Actor

Sistema

### Flujo

1. El análisis es enviado al proveedor de IA.
2. El modelo no responde o devuelve un error.
3. El sistema registra el incidente.
4. Se muestra un mensaje solicitando reintentar más tarde.

---

# 5. Criterios de Aceptación

El MVP será considerado funcional cuando:

* Se pueda analizar un PR público válido.
* Se detecten y clasifiquen hallazgos de bugs, seguridad y estilo.
* Se generen sugerencias de refactor en español.
* Los resultados se visualicen mediante tarjetas interactivas.
* El sistema gestione correctamente errores de GitHub y del proveedor de IA.
* El tiempo promedio de respuesta sea inferior a 20 segundos para PRs dentro de los límites establecidos.
* Toda la trazabilidad de agentes sea visible desde LangSmith.
* No se requiera persistencia de datos para operar correctamente.
