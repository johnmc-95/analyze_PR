import os
import httpx
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

PR_URL = "https://github.com/maykmbs/code-review-dataquantum/pull/17"


# ── 1. Descargar el diff desde GitHub ────────────────────────────

def get_pr_diff(pr_url: str) -> str:
    parts = pr_url.rstrip("/").split("/")
    owner, repo, pr_number = parts[-4], parts[-3], parts[-1]

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff",
    }

    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    return response.text


# ── 2. Enviar el diff a Groq ──────────────────────────────────────

def analyze_with_groq(diff: str) -> str:
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
Eres un experto en revisión de código.

Analiza el siguiente diff de un Pull Request y detecta bugs, problemas de seguridad o malas prácticas.
Sé breve y directo. Responde en español.

Diff:
{diff[:3000]}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


# ── Main ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print(f"PR: {PR_URL}")
    print("=" * 60)

    print("\n[1] Descargando diff desde GitHub...")
    diff = get_pr_diff(PR_URL)
    print(f"    {len(diff.splitlines())} líneas descargadas")
    print("\n--- Primeras 20 líneas del diff ---")
    print("\n".join(diff.splitlines()[:20]))

    print("\n[2] Enviando diff a Groq (Llama 3.3 70B)...")
    analysis = analyze_with_groq(diff)

    print("\n--- Respuesta del modelo ---")
    print(analysis)
    print("=" * 60)
