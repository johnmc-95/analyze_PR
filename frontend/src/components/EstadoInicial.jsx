function EstadoInicial() {
  return (
    <div className="estado-inicial">
      <div className="estado-inicial__linea" />
      <p>Introduce la URL de un Pull Request para comenzar el análisis.</p>
      <div className="estado-inicial__pasos" aria-label="Proceso de análisis">
        <span><b>01</b> Conecta</span><i />
        <span><b>02</b> Analiza</span><i />
        <span><b>03</b> Mejora</span>
      </div>
    </div>
  )
}

export default EstadoInicial
