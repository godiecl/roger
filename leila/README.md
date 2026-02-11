# Leila - Frontend Web

**LEI**tura **L**ibre de **I**mágenes **A**ntiguas

Interfaz web desarrollada con SvelteKit para el proyecto ROGER, que proporciona una experiencia interactiva para explorar, buscar y visualizar colecciones patrimoniales de fotografías históricas de Robert Gerstmann.

---

## Estado del Proyecto

**Versión:** 0.1.0
**Completado:** ~65%

### Funcionalidades Implementadas

- ✅ Autenticación completa (login, logout, registro)
- ✅ Gestión de sesiones con tokens JWT
- ✅ Sistema de renovación automática de tokens (30 min con actividad)
- ✅ Protección de rutas basada en roles
- ✅ Navegación responsive (Header, Footer, Layout)
- ✅ Galería de imágenes con grid adaptativo
- ✅ Visor de imágenes en modal con zoom
- ✅ Búsqueda avanzada con múltiples filtros
- ✅ Búsqueda semántica con IA
- ✅ Sistema de notificaciones (toasts con animaciones)
- ✅ Panel de desarrollo (debug de autenticación)
- ✅ Seguridad: rate limiting, sanitización de inputs, HTTPS enforcement
- ✅ Stores reactivos con Svelte
- ✅ UI moderna con DaisyUI

### Pendiente

- 🔲 Mapa interactivo con georreferenciación (Leaflet)
- 🔲 Líneas de tiempo paralelas
- 🔲 Panel de administración completo
- 🔲 Perfil de usuario con edición
- 🔲 Sistema de upload de imágenes
- 🔲 Gestión de colecciones
- 🔲 Comparador histórico "Antes/Ahora"
- 🔲 Exportación de resultados (PDF, Excel)
- 🔲 Tests E2E completos
- 🔲 PWA (modo offline)

---

## Requisitos

- Node.js 18 o superior
- npm o pnpm (gestor de paquetes)

---

## Instalación

### 1. Instalar dependencias

```bash
# Usando npm
npm install

# O usando pnpm (más rápido)
pnpm install
```

### 2. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env
```

Editar el archivo `.env` con la configuración necesaria:

```env
# URL del backend API
VITE_API_URL=http://localhost:8000/api/v1

# Configuración de la aplicación
VITE_APP_NAME=ROGER
VITE_APP_DESCRIPTION=Archivo Robert Gerstmann

# Feature flags
VITE_ENABLE_SEMANTIC_SEARCH=true
VITE_ENABLE_AI_NARRATIVES=true
```

---

## Ejecución

### Servidor de desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

### Build de producción

```bash
# Generar build optimizado
npm run build

# Previsualizar build de producción
npm run preview
```

### Otros comandos útiles

```bash
# Linting
npm run lint

# Formateo de código
npm run format

# Verificar tipos TypeScript
npm run check
```

---

## Testing

```bash
# Tests unitarios
npm run test

# Tests unitarios en modo watch
npm run test:watch

# Tests E2E
npm run test:e2e

