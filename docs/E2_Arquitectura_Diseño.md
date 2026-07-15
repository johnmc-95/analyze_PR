# 📄 E2 — Documento de Arquitectura y Diseño

**Proyecto:** AI Code Review Agent (Web MVP)
**Fecha:** 25/06/2026
**Equipo:** 6–8 Integrantes

---

# 1. Arquitectura General del Sistema

El sistema sigue una arquitectura desacoplada Cliente-Servidor basada en tres capas principales:

1. **Capa de Presentación (Frontend)**
2. **Capa de Aplicación (Backend/API)**
3. **Capa de Inteligencia Artificial (Orquestación mediante LangGraph)**

La arquitectura está diseñada para cumplir los requisitos definidos en el documento E1, permitiendo análisis automáticos de Pull Requests mediante agentes especializados de IA.

---

## Diagrama General de Arquitectura

```text
┌──────────────────────────────────────────────┐
│           CAPA DE PRESENTACIÓN               │
│                                              │
│      React + Vite + Tailwind CSS             │
│      Desktop First + Dark Mode               │
└──────────────────────┬───────────────────────┘
                       │
                       │ HTTP POST Asíncrono
                       ▼

┌──────────────────────────────────────────────┐
│              CAPA DE APLICACIÓN              │
│                                              │
│      FastAPI + Pydantic                      │
│                                              │
│  - Validación de URL                         │
│  - Validación de restricciones               │
│  - Gestión de solicitudes                   │
└──────────────────────┬───────────────────────┘
                       │

                       ▼

┌──────────────────────────────────────────────┐
│            CAPA DE ORQUESTACIÓN IA           │
│                                              │
│              LangGraph                       │
│                                              │
│  - GitHub API Tool                           │
│  - Groq API (Llama-3.3-70B)                  │
│  - LangSmith Monitoring                      │
└──────────────────────────────────────────────┘
```

---

# Descripción de Componentes

## Frontend (React + Vite)

Aplicación web orientada a escritorio que permite:

* Introducir la URL del Pull Request.
* Mostrar estados de carga.
* Mostrar errores de validación.
* Renderizar resultados mediante tarjetas visuales.
* Clasificar hallazgos según severidad.

El frontend no interpreta directamente respuestas de texto libre de la IA, sino un JSON estructurado recibido desde el backend.

---

## Backend (FastAPI)

Responsable de:

* Exponer endpoints HTTP.
* Validar entradas del usuario.
* Aplicar reglas de negocio.
* Gestionar comunicación con LangGraph.
* Validar respuestas mediante Pydantic.
* Devolver resultados estructurados al frontend.

El backend utiliza programación asíncrona para evitar bloqueos durante las llamadas a modelos de IA.

---

## Orquestador IA (LangGraph)

Motor encargado de coordinar el flujo de análisis mediante un grafo de estados.

Sus responsabilidades:

* Controlar el flujo entre agentes.
* Mantener el estado del análisis.
* Ejecutar agentes especializados.
* Consolidar resultados.
* Generar la respuesta final.

---

# 2. Flujo de Información (Data Flow)

El sistema utiliza una solicitud HTTP asíncrona de larga duración.

El cliente mantiene la petición abierta mientras el backend ejecuta el análisis completo.

---

## Secuencia de Datos

1. El usuario introduce la URL del Pull Request en el frontend React.

2. El frontend envía:

```http
POST /review/initiate
```

con la URL del PR.

3. FastAPI realiza:

* Validación del formato.
* Verificación de repositorio público.
* Validación inicial de datos.

4. FastAPI envía la solicitud al grafo de LangGraph.

5. El nodo inicial obtiene el diff mediante GitHub API.

6. Se validan restricciones:

* Máximo 5 archivos modificados.
* Máximo 1000 líneas modificadas.

7. LangGraph ejecuta agentes especializados en paralelo:

* Detección de bugs.
* Análisis de seguridad.
* Revisión de estilo.

8. Los resultados son enviados al agente coordinador.

9. El agente coordinador:

* Elimina duplicados.
* Clasifica severidad.
* Genera recomendaciones.
* Construye el JSON final.

10. FastAPI valida la estructura mediante Pydantic.

11. El frontend recibe la respuesta y renderiza las tarjetas visuales.

---

# Evolución Arquitectónica Futura

Para futuras versiones se contempla evolucionar hacia comunicación basada en eventos mediante:

* Server-Sent Events (SSE)
* WebSockets

Esto permitiría mostrar estados intermedios:

* Extrayendo código.
* Analizando seguridad.
* Generando reporte.

---

# 3. Diseño Conceptual de LangGraph

El sistema se modela como un grafo de estados donde cada nodo realiza una tarea específica.

Los nodos comparten un estado común (`StateSchema`).

---

# Estado del Grafo (StateSchema)

```python
ReviewState:

pr_url: str

raw_diff: str

files_count: int

changed_lines: int

bug_issues: list

security_issues: list

style_issues: list

final_report: dict

status: str

# Campos de error (RF-08) con reducer para tolerar fallos simultáneos
# de los nodos paralelos bug/security/style:
error_message: Annotated[str | None, _conservar_primer_error]

error_status: Annotated[int | None, _conservar_primer_error]

error_code: Annotated[str | None, _conservar_primer_error]
```

