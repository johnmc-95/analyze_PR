const PATRON_PULL_REQUEST = /^https:\/\/github\.com\/[^/\s]+\/[^/\s]+\/pull\/\d+(?:[/?#].*)?$/i

function validarUrl(url) {
  const valor = url.trim()
  if (!valor) return 'Introduce una URL antes de continuar.'
  if (!valor.startsWith('https://github.com')) return 'La URL debe empezar por https://github.com'
  if (!PATRON_PULL_REQUEST.test(valor)) return 'Introduce una URL válida de un Pull Request de GitHub.'
  return ''
}

function FormularioAnalizador({ url, onUrlChange, onSubmit, cargando, error, setError }) {
  const enviar = (evento) => {
    evento.preventDefault()
    const mensaje = validarUrl(url)
    setError(mensaje)
    if (!mensaje) onSubmit(url.trim())
  }

  return (
    <form className="formulario" onSubmit={enviar} noValidate>
      <label htmlFor="url-pull-request">URL del Pull Request</label>
      <div className={`formulario__control${error ? ' formulario__control--error' : ''}`}>
        <span className="formulario__github" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M12 .8a11.5 11.5 0 0 0-3.64 22.4c.58.11.79-.25.79-.56v-2.23c-3.22.7-3.9-1.37-3.9-1.37-.52-1.34-1.28-1.7-1.28-1.7-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.74-1.55-2.57-.29-5.27-1.28-5.27-5.68 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.47.11-3.05 0 0 .97-.31 3.16 1.18a10.9 10.9 0 0 1 5.76 0c2.2-1.49 3.16-1.18 3.16-1.18.63 1.58.23 2.76.11 3.05.74.81 1.19 1.83 1.19 3.09 0 4.41-2.71 5.38-5.29 5.67.42.36.79 1.06.79 2.15v3.19c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .8Z" /></svg>
        </span>
        <input
          id="url-pull-request"
          type="url"
          value={url}
          onChange={(evento) => onUrlChange(evento.target.value)}
          placeholder="https://github.com/usuario/repositorio/pull/123"
          disabled={cargando}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? 'error-url' : 'ayuda-url'}
          autoComplete="url"
        />
        <button type="submit" disabled={cargando}>
          {cargando ? <span className="boton__spinner" aria-hidden="true" /> : <span aria-hidden="true">✦</span>}
          {cargando ? 'Analizando...' : 'Analizar'}
        </button>
      </div>
      {error ? (
        <p id="error-url" className="formulario__error" role="alert"><span aria-hidden="true">!</span>{error}</p>
      ) : (
        <p id="ayuda-url" className="formulario__ayuda">El repositorio debe ser público para realizar el análisis.</p>
      )}
    </form>
  )
}

export default FormularioAnalizador
