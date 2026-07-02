function EstadoError({ onReintentar }) {
  return (
    <section className="error-analisis" role="alert">
      <div className="error-analisis__icono" aria-hidden="true">!</div>
      <div className="error-analisis__contenido">
        <span className="mono">ANÁLISIS INTERRUMPIDO</span>
        <h2>No se pudo completar el análisis.</h2>
        <p>El backend no respondió correctamente o la URL no es válida. Revisa la información e inténtalo de nuevo.</p>
      </div>
      <button type="button" className="boton-secundario" onClick={onReintentar}>↻ Reintentar</button>
    </section>
  )
}

export default EstadoError
