# Leila — Frontend Web

**L**egado de **E**xploración de **I**mágenes y **L**ibrería **A**rchivística

Interfaz web desarrollada con SvelteKit para el proyecto ROGER. Permite explorar, buscar y visualizar las colecciones fotográficas del Fondo Robert Gerstmann, proponer metadatos, revisar contribuciones y colaborar en proyectos de investigación con asistencia de IA.

---

## Requisitos

- Node.js 18 o superior
- npm (incluido con Node.js)
- El backend Valeria debe estar corriendo en `http://localhost:8000`

---

## Instalación

```bash
npm install
```

---

## Configuración

El archivo `.env` ya está incluido con los valores por defecto para desarrollo local. Si necesita ajustarlo:

```env
# URL del backend
VITE_API_URL=http://localhost:8000/api/v1

# Nombre de la aplicación
VITE_APP_NAME=ROGER
VITE_APP_DESCRIPTION=Archivo Robert Gerstmann

# Feature flags
VITE_ENABLE_SEMANTIC_SEARCH=true
VITE_ENABLE_AI_NARRATIVES=true
```

Si el backend corre en un puerto distinto, cambiar `VITE_API_URL` según corresponda.

---

## Ejecución

```bash
npm run dev
```

La aplicación queda disponible en `http://localhost:5173`.

---

## Otros comandos

```bash
# Build de producción
npm run build

# Vista previa del build
npm run preview

# Verificación de tipos TypeScript
npm run check

# Linting
npm run lint
```

---

## Estructura del proyecto

```
src/
├── routes/
│   ├── (public)/            # Páginas accesibles sin sesión
│   │   ├── +page.svelte     # Inicio
│   │   ├── colecciones/     # Galería pública con búsqueda
│   │   ├── archivo/         # Explorador jerárquico del archivo físico (requiere login)
│   │   ├── mapa/            # Exploración geográfica
│   │   ├── investigacion/
│   │   ├── sobre-roger/
│   │   └── login/
│   └── (protected)/         # Requieren sesión activa
│       ├── archivo/         # Catalogación (Colecciones → Cajas → Rollos → Fotografías)
│       ├── curador/         # Cola de revisión de contribuciones
│       ├── proyectos/       # Proyectos colaborativos con chat IA
│       ├── profile/         # Perfil y configuración de cuenta
│       └── admin/           # Gestión de usuarios (solo administrador)
├── lib/
│   ├── components/
│   │   ├── common/          # Toast, Loading, ErrorMessage, ThemeToggle
│   │   ├── layout/          # Header, Footer, Layout
│   │   └── viewer/          # ImageCard, ImageGrid, ImageViewer
│   ├── services/            # Clientes HTTP por dominio
│   │   ├── apiClient.ts     # Cliente base con manejo de auth y errores
│   │   ├── archiveService.ts
│   │   ├── contributionService.ts
│   │   ├── authService.ts
│   │   ├── imageService.ts
│   │   ├── projectService.ts
│   │   └── ...
│   ├── stores/              # Estado reactivo (auth, images, search, notifications)
│   └── types/               # Interfaces TypeScript
└── app.css                  # Estilos globales (Tailwind + DaisyUI)
```

---

## Páginas principales

| Ruta | Acceso | Descripción |
|------|--------|-------------|
| `/` | Público | Página de inicio con galería destacada |
| `/colecciones` | Público | Búsqueda global con filtros y búsqueda semántica |
| `/mapa` | Público | Exploración geográfica de fotografías |
| `/archivo` | Autenticado | Explorador jerárquico: Colección → Caja → Rollo → Fotografía |
| `/curador` | Curador / Admin | Cola de contribuciones pendientes de aprobación |
| `/proyectos` | Autenticado | Proyectos colaborativos con chat IA |
| `/admin` | Administrador | Gestión de usuarios y roles |
| `/profile` | Autenticado | Edición de perfil y cambio de contraseña |

---

## Acceso según rol

El menú se adapta al rol del usuario autenticado:

- Todos los usuarios autenticados ven **Catalogación** (`/archivo`) en el dropdown de perfil.
- Curadores, mesa evaluadora y administradores ven además **Cola de revisión** (`/curador`).
- Solo administradores y curadores ven el **Panel de administración** (`/admin`).

---

## Tecnologías principales

- SvelteKit 2.0 / Svelte 4
- TypeScript 5
- Tailwind CSS 3 + DaisyUI 4
- Vite 5
- Leaflet (mapa interactivo)

---

## Resolución de problemas

**"Cannot connect to API" o errores 401/404 al cargar datos**
Verificar que el backend esté corriendo (`uvicorn app.main:app --reload` en la carpeta `valeria`) y que `VITE_API_URL` en `.env` apunte al puerto correcto.

**Cambios no se reflejan en el navegador**
Detener el servidor de desarrollo y volver a ejecutar `npm run dev`. Si persiste, borrar la carpeta `.svelte-kit` y reiniciar.

**Error de tipos TypeScript**
Ejecutar `npm run check` para ver los errores específicos. Asegurarse de haber corrido `npm install` después de actualizar el repositorio.

---

&copy; 2025 Universidad Católica del Norte
