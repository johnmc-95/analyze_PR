import TarjetaHallazgo from './TarjetaHallazgo'

function EstadoExito({ resultados }) {
  return (
    <section className="resultados">
      <div className="resultados__titulo">
        <div>
          <span className="resultados__completado"><i /> Análisis completado</span>
          <h2>Resultados del análisis</h2>
        </div>
        <span className="resultados__riesgo">Riesgo <b>{resultados.nivelRiesgo}</b></span>
      </div>

      <dl className="metricas">
        <div><dt>Estado del análisis</dt><dd className="texto-exito">✓ {resultados.estado}</dd></div>
        <div><dt>Repositorio</dt><dd>{resultados.repositorio}</dd></div>
        <div><dt>Pull Request</dt><dd>{resultados.pullRequest}</dd></div>
        <div><dt>Archivos analizados</dt><dd>{resultados.archivosAnalizados}</dd></div>
        <div><dt>Hallazgos encontrados</dt><dd>{resultados.hallazgosEncontrados}</dd></div>
        <div><dt>Nivel de riesgo</dt><dd className="texto-riesgo">{resultados.nivelRiesgo}</dd></div>
      </dl>

      <div className="resultados__subtitulo">
        <h2>Hallazgos</h2>
        <span>{resultados.hallazgos.length} elementos destacados</span>
      </div>
      <div className="hallazgos">
        {resultados.hallazgos.map((hallazgo) => <TarjetaHallazgo key={hallazgo.severidad} hallazgo={hallazgo} />)}
      </div>
    </section>
  )
}

export default EstadoExito
