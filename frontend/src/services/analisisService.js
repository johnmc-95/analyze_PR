const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000'

const SEVERIDAD_MAP = {
  critical: 'Crítica',
  high: 'Alta',
  medium: 'Media',
  low: 'Baja',
}

const RIESGO_MAP = {
  critical: 'Crítico',
  high: 'Alto',
  medium: 'Medio',
  low: 'Bajo',
}

function extraerInfoPR(url) {
  const match = url.match(/github\.com\/([^/]+\/[^/]+)\/pull\/(\d+)/)
  if (!match) return { repositorio: url, pullRequest: '#?' }
  return { repositorio: match[1], pullRequest: `#${match[2]}` }
}

function nivelRiesgoGlobal(findings) {
  const prioridad = ['critical', 'high', 'medium', 'low']
  for (const nivel of prioridad) {
    if (findings.some((f) => f.severity === nivel)) return RIESGO_MAP[nivel]
  }
  return 'Ninguno'
}

function mapearRespuesta(data, url) {
  const { repositorio, pullRequest } = extraerInfoPR(url)
  const findings = data.findings ?? []
  const estadoAnalisis = data.summary?.status ?? 'issues_found'

  return {
    estado: estadoAnalisis === 'clean' ? 'Limpio' : 'Completado',
    estadoAnalisis,
    repositorio,
    pullRequest,
    mensajeIA: data.summary?.global_comment ?? '',
    archivosAnalizados: data.metadata?.files_processed ?? 0,
    hallazgosEncontrados: data.summary?.total_issues ?? findings.length,
    nivelRiesgo: nivelRiesgoGlobal(findings),
    hallazgos: findings.map((f) => ({
      severidad: SEVERIDAD_MAP[f.severity] ?? 'Baja',
      titulo: f.explanation,
      archivo: f.file_name,
      linea: f.line_number?.toString() ?? 'N/A',
      recomendacion: f.refactor_suggestion,
    })),
  }
}

export async function analizarPullRequest(url) {
  const response = await fetch(`${BACKEND_URL}/review/initiate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pr_url: url }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail ?? 'Error al analizar el Pull Request.')
  }

  const data = await response.json()
  return mapearRespuesta(data, url)
}
