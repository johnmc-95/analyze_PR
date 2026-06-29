from pydantic import BaseModel, HttpUrl
from typing import Literal


class ReviewRequest(BaseModel):
    pr_url: HttpUrl


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


class Summary(BaseModel):
    status: Literal["issues_found", "clean"]
    total_issues: int
    global_comment: str


class Metadata(BaseModel):
    model: str
    files_processed: int
    changed_lines: int


class ReviewResponse(BaseModel):
    summary: Summary
    findings: list[Finding]
    metadata: Metadata | None = None
