"""
Observabilidad y trazabilidad de errores externos (RF-08 / RNF-05).

Registra los errores de servicios externos SIEMPRE en el logging estándar y,
de forma opcional, en LangSmith cuando hay una API key configurada.

El diseño es "degradación elegante": si LangSmith no está instalado, no hay
API key, o la llamada falla, la aplicación sigue funcionando y el error queda
al menos en el log. Así los tests y el desarrollo local no necesitan clave.
"""

import logging
import os

from errors import ExternalServiceError

logger = logging.getLogger("code_review")

# Configuración básica de logging solo si nadie la ha definido antes,
# para no pisar la configuración de uvicorn u otros hosts.
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def _langsmith_enabled() -> bool:
    """LangSmith solo se usa si hay API key en el entorno."""
    return bool(os.getenv("LANGSMITH_API_KEY"))


def _log_to_langsmith(err: ExternalServiceError, *, pr_url: str, node: str) -> None:
    """
    Envía el error a LangSmith como un run independiente para trazabilidad.

    Cualquier fallo aquí (dependencia ausente, red, credenciales) se ignora:
    la trazabilidad es un extra que nunca debe romper la petición del usuario.
    """
    try:
        from langsmith import Client

        Client().create_run(
            name="external_error",
            run_type="chain",
            inputs={"pr_url": pr_url, "node": node},
            outputs={"error_code": err.error_code, "status_code": err.status_code},
            error=err.technical_detail or err.user_message,
            project_name=os.getenv("LANGSMITH_PROJECT", "code-review-agent"),
        )
    except Exception:  # noqa: BLE001 - la observabilidad nunca debe propagar
        logger.warning("No se pudo registrar el error en LangSmith", exc_info=True)


def log_external_error(
    err: ExternalServiceError, *, pr_url: str = "", node: str = ""
) -> None:
    """
    Registra un error externo para trazabilidad.

    - Siempre lo escribe en el logging estándar (con el detalle técnico).
    - Si hay LANGSMITH_API_KEY, además lo envía a LangSmith.
    """
    logger.error(
        "external_error code=%s status=%s node=%s pr_url=%s detail=%s",
        err.error_code,
        err.status_code,
        node or "-",
        pr_url or "-",
        err.technical_detail or "-",
    )

    if _langsmith_enabled():
        _log_to_langsmith(err, pr_url=pr_url, node=node)