---

# Diagrama del Grafo

```text
                 [ START ]

                      |

                      ▼

              download_diff

                      |

                      ▼

          validate_constraints

                      |

       ┌──────────────┼──────────────┐

       ▼              ▼              ▼


 bug_analysis   security_analysis   style_analysis

    node             node              node


       └──────────────┼──────────────┘

                      ▼


          consolidation_node

                      |

                      ▼

                   [ END ]
```

---

# Especificación de los Nodos

---

## download_diff

Nodo responsable de obtener información desde GitHub.

Funciones:

* Conectarse a GitHub API.
* Descargar el diff del Pull Request.
* Guardar contenido en `raw_diff`.

Utiliza:

```text
GitHub API Tool
```

---

## validate_constraints

Nodo encargado de validar límites del MVP.

Comprueba:

* Número máximo de archivos.
* Cantidad máxima de líneas modificadas.

Si falla:

* Detiene el flujo.
* Genera mensaje de error.

---

# Agentes Especializados

---

## bug_analysis_node

Responsable de detectar:

* Errores lógicos.
* Fallos de ejecución.
* Problemas de rendimiento.

Modelo utilizado:

```text
Groq - Llama-3.3-70B
```

Salida:

```text
bug_issues
```

---

## security_analysis_node

Responsable de detectar:

* Vulnerabilidades.
* Credenciales expuestas.
* Malas prácticas críticas.

Salida:

```text
security_issues
```

---

## style_analysis_node

Responsable de revisar:

* Clean Code.
* Convenciones.
* Legibilidad.
* Mantenibilidad.

Salida:

```text
style_issues
```

---

# consolidation_node

Nodo final del flujo.

Responsabilidades:

* Unificar resultados.
* Eliminar duplicados.
* Definir severidad.
* Crear resumen general.
* Detectar código limpio.
* Generar JSON final.

---

# 4. Contrato de Intercambio de Datos

El backend y frontend se comunican mediante un contrato JSON validado utilizando Pydantic.

Esto garantiza que el frontend siempre reciba una estructura consistente.

---

# Ejemplo JSON Final

```json
{
  "summary": {
    "status": "issues_found",
    "total_issues": 1,
    "global_comment": "Se detectaron problemas de seguridad que requieren atención."
  },

  "findings": [

    {
      "id": "ISSUE-001",

      "file_name": "backend/main.py",

      "line_number": 45,

      "category": "security",

      "severity": "critical",

      "explanation":
      "Se detectó una API Key escrita directamente en el código.",

      "bad_example":
      "API_KEY = '12345'",

      "refactor_suggestion":
      "Utilizar variables de entorno para almacenar credenciales.",

      "code_fix":
      "import os\n\nAPI_KEY = os.getenv('API_KEY')"
    }

  ],

  "metadata": {

    "model":
    "llama-3.3-70b",

    "files_processed":
    3,

    "changed_lines":
    250

  }
}
```

---

# Respuesta cuando el código está limpio

Ejemplo:

```json
{
  "summary": {

    "status": "clean",

    "total_issues": 0,

    "global_comment":
    "¡Buen trabajo! El código analizado no presenta problemas relevantes."
  },

  "findings": []
}
```

El frontend utilizará este estado para mostrar una pantalla positiva de código limpio.

---

# 5. Manejo de Errores

El sistema contempla errores provenientes de servicios externos.

Casos:

## GitHub API

Ejemplos:

* Pull Request inexistente.
* Repositorio privado.
* Rate Limit.
* Error de conexión.

---

## Groq API

Ejemplos:

* Timeout.
* Fallo de inferencia.
* Respuesta inválida.

---

## Flujo de error

Los nodos escriben los campos de error en el estado del grafo. El endpoint de FastAPI lee `error_message` tras `graph.invoke()` y lanza el `HTTPException` correspondiente con el código HTTP y el mensaje seguro para el usuario.

```text
            Nodo actual

                 |

              error

                 |

                 ▼

    error_message / error_status
    / error_code  → estado del grafo

                 |

                 ▼

          FastAPI (main.py)
          HTTPException

                 |

                 ▼

          Respuesta HTTP

```

---

# 6. Observabilidad y Trazabilidad

Todo el flujo de ejecución de LangGraph será conectado con LangSmith.

Permitirá:

* Ver prompts utilizados.
* Revisar respuestas de agentes.
* Analizar tiempos.
* Detectar errores.
* Mejorar instrucciones.

---

# 7. Consideraciones de Despliegue

Arquitectura prevista:

```text
Usuario

   |

   ▼

Frontend React + Vite

   |

   ▼

Backend FastAPI

   |

   ├──────────────► GitHub API

   |

   ├──────────────► Groq API

   |

   └──────────────► LangSmith

```

---

# 8. Decisiones de Diseño del MVP

Las decisiones principales son:

* Sin base de datos.
* Procesamiento bajo demanda.
* Máximo 5 archivos modificados.
* Máximo 1000 líneas modificadas.
* Análisis mediante agentes paralelos.
* Comunicación mediante JSON estructurado.
* Diseño Desktop First.
* Dark Mode por defecto.

Estas decisiones permiten entregar un MVP funcional dentro del plazo de 3 semanas.
