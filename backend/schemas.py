from pydantic import BaseModel, HttpUrl, field_validator
from typing import Literal

# Validación de la pr_url 

class ReviewRequest(BaseModel):
    pr_url: HttpUrl

    @field_validator("pr_url")
    @classmethod
    def validate_github_pr_url(cls, value: HttpUrl) -> HttpUrl:
        """Comprueba que la URL recibida pertenece a un Pull Request de GitHub."""
        path_parts = [part for part in value.path.split("/") if part]
        is_pull_request_path = (
            len(path_parts) == 4
            and path_parts[2] == "pull"
            and path_parts[3].isdigit()
            and int(path_parts[3]) > 0
        )

        if (
            value.scheme != "https"
            or value.host not in {"github.com", "www.github.com"}
            or not is_pull_request_path
            or value.query is not None
            or value.fragment is not None
        ):
            raise ValueError(
                "La URL debe tener el formato "
                "https://github.com/{owner}/{repository}/pull/{number}"
            )

        return value

# Campos opcionales como None por defecto, Literal para categoría y seguridad 
class Finding(BaseModel):
    id: str
    file_name: str
    line_number: int | None = None
    category: Literal["bug", "security", "style"]
    severity: Literal["critical", "high", "medium", "low"]
    explanation: str
    bad_example: str | None = None
    refactor_suggestion: str
    code_fix: str | None = None

#  Estado (status) restringido a "issues_found" o "clean"
class Summary(BaseModel):
    status: Literal["issues_found", "clean"]
    total_issues: int
    global_comment: str

# Datos del modelo y del PR (PullRequest) procesado
class Metadata(BaseModel):
    model: str
    files_processed: int
    changed_lines: int

# Modelo raíz que agrupa todo, metadata es opcional para el caso de código limpio
class ReviewResponse(BaseModel):
    summary: Summary
    findings: list[Finding]
    metadata: Metadata | None = None
