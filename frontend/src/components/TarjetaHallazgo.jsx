// Relaciona cada severidad con su color sin depender de clases CSS personalizadas.
const ESTILOS_SEVERIDAD = {
  Crítica: 'border-[#e8871e] bg-[#e8871e] text-[#261606]',
  Alta: 'border-current text-[#ffb77a]',
  Media: 'border-current text-[#edc76b]',
  Baja: 'border-current text-[#b4cea5]',
}

function TarjetaHallazgo({ hallazgo }) {
  // Usa el estilo de baja severidad si llega un valor no reconocido.
  const estiloSeveridad = ESTILOS_SEVERIDAD[hallazgo.severidad] ?? ESTILOS_SEVERIDAD.Baja

  return (
    <article className="overflow-hidden rounded-[7px] border border-[#2c2a28] bg-[#131313]">
      <div className="flex items-center gap-3.5 border-b border-[#292725] bg-[#181717] px-[15px] py-2.5">
        <span className={`min-w-[61px] rounded-sm border px-[7px] py-1 text-center font-['JetBrains_Mono'] text-[9px] font-bold tracking-[.08em] uppercase ${estiloSeveridad}`}>{hallazgo.severidad}</span>
        <span className="[overflow-wrap:anywhere] font-['JetBrains_Mono'] text-[11px] font-medium text-[#8d8985]">{hallazgo.archivo}:{hallazgo.linea}</span>
      </div>
      <div className="p-[18px]">
        <h3 className="mt-0 mb-[15px] text-lg font-bold">{hallazgo.titulo}</h3>
        <div className="flex items-start gap-3 border-l-2 border-[#50402f] bg-[#0e0e0e] px-3.5 py-3 text-[#a39e99]">
          <span className="text-[#e8871e]" aria-hidden="true">↳</span>
          <p className="m-0 text-[13px] leading-[1.55]"><b className="mb-[3px] block font-['JetBrains_Mono'] text-[9px] font-semibold tracking-[.07em] text-[#c7c2bd] uppercase">Recomendación</b>{hallazgo.recomendacion}</p>
        </div>
      </div>
    </article>
  )
}

export default TarjetaHallazgo
