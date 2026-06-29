from pydantic import BaseModel, HttpUrl
from typing import Literal

# Validación de la pr_url 

class ReviewRequest(BaseModel):
    pr_url: HttpUrl

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
