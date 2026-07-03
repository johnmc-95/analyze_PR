import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    // Permite que Vite transforme los componentes React durante el desarrollo.
    react(),
    // Procesa las clases de Tailwind usadas en JSX y genera solo el CSS necesario.
    tailwindcss(),
  ],
})
