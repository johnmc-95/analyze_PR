import resultadosMock from '../data/resultadosMock'

// Sustituir esta función por la llamada HTTP al backend cuando esté disponible.
export function analizarPullRequest(url) {
  return new Promise((resolve, reject) => {
    window.setTimeout(() => {
      if (url.toLowerCase().includes('error')) {
        reject(new Error('No se pudo completar el análisis.'))
        return
      }
      resolve(resultadosMock)
    }, 1600)
  })
}
