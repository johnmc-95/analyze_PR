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
  // Controla qué vista del análisis se muestra en cada momento.
  const [url, setUrl] = useState('')
  const [estadoAnalisis, setEstadoAnalisis] = useState(ESTADOS.INICIAL)
  const [error, setError] = useState('')
  // Mensaje del error del análisis (RF-08). Es independiente de `error`, que se
  // usa para la validación inline de la URL bajo el input del formulario.
  const [mensajeError, setMensajeError] = useState('')
  const [resultados, setResultados] = useState(null)

  const ejecutarAnalisis = async (urlValida) => {
    setError('')
    setMensajeError('')
    setEstadoAnalisis(ESTADOS.CARGANDO)

    try {
      const respuesta = await analizarPullRequest(urlValida)
      setResultados(respuesta)
      setEstadoAnalisis(ESTADOS.EXITO)
    } catch (e) {
      // Mostramos el mensaje claro que envía el backend (o el de fallo de red).
      setResultados(null)
      setMensajeError(e.message)
      setEstadoAnalisis(ESTADOS.ERROR)
    }
  }

  const reintentar = () => {
    setEstadoAnalisis(ESTADOS.INICIAL)
    setError('')
    setMensajeError('')
  }

  return (
    // Los valores entre corchetes conservan los colores y medidas del diseño original.
    <div className="flex min-h-screen flex-col bg-[radial-gradient(circle_at_50%_26%,rgba(232,135,30,.08),transparent_32%)] bg-[#0a0a0a] font-['Hanken_Grotesk'] text-[#e5e2e1] antialiased">
      <header className="flex h-[72px] items-center justify-between border-b border-[#242322] bg-[rgba(14,14,14,.86)] px-[clamp(20px,5vw,72px)] backdrop-blur-xl">
        <a className="flex items-center gap-[11px] text-[17px] font-bold tracking-[-.01em] text-[#f2efed] no-underline outline-[#ffb77a] outline-offset-3" href="#principal" aria-label="Ir al analizador">
          <span className="grid size-[31px] place-items-center rounded-sm border border-[#e8871e] font-['JetBrains_Mono'] text-[10px] font-bold text-[#ffb77a] shadow-[inset_0_0_12px_rgba(232,135,30,.12)]" aria-hidden="true">DQ</span>
          <span>DataQuantum</span>
        </a>
        <span className="hidden font-['JetBrains_Mono'] text-[10px] font-semibold tracking-[.12em] text-[#8d8985] uppercase min-[701px]:inline">Analizador de Pull Requests</span>
      </header>

      <main id="principal" className="mx-auto w-[calc(100%_-_28px)] max-w-[1060px] flex-1 pt-[52px] pb-[72px] min-[701px]:w-[calc(100%_-_40px)] min-[701px]:pt-[clamp(64px,9vh,104px)]">
        <section className="mx-auto mb-[34px] max-w-[760px] text-center min-[701px]:mb-11" aria-labelledby="titulo-principal">
          <div className="inline-flex items-center gap-[9px] rounded-full border border-[#2d2b29] px-3 py-[7px] font-['JetBrains_Mono'] text-[10px] font-semibold tracking-[.08em] text-[#aaa5a0] uppercase">
            <span className="size-1.5 rounded-full bg-[#ffb77a] shadow-[0_0_10px_#e8871e]" /> Revisión inteligente de código
          </div>
          <h1 id="titulo-principal" className="my-[22px] mt-[25px] text-[clamp(43px,14vw,60px)] leading-[.99] font-bold tracking-[-.055em] text-[#f1efed] min-[701px]:text-[clamp(48px,7vw,76px)]">
            Analiza antes de<br />
            <span className="text-[#e8871e]">fusionar.</span>
          </h1>
          <p className="mx-auto max-w-[590px] text-[17px] leading-[1.65] text-[#9a9692]">Detecta riesgos, vulnerabilidades y oportunidades de mejora en cualquier Pull Request de GitHub.</p>
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

        <div className="mx-auto max-w-[880px]" aria-live="polite">
          {estadoAnalisis === ESTADOS.INICIAL && <EstadoInicial />}
          {estadoAnalisis === ESTADOS.CARGANDO && <EstadoCarga />}
          {estadoAnalisis === ESTADOS.EXITO && <EstadoExito resultados={resultados} />}
          {estadoAnalisis === ESTADOS.ERROR && (
            <EstadoError mensaje={mensajeError} onReintentar={reintentar} />
          )}
        </div>
      </main>

      <footer className="flex justify-center border-t border-[#242322] px-[clamp(20px,5vw,72px)] py-5 text-[11px] text-[#5f5b58] min-[701px]:justify-between">
        <span className="hidden min-[701px]:inline">Hecho para revisiones más seguras.</span>
        <span className="font-['JetBrains_Mono'] tracking-[.07em] uppercase"><i className="mr-1.5 inline-block size-1.5 rounded-full bg-[#8fba78] shadow-[0_0_8px_rgba(143,186,120,.6)]" /> Sistema disponible</span>
      </footer>
    </div>
  )
}

export default App
