function EstadoCarga() {
  return (
    <section className="carga" aria-label="Análisis en curso">
      <div className="carga__cabecera">
        <div className="carga__orbita"><span /></div>
        <div>
          <span className="mono">ANÁLISIS EN CURSO</span>
          <h2>Inspeccionando el código</h2>
          <p>Estamos analizando el Pull Request. Esto puede tardar unos segundos.</p>
        </div>
      </div>
      <div className="carga__progreso"><span /></div>
      <div className="carga__esqueletos">
        {[1, 2, 3].map((item) => <div className="esqueleto" key={item}><i /><span /><span /></div>)}
      </div>
    </section>
  )
}

export default EstadoCarga
