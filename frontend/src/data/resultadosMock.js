const resultadosMock = {
  estado: 'Completado',
  repositorio: 'openai/example',
  pullRequest: '#42',
  archivosAnalizados: 8,
  hallazgosEncontrados: 5,
  nivelRiesgo: 'Medio',
  hallazgos: [
    { severidad: 'Crítica', titulo: 'Posible exposición de token', archivo: 'src/config/api.ts', linea: '24', recomendacion: 'Mover las credenciales a variables de entorno.' },
    { severidad: 'Alta', titulo: 'Validación insuficiente de entrada', archivo: 'src/services/pullRequestService.ts', linea: '58', recomendacion: 'Validar correctamente la URL antes de enviarla.' },
    { severidad: 'Media', titulo: 'Función demasiado larga', archivo: 'src/components/FormularioAnalizador.jsx', linea: '112', recomendacion: 'Dividir la función en componentes más pequeños.' },
    { severidad: 'Baja', titulo: 'Nombre de variable poco descriptivo', archivo: 'src/utils/parser.js', linea: '17', recomendacion: 'Usar un nombre más claro para mejorar la legibilidad.' },
  ],
}

export default resultadosMock
