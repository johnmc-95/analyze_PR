function EstadoInicial() {
  return (
    <div className="mt-12 text-center text-[#77736f]">
      <div className="h-px bg-gradient-to-r from-transparent via-[#302e2c] to-transparent" />
      <p className="my-[26px] mt-7 text-sm">Introduce la URL de un Pull Request para comenzar el análisis.</p>
      <div className="flex items-center justify-center gap-4 font-['JetBrains_Mono'] text-[10px] font-semibold tracking-[.08em] text-[#67635f] uppercase" aria-label="Proceso de análisis">
        <span className="flex items-center gap-[7px]"><b className="text-[#a05f22]">01</b> Conecta</span><i className="h-px w-3 bg-[#373432] min-[701px]:w-[38px]" />
        <span className="flex items-center gap-[7px]"><b className="text-[#a05f22]">02</b> Analiza</span><i className="h-px w-3 bg-[#373432] min-[701px]:w-[38px]" />
        <span className="flex items-center gap-[7px]"><b className="text-[#a05f22]">03</b> Mejora</span>
      </div>
    </div>
  )
}

export default EstadoInicial
