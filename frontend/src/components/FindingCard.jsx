const ESTILOS_SEVERIDAD = {
  Crítica: 'border-[#ef5b5b] bg-[#ef5b5b]/15 text-[#ff8b8b]',
  Alta: 'border-[#ff874d] bg-[#ff874d]/10 text-[#ff9d6c]',
  Media: 'border-[#e8b84a] bg-[#e8b84a]/10 text-[#f2cb70]',
  Baja: 'border-[#68c78f] bg-[#68c78f]/10 text-[#8cdaa9]',
}

const CATEGORIAS = {
  bug: 'Error lógico',
  security: 'Seguridad',
  style: 'Calidad y estilo',
}

const PATRON_SINTAXIS = /(\/\/.*$|#.*$|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b(?:const|let|var|function|return|if|else|for|while|async|await|import|from|def|class|True|False|None|null|true|false)\b|\b\d+(?:\.\d+)?\b)/g

function ResaltarLinea({ linea }) {
  return linea.split(PATRON_SINTAXIS).filter(Boolean).map((fragmento, indice) => {
    let color = ''
    if (/^(\/\/|#)/.test(fragmento)) color = 'text-[#77736f] italic'
    else if (/^["']/.test(fragmento)) color = 'text-[#b4cea5]'
    else if (/^\d/.test(fragmento)) color = 'text-[#83cfff]'
    else if (/^(const|let|var|function|return|if|else|for|while|async|await|import|from|def|class|True|False|None|null|true|false)$/.test(fragmento)) color = 'text-[#ffb77a]'

    return <span className={color} key={`${indice}-${fragmento}`}>{fragmento}</span>
  })
}

function BloqueCodigo({ titulo, codigo, tipo }) {
  if (!codigo) return null

  return (
    <div>
      <h4 className="mb-2 font-['JetBrains_Mono'] text-[9px] font-semibold tracking-[.08em] text-[#8d8985] uppercase">
        {titulo}
      </h4>
      <pre className="m-0 overflow-x-auto rounded-sm border border-[#292725] bg-[#0a0a0a] p-3 font-['JetBrains_Mono'] text-xs leading-5 text-[#c7c2bd]">
        <code>
          {codigo.split('\n').map((linea, indice) => (
            <span
              className={`block min-w-max px-2 ${tipo === 'error' ? 'bg-[#ef5b5b]/8 text-[#ffaaa4]' : 'bg-[#68c78f]/8 text-[#a9dfba]'}`}
              key={`${indice}-${linea}`}
            >
              <span className="mr-3 inline-block w-5 select-none text-right text-[#57534f]">{indice + 1}</span>
              {linea ? <ResaltarLinea linea={linea} /> : ' '}
            </span>
          ))}
        </code>
      </pre>
    </div>
  )
}

function FindingCard({ hallazgo }) {
  const estiloSeveridad = ESTILOS_SEVERIDAD[hallazgo.severidad] ?? ESTILOS_SEVERIDAD.Baja
  const categoria = CATEGORIAS[hallazgo.categoria] ?? hallazgo.categoria ?? 'Sin categoría'

  return (
    <article className="overflow-hidden rounded-[7px] border border-[#2c2a28] bg-[#131313]">
      <header className="flex flex-wrap items-center gap-2.5 border-b border-[#292725] bg-[#181717] px-[15px] py-2.5">
        <span className={`min-w-[61px] rounded-sm border px-[7px] py-1 text-center font-['JetBrains_Mono'] text-[9px] font-bold tracking-[.08em] uppercase ${estiloSeveridad}`}>
          {hallazgo.severidad}
        </span>
        <span className="rounded-sm border border-[#3a3734] px-2 py-1 font-['JetBrains_Mono'] text-[9px] font-semibold tracking-[.06em] text-[#aaa5a0] uppercase">
          {categoria}
        </span>
        <span className="min-w-0 flex-1 [overflow-wrap:anywhere] font-['JetBrains_Mono'] text-[11px] font-medium text-[#8d8985]">
          {hallazgo.archivo}:{hallazgo.linea}
        </span>
        {hallazgo.id && <span className="font-['JetBrains_Mono'] text-[9px] text-[#5f5b58]">{hallazgo.id}</span>}
      </header>

      <div className="grid gap-[18px] p-[18px]">
        <div>
          <h3 className="mt-0 mb-1.5 text-lg font-bold text-[#e5e2e1]">Explicación</h3>
          <p className="m-0 text-sm leading-6 text-[#aaa5a0]">{hallazgo.explicacion}</p>
        </div>

        <div className="grid gap-3 min-[760px]:grid-cols-2">
          <BloqueCodigo titulo="Código problemático" codigo={hallazgo.codigoMalo} tipo="error" />
          <BloqueCodigo titulo="Código corregido" codigo={hallazgo.codigoCorregido} tipo="solucion" />
        </div>

        <div className="flex items-start gap-3 border-l-2 border-[#e8871e] bg-[#0e0e0e] px-3.5 py-3 text-[#a39e99]">
          <span className="text-[#e8871e]" aria-hidden="true">↳</span>
          <p className="m-0 text-[13px] leading-[1.55]">
            <b className="mb-[3px] block font-['JetBrains_Mono'] text-[9px] font-semibold tracking-[.07em] text-[#c7c2bd] uppercase">Sugerencia de mejora</b>
            {hallazgo.recomendacion}
          </p>
        </div>
      </div>
    </article>
  )
}

export default FindingCard
