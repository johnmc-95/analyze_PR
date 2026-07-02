import { useState } from 'react'
import FormularioAnalizador from './components/FormularioAnalizador'
import EstadoInicial from './components/EstadoInicial'
import EstadoCarga from './components/EstadoCarga'
import EstadoExito from './components/EstadoExito'
import EstadoError from './components/EstadoError'
import { analizarPullRequest } from './services/analisisService'

const ESTADOS = {
  INICIAL: 'inicial',
  CARGANDO: 'cargando',
  EXITO: 'exito',
  ERROR: 'error',
}

function App() {
  const [url, setUrl] = useState('')
  const [estadoAnalisis, setEstadoAnalisis] = useState(ESTADOS.INICIAL)
  const [error, setError] = useState('')
  const [resultados, setResultados] = useState(null)

  const ejecutarAnalisis = async (urlValida) => {
    setError('')
    setEstadoAnalisis(ESTADOS.CARGANDO)

    try {
      const respuesta = await analizarPullRequest(urlValida)
      setResultados(respuesta)
      setEstadoAnalisis(ESTADOS.EXITO)
    } catch {
      setResultados(null)
      setEstadoAnalisis(ESTADOS.ERROR)
    }
  }

  const reintentar = () => {
    setEstadoAnalisis(ESTADOS.INICIAL)
    setError('')
  }

  return (
    <div className="aplicacion">
      <header className="cabecera">
        <a className="marca" href="#principal" aria-label="Ir al analizador">
          <span className="marca__simbolo" aria-hidden="true">DQ</span>
          <span>DataQuantum</span>
        </a>
        <span className="cabecera__etiqueta">Analizador de Pull Requests</span>
      </header>

      <main id="principal" className={`principal principal--${estadoAnalisis}`}>
        <section className="presentacion" aria-labelledby="titulo-principal">
          <div className="presentacion__etiqueta">
            <span className="presentacion__punto" /> Revisión inteligente de código
          </div>
          <h1 id="titulo-principal">
            Analiza antes de<br />
            <span>fusionar.</span>
          </h1>
          <p>Detecta riesgos, vulnerabilidades y oportunidades de mejora en cualquier Pull Request de GitHub.</p>
        </section>

        <FormularioAnalizador
          url={url}
          onUrlChange={(nuevoValor) => {
            setUrl(nuevoValor)
            if (error) setError('')
          }}
          onSubmit={ejecutarAnalisis}
          cargando={estadoAnalisis === ESTADOS.CARGANDO}
          error={error}
          setError={setError}
        />

        <div className="estado" aria-live="polite">
          {estadoAnalisis === ESTADOS.INICIAL && <EstadoInicial />}
          {estadoAnalisis === ESTADOS.CARGANDO && <EstadoCarga />}
          {estadoAnalisis === ESTADOS.EXITO && <EstadoExito resultados={resultados} />}
          {estadoAnalisis === ESTADOS.ERROR && <EstadoError onReintentar={reintentar} />}
        </div>
      </main>

      <footer className="pie">
        <span>Hecho para revisiones más seguras.</span>
        <span className="pie__estado"><i /> Sistema disponible</span>
      </footer>
    </div>
  )
}

export default App
