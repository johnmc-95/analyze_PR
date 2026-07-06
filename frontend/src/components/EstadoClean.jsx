function EstadoClean({ resultados }) {
  const metricas = [
    ['Repositorio', resultados.repositorio],
    ['Pull Request', resultados.pullRequest],
    ['Archivos analizados', resultados.archivosAnalizados],
    ['Hallazgos encontrados', resultados.hallazgosEncontrados],
  ]

  return (
    <section className="mt-[58px]">
      <div className="mb-[18px] flex items-start justify-between gap-5 min-[701px]:items-end">
        <div>
          <span className="font-['JetBrains_Mono'] text-[10px] font-semibold tracking-[.1em] text-[#b4cea5] uppercase">
            <i className="mr-1.5 inline-block size-1.5 rounded-full bg-[#8fba78] shadow-[0_0_8px_rgba(143,186,120,.6)]" />{' '}
            Análisis completado
          </span>
          <h2 className="mt-[7px] mb-0 text-[28px] font-bold tracking-[-.02em]">Resultados del análisis</h2>
        </div>
      </div>

      <div className="mb-10 overflow-hidden rounded-[16px] border border-[#2a3a28] bg-[rgba(143,186,120,.04)] p-10 text-center">
        <div className="mx-auto mb-5 grid size-[72px] place-items-center rounded-full border-2 border-[#8fba78] bg-[rgba(143,186,120,.08)] shadow-[0_0_30px_rgba(143,186,120,.15)]">
          <svg className="w-[32px] text-[#8fba78]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
        <h3 className="mt-0 mb-3 text-[26px] font-bold tracking-[-.02em] text-[#f1efed]">¡Buen trabajo! Código limpio.</h3>
        <p className="mx-auto mb-0 max-w-[520px] text-[15px] leading-[1.6] text-[#b4cea5]">{resultados.mensajeIA}</p>
      </div>

      <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-[7px] border border-[#2c2a28] bg-[#2c2a28] min-[701px]:grid-cols-4">
        {metricas.map(([titulo, valor]) => (
          <div className="bg-[#121212] p-[18px]" key={titulo}>
            <dt className="mb-2 font-['JetBrains_Mono'] text-[10px] font-semibold tracking-[.06em] text-[#77726e] uppercase">{titulo}</dt>
            <dd className="m-0 font-['JetBrains_Mono'] text-sm font-semibold text-[#dedad6]">{valor}</dd>
          </div>
        ))}
      </dl>
    </section>
  )
}

export default EstadoClean