# Coverage
npm run test:coverage
```

---

## Arquitectura

El proyecto utiliza una estructura modular con **SvelteKit**:

```
src/
├── routes/                 # Rutas de la aplicación (file-based routing)
│   ├── +page.svelte       # Página principal
│   ├── +layout.svelte     # Layout global
│   ├── login/             # Página de login
│   ├── gallery/           # Galería de imágenes
│   ├── profile/           # Perfil de usuario
│   └── admin/             # Panel de administración
│
├── lib/                   # Biblioteca compartida
│   ├── components/        # Componentes reutilizables
│   │   ├── common/        # Componentes comunes (Toast, Modal, etc.)
│   │   ├── layout/        # Componentes de layout (Header, Footer)
│   │   ├── auth/          # Componentes de autenticación
│   │   └── dev/           # Componentes de desarrollo (DevPanel)
│   │
│   ├── stores/            # Stores de Svelte
│   │   ├── auth.ts        # Estado de autenticación
│   │   ├── images.ts      # Estado de imágenes
│   │   ├── search.ts      # Estado de búsqueda
│   │   └── notifications.ts # Sistema de notificaciones
│   │
│   ├── services/          # Servicios y lógica de negocio
│   │   ├── api/           # Cliente API
│   │   ├── auth/          # Servicios de autenticación
│   │   ├── activityTracker.ts # Rastreo de actividad
│   │   └── tokenRefreshService.ts # Renovación de tokens
│   │
│   ├── utils/             # Utilidades
│   │   ├── auth.guard.ts  # Guards de rutas
│   │   ├── sanitize.ts    # Sanitización de inputs
│   │   ├── rateLimiter.ts # Rate limiting
│   │   └── token.utils.ts # Utilidades de tokens
│   │
│   └── config/            # Configuración
│       └── security.ts    # Configuración de seguridad
│
└── app.css                # Estilos globales
```

---

## Características de Seguridad

### Implementadas

- ✅ **Autenticación JWT**: Tokens con expiración de 30 minutos
- ✅ **Renovación automática**: Los tokens se renuevan si el usuario está activo
- ✅ **Rate Limiting**: Límites en login (5 intentos/15 min) y registro (3 intentos/hora)
- ✅ **Sanitización de inputs**: Prevención de XSS en formularios
- ✅ **Protección de rutas**: Guards basados en autenticación y roles
- ✅ **HTTPS enforcement**: Redirección automática a HTTPS en producción
- ✅ **Activity tracking**: Seguimiento de actividad del usuario (30 min timeout)
- ✅ **Session warnings**: Alertas de expiración de sesión

---

## Stores Reactivos

El proyecto utiliza stores de Svelte para gestión de estado:

### `authStore`
- Estado de autenticación del usuario
- Manejo de tokens (access + refresh)
- Operaciones: login, logout, updateTokens, updateUser

### `notificationsStore`
- Sistema de notificaciones toast
- Tipos: success, error, warning, info
- Auto-dismiss configurable

### `imagesStore`
- Estado de imágenes cargadas
- Operaciones: fetchImages, fetchImageById, etc.

### `searchStore`
- Estado de búsqueda y filtros
- Soporte para búsqueda semántica

---

## Componentes Principales

### Layout
- `Header.svelte` - Barra de navegación con autenticación
- `Footer.svelte` - Pie de página
- `Layout.svelte` - Layout principal con SessionWarning y DevPanel

### Common
- `Toast.svelte` - Sistema de notificaciones con animaciones
- `Modal.svelte` - Modal reutilizable
- `SessionWarning.svelte` - Advertencia de sesión próxima a expirar

### Dev
- `DevPanel.svelte` - Panel de debug para desarrollo (solo visible en modo dev)
  - Muestra estado de autenticación en tiempo real
  - Info de tokens y expiración
  - Estado de actividad del usuario
  - Acciones rápidas (logout, refresh)

---

## Tecnologías

- **Framework:** SvelteKit 2.0+
- **Lenguaje:** TypeScript 5.0+
- **UI Library:** DaisyUI 4.0+
- **CSS Framework:** Tailwind CSS 3.0+
- **HTTP Client:** Fetch API nativo
- **Validación:** Zod (pendiente integración completa)
- **Mapas:** Leaflet (pendiente integración)
- **Testing:** Vitest + Testing Library
- **Build Tool:** Vite 5.0+

---

## Variables de Entorno

### Requeridas

```env
VITE_API_URL=http://localhost:8000/api/v1  # URL del backend
```

### Opcionales

```env
# Configuración de la aplicación
VITE_APP_NAME=ROGER
VITE_APP_DESCRIPTION=Archivo Robert Gerstmann

# Feature flags
VITE_ENABLE_SEMANTIC_SEARCH=true
VITE_ENABLE_AI_NARRATIVES=true

# Analytics (opcional)
VITE_GOOGLE_ANALYTICS_ID=
VITE_MATOMO_URL=
VITE_MATOMO_SITE_ID=
```

---

## Credenciales de Prueba

Después de ejecutar el seed del backend:

| Rol | Email | Password |
|-----|-------|----------|
| Administrador | admin@roger.cl | admin123 |
| Curador | curador@roger.cl | curador123 |
| Investigador | investigador@roger.cl | investigador123 |
| Usuario | user@roger.cl | user123 |

---

## Modo Desarrollo

### DevPanel

En modo desarrollo (`npm run dev`), se muestra un panel flotante en la esquina inferior derecha con información de debug:

- Estado de autenticación
- Información del usuario logueado
- Tiempo hasta expiración del token
- Estado de actividad (activo/inactivo)
- Tiempo desde última actividad
- Botones para logout y refresh manual

El panel es minimizable y puede cerrarse. Se reactiva con un botón flotante.

---

## Despliegue

### Build de producción

```bash
npm run build
```

Esto genera una carpeta `build/` con los archivos estáticos optimizados.

### Opciones de deployment

**Recomendadas:**
- Vercel (deployment automático desde Git)
- Netlify
- Cloudflare Pages

**Alternativas:**
- Servidor Node.js con adaptador
- Contenedor Docker
- Static hosting (GitHub Pages, etc.)

---

## Documentación Adicional

- Ver archivo raíz `SETUP.md` para guía completa de instalación
- Ver carpeta `docs/` del proyecto para documentación técnica
- Documentación oficial de SvelteKit: https://kit.svelte.dev/

---

## Resolución de Problemas

### Error: "Cannot connect to API"
- Verificar que el backend esté corriendo en el puerto 8000
- Revisar la variable `VITE_API_URL` en `.env`
- Verificar CORS en el backend

### Error: "Module not found"
- Ejecutar `npm install` para instalar dependencias
- Borrar `node_modules` y reinstalar si persiste

### Hot reload no funciona
- Reiniciar el servidor de desarrollo
- Verificar que el puerto 5173 esté libre

---

&copy; 2025 Universidad Católica del Norte
