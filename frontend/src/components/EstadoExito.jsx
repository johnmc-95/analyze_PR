import TarjetaHallazgo from './TarjetaHallazgo'
import EstadoClean from './EstadoClean'

function EstadoExito({ resultados }) {
  if (resultados.status === 'clean') {
    return <EstadoClean resultados={resultados} />
  }
  // Centraliza las métricas para renderizarlas con la misma estructura visual.
  const metricas = [
    ['Estado del análisis', `✓ ${resultados.estado}`, 'text-[#b4cea5]'],
    ['Repositorio', resultados.repositorio],
    ['Pull Request', resultados.pullRequest],
    ['Archivos analizados', resultados.archivosAnalizados],
    ['Hallazgos encontrados', resultados.hallazgosEncontrados],
    ['Nivel de riesgo', resultados.nivelRiesgo, 'text-[#edc76b]'],
  ]

  return (
    <section className="mt-[58px]">
      <div className="mb-[18px] flex items-start justify-between gap-5 min-[701px]:items-end">
        <div>
          <span className="font-['JetBrains_Mono'] text-[10px] font-semibold tracking-[.1em] text-[#b4cea5] uppercase"><i className="mr-1.5 inline-block size-1.5 rounded-full bg-[#8fba78] shadow-[0_0_8px_rgba(143,186,120,.6)]" /> Análisis completado</span>
          <h2 className="mt-[7px] mb-0 text-[28px] font-bold tracking-[-.02em]">Resultados del análisis</h2>
        </div>
        <span className="mt-[7px] font-['JetBrains_Mono'] text-[11px] font-semibold tracking-[.07em] text-[#8f8a86] uppercase min-[701px]:mt-0">Riesgo <b className="ml-[7px] rounded-[3px] border border-[#8d702d] px-[9px] py-1.5 text-[#edc76b]">{resultados.nivelRiesgo}</b></span>
      </div>

      <dl className="mb-[45px] grid grid-cols-2 gap-px overflow-hidden rounded-[7px] border border-[#2c2a28] bg-[#2c2a28] min-[701px]:grid-cols-3">
        {metricas.map(([titulo, valor, color]) => (
          <div className="bg-[#121212] p-[18px]" key={titulo}>
            <dt className="mb-2 font-['JetBrains_Mono'] text-[10px] font-semibold tracking-[.06em] text-[#77726e] uppercase">{titulo}</dt>
            <dd className={`m-0 font-['JetBrains_Mono'] text-sm font-semibold ${color ?? 'text-[#dedad6]'}`}>{valor}</dd>
          </div>
        ))}
      </dl>

      <div className="mb-[18px] flex items-end justify-between border-b border-[#2a2826] pb-[13px]">
        <h2 className="m-0 text-[22px] font-bold tracking-[-.02em]">Hallazgos</h2>
        <span className="font-['JetBrains_Mono'] text-[10px] font-medium text-[#716d69] uppercase">{resultados.hallazgos.length} elementos destacados</span>
      </div>
      <div className="grid gap-3">
        {resultados.hallazgos.map((hallazgo) => (
          <TarjetaHallazgo key={`${hallazgo.archivo}-${hallazgo.linea}-${hallazgo.titulo}`} hallazgo={hallazgo} />
        ))}
      </div>
    </section>
  )
}

export default EstadoExito
