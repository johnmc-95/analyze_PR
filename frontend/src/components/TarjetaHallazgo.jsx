function TarjetaHallazgo({ hallazgo }) {
  const clase = hallazgo.severidad.toLowerCase().replace('í', 'i')
  return (
    <article className={`hallazgo hallazgo--${clase}`}>
      <div className="hallazgo__cabecera">
        <span className="insignia">{hallazgo.severidad}</span>
        <span className="hallazgo__ruta">{hallazgo.archivo}:{hallazgo.linea}</span>
      </div>
      <div className="hallazgo__cuerpo">
        <h3>{hallazgo.titulo}</h3>
        <div className="hallazgo__recomendacion">
          <span aria-hidden="true">↳</span>
          <p><b>Recomendación</b>{hallazgo.recomendacion}</p>
        </div>
      </div>
    </article>
  )
}

export default TarjetaHallazgo
