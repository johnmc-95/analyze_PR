# Frontend — AI Code Review Agent

Interfaz web construida con React + Vite + Tailwind CSS para visualizar los resultados del análisis de Pull Requests.

---

## Requisitos

- Node.js 18 o superior
- El backend corriendo en `http://localhost:8000`

---

## Instalación

### 1. Instalar dependencias

```bash
npm install
```

### 2. Configurar variables de entorno

Crea un archivo `.env.local` en la carpeta `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

---

## Levantar el servidor de desarrollo

```bash
npm run dev
```

La aplicación quedará disponible en `http://localhost:5173`.

---

## Build de producción

```bash
npm run build
```

Los archivos compilados se generan en la carpeta `dist/`.
