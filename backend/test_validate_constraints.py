from graph import (
    LIMITE_ARCHIVOS,
    LIMITE_LINEAS,
    ReviewState,
    _contar_cambios,
    validate_constraints,
)


# ── Diffs de ejemplo en formato unified de GitHub ─────────────────────

def _diff_de_un_archivo(lineas_add: int, lineas_del: int) -> str:
    """Genera un diff de un único archivo con N líneas añadidas y M borradas."""
    cabecera = (
        "diff --git a/backend/main.py b/backend/main.py\n"
        "index 1111111..2222222 100644\n"
        "--- a/backend/main.py\n"
        "+++ b/backend/main.py\n"
        "@@ -1,3 +1,3 @@\n"
    )
    cuerpo = "".join(f"+linea nueva {i}\n" for i in range(lineas_add))
    cuerpo += "".join(f"-linea vieja {i}\n" for i in range(lineas_del))
    return cabecera + cuerpo


def _estado(raw_diff: str) -> ReviewState:
    return {
        "pr_url": "https://github.com/example/project/pull/1",
        "raw_diff": raw_diff,
        "files_count": 0,
        "changed_lines": 0,
        "bug_issues": [],
        "security_issues": [],
        "style_issues": [],
        "final_report": {},
        "status": "diff_downloaded",
        "error_message": None,
    }


# ── Tests de la función auxiliar _contar_cambios ──────────────────────

def test_contar_cambios_ignora_cabeceras():
    """Las líneas '+++' y '---' de cabecera no deben contarse como modificadas."""
    diff = _diff_de_un_archivo(lineas_add=3, lineas_del=2)
    files_count, changed_lines = _contar_cambios(diff)

    assert files_count == 1
    assert changed_lines == 5  # 3 añadidas + 2 borradas, sin contar +++/---


def test_contar_cambios_cuenta_varios_archivos():
    diff = _diff_de_un_archivo(2, 0) + _diff_de_un_archivo(1, 1)
    files_count, changed_lines = _contar_cambios(diff)

    assert files_count == 2
    assert changed_lines == 4


# ── Tests del nodo validate_constraints ───────────────────────────────

def test_validate_constraints_dentro_de_limites():
    """Un PR pequeño pasa la validación y guarda las métricas en el estado."""
    diff = _diff_de_un_archivo(lineas_add=10, lineas_del=5)
    result = validate_constraints(_estado(diff))

    assert result["status"] == "constraints_validated"
    assert result["files_count"] == 1
    assert result["changed_lines"] == 15
    assert "error_message" not in result


def test_validate_constraints_supera_limite_de_archivos():
    """Más de 5 archivos → error RS-01 y flujo detenido."""
    diff = "".join(_diff_de_un_archivo(1, 0) for _ in range(LIMITE_ARCHIVOS + 1))
    result = validate_constraints(_estado(diff))

    assert result["status"] == "error"
    assert result["files_count"] == LIMITE_ARCHIVOS + 1
    assert "RS-01" in result["error_message"]


def test_validate_constraints_supera_limite_de_lineas():
    """Más de 1000 líneas → error RS-02 y flujo detenido."""
    diff = _diff_de_un_archivo(lineas_add=LIMITE_LINEAS + 1, lineas_del=0)
    result = validate_constraints(_estado(diff))

    assert result["status"] == "error"
    assert result["changed_lines"] == LIMITE_LINEAS + 1
    assert "RS-02" in result["error_message"]


def test_validate_constraints_en_el_limite_exacto_pasa():
    """Exactamente 5 archivos y 1000 líneas están permitidos (se supera con > )."""
    diff = "".join(_diff_de_un_archivo(200, 0) for _ in range(LIMITE_ARCHIVOS))
    result = validate_constraints(_estado(diff))

    assert result["files_count"] == LIMITE_ARCHIVOS
    assert result["changed_lines"] == LIMITE_LINEAS
    assert result["status"] == "constraints_validated"


def test_validate_constraints_respeta_error_previo():
    """Si ya había un error (fallo de descarga), el nodo no hace nada."""
    estado = _estado("")
    estado["status"] = "error"
    estado["error_message"] = "Error previo de descarga"

    result = validate_constraints(estado)

    assert result == {}
