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
      id: f.id,
      categoria: f.category,
      severidad: SEVERIDAD_MAP[f.severity] ?? 'Baja',
      explicacion: f.explanation,
      archivo: f.file_name,
      linea: f.line_number?.toString() ?? 'N/A',
      recomendacion: f.refactor_suggestion,
      codigoMalo: f.bad_example,
      codigoCorregido: f.code_fix,
    })),
  }
}

export async function analizarPullRequest(url) {
  let response
  try {
    response = await fetch(`${BACKEND_URL}/review/initiate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pr_url: url }),
    })
  } catch {
    // La promesa de fetch solo se rechaza ante fallos de red (backend caído,
    // sin conexión...). Mostramos un mensaje amigable en vez del error técnico.
    throw new Error(
      'No pudimos conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.',
    )
  }

  if (!response.ok) {
    // El backend devuelve en `detail` un mensaje claro y seguro para el usuario (RF-08).
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail ?? 'Error al analizar el Pull Request.')
  }

  const data = await response.json()
  return mapearRespuesta(data, url)
}
