# Pruebas funcionales con Pull Requests reales — Issue #47

**Fecha:** 07/07/2026  
**Rama:** `test/pruebas-funcionales-prs`  
**Entorno:** Windows, frontend Vite en `http://localhost:5173` y FastAPI en `http://127.0.0.1:8000`

## Resultado general

**NO APROBADO todavía.** Los casos funcionales principales responden según el contrato, pero el tiempo medio de los análisis exitosos con hallazgos fue de **30,05 segundos**, por encima del máximo de 20 segundos establecido en RNF-01. También se observó un fallo intermitente del proveedor de IA.

## Comprobaciones automáticas

| Comprobación | Resultado |
|---|---|
| Backend: `pytest -q` | APROBADO — 52 pruebas |
| Frontend: `npm run build` | APROBADO |
| Frontend: `npm run lint` | APROBADO |

Pytest mostró una advertencia de deprecación de `httpx`/`TestClient`, sin afectar al resultado de las pruebas.

## Casos obligatorios

### 1. PR público con bugs reales

- **URL:** https://github.com/maykmbs/code-review-dataquantum/pull/63
- **Resultado:** APROBADO funcionalmente.
- **Evidencia:** HTTP 200, estado `issues_found` y hallazgos de categoría `bug`.
- **Observación:** este PR también produjo hallazgos de seguridad y estilo.

### 2. PR público con vulnerabilidades de seguridad

- **URL:** https://github.com/maykmbs/code-review-dataquantum/pull/63
- **Resultado:** APROBADO funcionalmente.
- **Evidencia:** HTTP 200 y hallazgos de categoría `security`.

### 3. PR público con malas prácticas de estilo

- **URL:** https://github.com/maykmbs/code-review-dataquantum/pull/63
- **Resultado:** APROBADO funcionalmente.
- **Evidencia:** HTTP 200 y hallazgos de categoría `style`.

### 4. PR con código limpio

- **URL:** https://github.com/maykmbs/code-review-dataquantum/pull/51
- **Resultado:** APROBADO con limitación del fixture.
- **Evidencia:** HTTP 200, estado `clean`, 0 hallazgos, 1 archivo y 0 líneas modificadas.
- **Limitación:** valida la respuesta limpia del sistema, pero conviene repetir la prueba con un PR que contenga código real sin problemas.
- **Prueba adicional:** el PR #55, con un cambio mínimo, devolvió HTTP 502 por indisponibilidad de Groq tras 10,19 segundos.

### 5. URL inválida

- **Entrada:** `https://example.com/owner/repo/pull/1`
- **Resultado:** APROBADO.
- **Evidencia:** HTTP 422 en 0,01 segundos con mensaje indicando el formato requerido de GitHub.

### 6. PR de repositorio privado

- **Entrada:** URL de repositorio privado o no accesible para el token.
- **Resultado:** PARCIAL.
- **Evidencia:** HTTP 404 en 0,51 segundos con el mensaje: «No encontramos el Pull Request. Revisa que la URL sea correcta y que el repositorio sea público.»
- **Limitación:** GitHub no permite distinguir externamente entre un repositorio privado sin acceso y uno inexistente. Para completar la evidencia se necesita una URL privada real a la que el token de pruebas no tenga acceso.

### 7. PR con más de 5 archivos modificados

- **URL:** https://github.com/maykmbs/code-review-dataquantum/pull/62
- **Datos de GitHub:** 10 archivos y 322 líneas modificadas.
- **Resultado:** APROBADO.
- **Evidencia:** HTTP 422 en 0,84 segundos con error RS-01 y recomendación de dividir el Pull Request.

### 8. PR con más de 1000 líneas modificadas

- **URL:** https://github.com/servisbot/node-red/pull/67
- **Datos de GitHub:** 2 archivos y 10.916 líneas modificadas.
- **Resultado:** APROBADO.
- **Evidencia:** HTTP 422 en 1,35 segundos con error RS-02 y recomendación de dividir el Pull Request.
- **Nota:** se eligió un PR externo para aislar RS-02 sin superar simultáneamente el límite de cinco archivos.

## Medición de rendimiento

Se utilizó el PR #63, que está dentro de los límites del MVP y ejecuta los tres agentes.

| Ejecución | Resultado | Tiempo | Hallazgos |
|---|---:|---:|---:|
| 1 | HTTP 200 | 29,52 s | 8 |
| 2 | HTTP 200 | 30,57 s | 8 |
| 3 | HTTP 502 | 56,52 s | — |

**Promedio de ejecuciones exitosas:** `(29,52 + 30,57) / 2 = 30,05 s`.

**Resultado RNF-01:** FALLIDO. El promedio supera el máximo de 20 segundos.

## Incidencias encontradas

1. **PERF-01 — Tiempo de respuesta:** el análisis completo tarda aproximadamente 30 segundos en las ejecuciones exitosas.
2. **EXT-01 — Inestabilidad de Groq:** una de las tres ejecuciones del PR #63 y la prueba del PR #55 devolvieron HTTP 502.
3. **FIXTURE-01 — Repositorio privado:** falta una URL privada controlada para demostrar el caso independientemente de un repositorio inexistente.
4. **FIXTURE-02 — Código limpio:** se recomienda crear un PR pequeño con código real y sin hallazgos para reforzar la prueba del estado `clean`.

## Conclusión

Los flujos de hallazgos, validación, errores externos y restricciones RS-01/RS-02 funcionan. La issue no cumple todavía completamente su criterio de aceptación debido al tiempo de respuesta superior a 20 segundos y a la falta de fixtures controlados para repositorio privado y código limpio real.
