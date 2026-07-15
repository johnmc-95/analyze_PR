import json
import os
import sys
from dotenv import load_dotenv

# Cargar el archivo .env ubicado en la raíz del proyecto
load_dotenv()

# Añadir el directorio 'backend' al sys.path para que los módulos importados se encuentren correctamente
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

from graph import review_graph


def run_verification():
    print("=" * 70)
    print("VERIFICACIÓN DEL AGENTE DE BUGS CON EL GRAFO DE LANGGRAPH")
    print("=" * 70)

    # Definir la URL de PR utilizada por demo.py
    pr_url = "https://github.com/maykmbs/code-review-dataquantum/pull/17"
    print(f"[1] Iniciando revisión para el Pull Request: {pr_url}")

    # Inicializar el estado de revisión siguiendo el esquema ReviewState
    initial_state = {
        "pr_url": pr_url,
        "raw_diff": "",
        "files_count": 0,
        "changed_lines": 0,
        "bug_issues": [],
        "security_issues": [],
        "style_issues": [],
        "final_report": {},
        "status": "init",
        "error_message": None
    }

    print("[2] Ejecutando el grafo de LangGraph...")
    try:
        # Invocar el grafo compiled. Esto ejecutará secuencialmente:
        # START -> download_diff -> validate_constraints -> [bug_analysis, security_analysis, style_analysis] -> consolidation -> END
        result_state = review_graph.invoke(initial_state)
    except Exception as e:
        print(f"\n❌ Error al ejecutar el grafo: {str(e)}")
        return

    # Verificar si hubo algún error registrado durante la ejecución de los nodos
    if result_state.get("error_message"):
        print(f"\n❌ Error registrado en el estado: {result_state['error_message']}")
        return

    print("\n[3] Grafo completado exitosamente!")
    print(f"    Estado final del flujo: {result_state['status']}")
    print(f"    Líneas de diff procesadas: {len(result_state.get('raw_diff', '').splitlines())}")
    
    # Extraer y mostrar los hallazgos del agente de bugs
    bug_issues = result_state.get("bug_issues", [])
    print(f"\n--- Hallazgos del Agente de Bugs ({len(bug_issues)} detectados) ---")
    
    if not bug_issues:
        print("¡El agente de bugs no detectó ningún problema de lógica, bugs o rendimiento!")
    else:
        for idx, issue in enumerate(bug_issues, 1):
            print(f"\n🐞 Bug #{idx} [{issue['id']}] - Severidad: {issue['severity'].upper()}")
            print(f"   Archivo: {issue['file_name']} (Línea {issue['line_number']})")
            print(f"   Explicación: {issue['explanation']}")
            if issue.get('bad_example'):
                print(f"   Código problemático:\n   >>> {issue['bad_example']}")
            print(f"   Propuesta de corrección: {issue['refactor_suggestion']}")
            if issue.get('code_fix'):
                print(f"   Código corregido:\n{issue['code_fix']}")
            print("-" * 50)
            
    print("\n" + "=" * 70)


if __name__ == "__main__":
    run_verification()
