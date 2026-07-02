import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar encoding para evitar errores unicode en consola de Windows
sys.stdout.reconfigure(encoding='utf-8')

# Añadir el directorio 'backend' al sys.path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

from agents.bug_agent import analyze_bugs


def test_buggy_diff():
    print("=" * 70)
    print("PROBANDO EL AGENTE DE BUGS CON UN DIFF QUE CONTIENE ERRORES")
    print("=" * 70)

    # Diff simulado que contiene errores de lógica y rendimiento:
    # 1. División por cero potencial en calculate_average.
    # 2. Uso de una variable no definida 'x' en process_data.
    # 3. Rendimiento ineficiente: concatenación repetida de strings en un bucle grande en construct_report.
    buggy_diff = """diff --git a/utils.py b/utils.py
index 1234567..89abcde 100644
--- a/utils.py
+++ b/utils.py
@@ -10,5 +12,23 @@
 def calculate_average(numbers):
-    return sum(numbers) / len(numbers)
+    # Si la lista está vacía, esto lanzará un ZeroDivisionError
+    total = sum(numbers)
+    count = len(numbers)
+    return total / count
+
+def process_data(data):
+    for i in range(len(data)):
+        # Bug: Uso de la variable indefinida 'x' en lugar del índice 'i'
+        print(data[x])
+
+def construct_report(items):
+    report = ""
+    for item in items:
+        # Ineficiencia de rendimiento (O(N^2) concatenación de strings)
+        report += item + "\\n"
+    return report
"""

    print("Enviando diff con errores a Groq...")
    try:
        findings = analyze_bugs(buggy_diff)
    except Exception as e:
        print(f"❌ Error al ejecutar el agente: {str(e)}")
        return

    print(f"\n✅ ¡Respuesta recibida! Se detectaron {len(findings)} hallazgos.")

    for idx, issue in enumerate(findings, 1):
        print(f"\n🐞 Hallazgo #{idx} [{issue.id}] - Severidad: {issue.severity.upper()}")
        print(f"   Archivo: {issue.file_name} (Línea {issue.line_number})")
        print(f"   Explicación: {issue.explanation}")
        if issue.bad_example:
            print(f"   Código problemático:\n   >>> {issue.bad_example}")
        print(f"   Sugerencia de refactorización: {issue.refactor_suggestion}")
        if issue.code_fix:
            print(f"   Solución propuesta:\n{issue.code_fix}")
        print("-" * 60)

    print("=" * 70)


if __name__ == "__main__":
    test_buggy_diff()
