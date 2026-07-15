function EstadoCarga() {
  return (
    <section className="mt-[38px] rounded-lg border border-[#2a2928] bg-[#121212] p-7" aria-label="Análisis en curso">
      <div className="flex items-center gap-[22px]">
        <div className="relative grid size-[52px] shrink-0 animate-spin place-items-center rounded-full border border-[#51402f] before:absolute before:size-[7px] before:-translate-y-[26px] before:rounded-full before:bg-[#ffb77a] before:shadow-[0_0_12px_#e8871e]"><span className="size-[13px] rotate-45 bg-[#e8871e]" /></div>
        <div>
          <span className="font-['JetBrains_Mono'] text-[10px] font-semibold tracking-[.12em] text-[#8d8985] uppercase">ANÁLISIS EN CURSO</span>
          <h2 className="my-1 text-[22px] font-bold">Inspeccionando el código</h2>
          <p className="m-0 text-sm leading-normal text-[#898580]">Estamos analizando el Pull Request. Esto puede tardar unos segundos.</p>
        </div>
      </div>
      <div className="my-[25px] h-0.5 overflow-hidden bg-[#292725]"><span className="block h-full w-[38%] animate-pulse bg-[#e8871e]" /></div>
      {/* Los esqueletos anticipan la distribución de las tarjetas mientras llega la respuesta. */}
      <div className="grid grid-cols-1 gap-3 min-[701px]:grid-cols-3">
        {[1, 2, 3].map((item) => (
          <div className="rounded-[5px] border border-[#282624] p-[15px]" key={item}>
            <i className="mb-4 block h-2 w-[28%] animate-pulse rounded-[3px] bg-[#4a3625]" />
            <span className="mt-2 block h-2 w-[88%] animate-pulse rounded-[3px] bg-[#2a2826]" />
            <span className="mt-2 block h-2 w-[56%] animate-pulse rounded-[3px] bg-[#2a2826]" />
          </div>
        ))}
      </div>
    </section>
  )
}

export default EstadoCarga
