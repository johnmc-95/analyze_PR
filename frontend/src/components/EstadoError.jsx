function EstadoError({ onReintentar }) {
  return (
    <section className="mt-[38px] grid grid-cols-[auto_1fr] items-center gap-5 rounded-[7px] border border-[#51302d] border-l-[3px] border-l-[#ffb4ab] bg-[rgba(147,0,10,.08)] p-[26px] min-[701px]:grid-cols-[auto_1fr_auto]" role="alert">
      <div className="grid size-[42px] place-items-center rounded-full border border-[#b55f58] font-['JetBrains_Mono'] text-lg font-bold text-[#ffb4ab]" aria-hidden="true">!</div>
      <div>
        <span className="font-['JetBrains_Mono'] text-[10px] font-semibold tracking-[.12em] text-[#d47d74] uppercase">ANÁLISIS INTERRUMPIDO</span>
        <h2 className="my-1 text-[22px] font-bold">No se pudo completar el análisis.</h2>
        <p className="m-0 text-sm leading-normal text-[#898580]">El backend no respondió correctamente o la URL no es válida. Revisa la información e inténtalo de nuevo.</p>
      </div>
      <button type="button" className="col-span-full cursor-pointer whitespace-nowrap rounded-sm border border-[#8f572a] bg-transparent px-4 py-[11px] font-semibold text-[#ffb77a] hover:bg-[rgba(232,135,30,.1)] min-[701px]:col-auto" onClick={onReintentar}>↻ Reintentar</button>
    </section>
  )
}

export default EstadoError
