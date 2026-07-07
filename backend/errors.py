"""
Taxonomía de errores de servicios externos (RF-08).

Define una única excepción, ``ExternalServiceError``, y un conjunto de fábricas
que la construyen ya poblada con:

- ``status_code``: el código HTTP que debe devolver la API.
- ``error_code``: un código estable y legible por máquina (p. ej. 'PR_NOT_FOUND').
- ``user_message``: mensaje claro y seguro para un usuario NO técnico.
- ``technical_detail``: detalle interno (excepción real, cuerpo de la respuesta,
  etc.) que SOLO debe ir a logging/LangSmith y NUNCA a la respuesta HTTP.

Centralizar aquí los textos garantiza que ningún detalle técnico se filtre al
frontend y que los mensajes sean consistentes en todo el backend.
"""


class ExternalServiceError(Exception):
    """Error controlado proveniente de un servicio externo (GitHub o Groq)."""

    def __init__(
        self,
        *,
        status_code: int,
        error_code: str,
        user_message: str,
        technical_detail: str = "",
    ) -> None:
        # El mensaje de la excepción es el técnico, útil en logs y trazas.
        super().__init__(technical_detail or user_message)
        self.status_code = status_code
        self.error_code = error_code
        self.user_message = user_message
        self.technical_detail = technical_detail


# ── Validación de límites del MVP (RS-01 / RS-02) ────────────────────────────

def constraints_exceeded(
    user_message: str, technical_detail: str = ""
) -> ExternalServiceError:
    """
    Error de negocio cuando el PR supera los límites del MVP (RS-01/RS-02).

    Se modela como ExternalServiceError para que pase por la misma trazabilidad
    (logging/LangSmith) que el resto de errores (RF-08). Devuelve 422 porque es
    una restricción de la petición, no un fallo del servicio.
    """
    return ExternalServiceError(
        status_code=422,
        error_code="CONSTRAINTS_EXCEEDED",
        user_message=user_message,
        technical_detail=technical_detail,
    )


# ── GitHub ───────────────────────────────────────────────────────────────────

def github_pr_not_found(technical_detail: str = "") -> ExternalServiceError:
    return ExternalServiceError(
        status_code=404,
        error_code="PR_NOT_FOUND",
        user_message=(
            "No encontramos el Pull Request. Revisa que la URL sea correcta y "
            "que el repositorio sea público."
        ),
        technical_detail=technical_detail,
    )


def github_forbidden(technical_detail: str = "") -> ExternalServiceError:
    return ExternalServiceError(
        status_code=403,
        error_code="REPO_FORBIDDEN",
        user_message=(
            "No tenemos acceso al repositorio. Puede que sea privado o requiera "
            "permisos adicionales."
        ),
        technical_detail=technical_detail,
    )


def github_rate_limit(technical_detail: str = "") -> ExternalServiceError:
    return ExternalServiceError(
        status_code=429,
        error_code="GITHUB_RATE_LIMIT",
        user_message=(
            "GitHub ha limitado temporalmente las peticiones. Inténtalo de nuevo "
            "en unos minutos."
        ),
        technical_detail=technical_detail,
    )


def github_timeout(technical_detail: str = "") -> ExternalServiceError:
    return ExternalServiceError(
        status_code=504,
        error_code="GITHUB_TIMEOUT",
        user_message=(
            "GitHub tardó demasiado en responder. Inténtalo de nuevo en unos "
            "momentos."
        ),
        technical_detail=technical_detail,
    )


def github_unavailable(technical_detail: str = "") -> ExternalServiceError:
    return ExternalServiceError(
        status_code=502,
        error_code="GITHUB_UNAVAILABLE",
        user_message="No pudimos conectar con GitHub. Inténtalo de nuevo más tarde.",
        technical_detail=technical_detail,
    )


# ── Groq ─────────────────────────────────────────────────────────────────────

def groq_timeout(technical_detail: str = "") -> ExternalServiceError:
    return ExternalServiceError(
        status_code=504,
        error_code="GROQ_TIMEOUT",
        user_message=(
            "El servicio de análisis con IA tardó demasiado en responder. "
            "Inténtalo de nuevo."
        ),
        technical_detail=technical_detail,
    )


def groq_inference_error(technical_detail: str = "") -> ExternalServiceError:
    return ExternalServiceError(
        status_code=502,
        error_code="GROQ_INFERENCE_ERROR",
        user_message=(
            "El servicio de análisis con IA no está disponible ahora mismo. "
            "Inténtalo de nuevo en unos minutos."
        ),
        technical_detail=technical_detail,
    )


def groq_invalid_response(technical_detail: str = "") -> ExternalServiceError:
    return ExternalServiceError(
        status_code=502,
        error_code="GROQ_INVALID_RESPONSE",
        user_message=(
            "El servicio de análisis devolvió una respuesta inesperada. "
            "Inténtalo de nuevo."
        ),
        technical_detail=technical_detail,
    )
