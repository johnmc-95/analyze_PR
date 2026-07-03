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
    <form className="mx-auto max-w-[880px]" onSubmit={enviar} noValidate>
      <label className="mb-2.5 ml-0.5 block font-['JetBrains_Mono'] text-[11px] font-semibold tracking-[.06em] text-[#cbc6c2] uppercase" htmlFor="url-pull-request">URL del Pull Request</label>
      {/* El borde cambia según la validación; desde 701 px el formulario queda en una sola fila. */}
      <div className={`flex min-h-[60px] flex-wrap items-stretch overflow-hidden rounded-[7px] border bg-[#151515] pt-[3px] transition-[border-color,box-shadow] focus-within:border-[#e8871e] focus-within:shadow-[0_0_0_3px_rgba(232,135,30,.1)] min-[701px]:flex-nowrap min-[701px]:pt-0 ${error ? 'border-[#e0776d]' : 'border-[#3a3836]'}`}>
        <span className="grid w-[45px] flex-[0_0_45px] place-items-center text-[#8e8985] min-[701px]:w-14 min-[701px]:flex-[0_0_56px]" aria-hidden="true">
          <svg className="w-[21px] fill-current" viewBox="0 0 24 24"><path d="M12 .8a11.5 11.5 0 0 0-3.64 22.4c.58.11.79-.25.79-.56v-2.23c-3.22.7-3.9-1.37-3.9-1.37-.52-1.34-1.28-1.7-1.28-1.7-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.74-1.55-2.57-.29-5.27-1.28-5.27-5.68 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.47.11-3.05 0 0 .97-.31 3.16 1.18a10.9 10.9 0 0 1 5.76 0c2.2-1.49 3.16-1.18 3.16-1.18.63 1.58.23 2.76.11 3.05.74.81 1.19 1.83 1.19 3.09 0 4.41-2.71 5.38-5.29 5.67.42.36.79 1.06.79 2.15v3.19c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .8Z" /></svg>
        </span>
        <input
          className="min-h-[50px] w-[calc(100%_-_45px)] min-w-0 flex-1 border-0 bg-transparent pr-4 font-['JetBrains_Mono'] text-xs font-medium text-[#f4f0ed] outline-none placeholder:text-[#65615e] disabled:cursor-wait min-[701px]:w-auto min-[701px]:text-sm"
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
        <button className="m-[7px] flex min-h-[46px] w-full min-w-[142px] cursor-pointer items-center justify-center gap-[9px] rounded-sm border-0 bg-[#e8871e] font-bold text-[#241507] transition-[background,transform] hover:not-disabled:-translate-y-px hover:not-disabled:bg-[#ffb77a] disabled:cursor-wait disabled:opacity-70 min-[701px]:w-auto" type="submit" disabled={cargando}>
          {cargando ? <span className="size-[15px] animate-spin rounded-full border-2 border-[rgba(36,21,7,.3)] border-t-[#241507]" aria-hidden="true" /> : <span aria-hidden="true">✦</span>}
          {cargando ? 'Analizando...' : 'Analizar'}
        </button>
      </div>
      {error ? (
        <p id="error-url" className="mx-0.5 mt-[9px] flex min-h-5 items-center gap-[7px] text-xs text-[#ffb4ab]" role="alert"><span className="grid size-4 place-items-center rounded-full border border-current font-['JetBrains_Mono'] text-[10px] font-bold" aria-hidden="true">!</span>{error}</p>
      ) : (
        <p id="ayuda-url" className="mx-0.5 mt-[9px] min-h-5 text-xs text-[#716d69]">El repositorio debe ser público para realizar el análisis.</p>
      )}
    </form>
  )
}

export default FormularioAnalizador
