const resultadosMock = {
  estado: 'Completado',
  repositorio: 'openai/example',
  pullRequest: '#42',
  archivosAnalizados: 8,
  hallazgosEncontrados: 4,
  nivelRiesgo: 'Medio',
  hallazgos: [
    { id: 'SEC-001', categoria: 'security', severidad: 'Crítica', explicacion: 'Posible exposición de token en el código fuente.', archivo: 'src/config/api.ts', linea: '24', recomendacion: 'Mover las credenciales a variables de entorno.', codigoMalo: 'const token = "secreto"', codigoCorregido: 'const token = import.meta.env.VITE_API_TOKEN' },
    { id: 'SEC-002', categoria: 'security', severidad: 'Alta', explicacion: 'La entrada se utiliza sin una validación suficiente.', archivo: 'src/services/pullRequestService.ts', linea: '58', recomendacion: 'Validar correctamente la URL antes de enviarla.', codigoMalo: 'fetch(url)', codigoCorregido: 'if (esUrlValida(url)) {\n  fetch(url)\n}' },
    { id: 'STYLE-001', categoria: 'style', severidad: 'Media', explicacion: 'La función concentra demasiadas responsabilidades.', archivo: 'src/components/FormularioAnalizador.jsx', linea: '112', recomendacion: 'Dividir la función en componentes más pequeños.', codigoMalo: null, codigoCorregido: null },
    { id: 'STYLE-002', categoria: 'style', severidad: 'Baja', explicacion: 'El nombre de la variable no comunica su propósito.', archivo: 'src/utils/parser.js', linea: '17', recomendacion: 'Usar un nombre más claro para mejorar la legibilidad.', codigoMalo: 'const x = parse(data)', codigoCorregido: 'const resultadoAnalisis = parse(data)' },
  ],
}

export default resultadosMock
