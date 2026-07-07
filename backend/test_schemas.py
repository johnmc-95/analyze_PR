import pytest
from pydantic import ValidationError
from schemas import ReviewRequest, Finding, Summary, Metadata, ReviewResponse

def test_review_request_valid():
    """
    Asegura que el modelo ReviewRequest acepta URLs de GitHub válidas.
    Este modelo es la puerta de entrada de nuestro endpoint, por lo que 
    debemos confiar en que parsee URLs correctas sin arrojar excepción.
    """
    req = ReviewRequest(pr_url="https://github.com/owner/repo/pull/1")
    assert str(req.pr_url) == "https://github.com/owner/repo/pull/1"

def test_review_request_invalid_domain():
    """
    Verifica la restricción del dominio.
    Si se provee una URL de otro servidor (ej. example.com o Gitlab), 
    Pydantic debe rechazarla usando nuestra lógica personalizada.
    """
    with pytest.raises(ValidationError):
        ReviewRequest(pr_url="https://example.com/owner/repo/pull/1")

def test_review_request_invalid_path():
    """
    Comprueba que el validador de ReviewRequest sea estricto con el sub-path.
    Si se le pasa 'issues' en vez de 'pull', tiene que detenerse antes de 
    ejecutar ningún agente, ahorrando cuota (tokens) innecesaria.
    """
    with pytest.raises(ValidationError):
        ReviewRequest(pr_url="https://github.com/owner/repo/issues/1")

def test_finding_valid():
    """
    Test de la estructura Finding (el JSON base de hallazgos que devuelven los agentes).
    Comprueba que un set de datos estándar logre instanciar el modelo de manera exitosa.
    """
    finding = Finding(
        id="BUG-001",
        file_name="main.py",
        line_number=10,
        category="bug",
        severity="high",
        explanation="test explanation",
        bad_example="test bad",
        refactor_suggestion="test refactor",
        code_fix="test fix"
    )
    assert finding.id == "BUG-001"
    assert finding.category == "bug"
    assert finding.severity == "high"

def test_finding_invalid_category():
    """
    Comprueba la restricción Literal['bug', 'security', 'style'] del modelo Finding.
    Esta restricción existe para asegurar que los LLMs no inventen categorías 
    nuevas imprevistas y rompan el reporte del lado del frontend.
    """
    with pytest.raises(ValidationError):
        Finding(
            id="BUG-002",
            file_name="main.py",
            category="invalid_category",  # Debería levantar la ValidationError
            severity="high",
            explanation="test explanation",
            refactor_suggestion="test refactor"
        )

def test_finding_invalid_severity():
    """
    Verifica que la severidad solo pueda ser de las opciones permitidas
    ('critical', 'high', 'medium', 'low'). Al igual que las categorías,
    fuerza al agente a acatar un vocabulario cerrado y seguro.
    """
    with pytest.raises(ValidationError):
        Finding(
            id="BUG-003",
            file_name="main.py",
            category="bug",
            severity="extreme",  # Debería levantar la ValidationError
            explanation="test explanation",
            refactor_suggestion="test refactor"
        )

def test_review_response_valid():
    """
    Verifica que el modelo final ReviewResponse, que anida (Summary, Findings, Metadata),
    puede crearse sin problemas para devolverlo al cliente en la ruta POST /review/initiate.
    """
    summary = Summary(status="clean", total_issues=0, global_comment="Perfect")
    metadata = Metadata(model="test-model", files_processed=1, changed_lines=10)
    
    response = ReviewResponse(
        summary=summary,
        findings=[],
        metadata=metadata
    )
    
    assert response.summary.status == "clean"
    assert response.metadata.files_processed == 1
