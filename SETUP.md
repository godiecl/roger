# ROGER - Guía de Instalación y Configuración

Esta guía describe el proceso de instalación y configuración del proyecto ROGER, desde los requisitos previos hasta la puesta en marcha del sistema completo.

## Requisitos Previos

### Obligatorios

- **Python 3.11+** - [Descargar](https://www.python.org/downloads/)
- **Node.js 18+** - [Descargar](https://nodejs.org/)
- **Git** - [Descargar](https://git-scm.com/)

### Opcionales (Recomendados)

- **PostgreSQL 14+** - [Descargar](https://www.postgresql.org/download/) - Para entornos de producción (SQLite se utiliza en desarrollo)
- **Redis** - Para sistema de caché (mejora el rendimiento)
- **OpenAI API Key** - Requerida únicamente para generación de narrativas (costo aproximado: $10/año)
  - **Alternativa:** Modelos locales de Hugging Face (sin costo, requiere GPU)

### Verificación de instalación

```bash
python --version    # Debe ser 3.11 o superior
node --version      # Debe ser 18 o superior
psql --version      # Verificar instalación de PostgreSQL
git --version
```

---

## Configuración del Backend (Valeria)

### 1. Navegación al directorio del backend

```bash
cd valeria
```

### 2. Creación y activación del entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Linux/Mac)
source venv/bin/activate
```

### 3. Instalación de dependencias

```bash
# Dependencias de producción
pip install -r requirements.txt

# Dependencias de desarrollo (opcional)
pip install -r requirements-dev.txt
```

### 4. Configuración de base de datos

**Opción A: SQLite (Desarrollo - Recomendado)**

```bash
# No requiere instalación adicional
# SQLite se crea automáticamente durante las migraciones
# Ubicación del archivo: valeria/roger.db
```

**Opción B: PostgreSQL (Producción)**

```bash
# Conexión a PostgreSQL
psql -U postgres

# Creación de base de datos y usuario
CREATE DATABASE roger_db;
CREATE USER roger_user WITH PASSWORD 'roger_pass';
GRANT ALL PRIVILEGES ON DATABASE roger_db TO roger_user;
\q
```

### 5. Configuración de variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env
```

**Editar `valeria/.env` con los valores correspondientes:**

**Variables obligatorias:**

```env
# ===================================
# BASE DE DATOS (OBLIGATORIO)
# ===================================
# Opción 1: SQLite para desarrollo (Recomendado)
DATABASE_URL=sqlite+aiosqlite:///./roger.db

# Opción 2: PostgreSQL para producción
# DATABASE_URL=postgresql+asyncpg://roger_user:roger_pass@localhost:5432/roger_db

# ===================================
# SEGURIDAD (OBLIGATORIO EN PRODUCCIÓN)
# ===================================
SECRET_KEY=genera-una-clave-secreta-super-segura-aqui-minimo-32-caracteres
# Generar con: python -c "import secrets; print(secrets.token_urlsafe(32))"

# ===================================
# ENTORNO
# ===================================
ENVIRONMENT=development  # development | staging | production
DEBUG=True               # True para desarrollo, False en producción
```

**Variables opcionales (IA):**

```env
# ===================================
# ARQUITECTURA DE IA (Ver docs/AI_ARCHITECTURE.md)
# ===================================
# Opción 1: Híbrida (Recomendado) - Local para embeddings, OpenAI para narrativas
USE_LOCAL_EMBEDDINGS=true           # true = Sentence Transformers (gratis)
USE_LOCAL_OBJECT_DETECTION=true     # true = YOLOv8 (gratis)
OPENAI_API_KEY=sk-tu-api-key-aqui   # Solo para narrativas (~$10/año)

# Opción 2: 100% OpenAI (Más costoso pero más simple)
# USE_LOCAL_EMBEDDINGS=false
# OPENAI_API_KEY=sk-tu-api-key-aqui

# Opción 3: 100% Local (Sin costo pero requiere GPU)
# USE_LOCAL_EMBEDDINGS=true
# USE_LOCAL_LLM=true
# LOCAL_LLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct

# ===================================
# OPENAI (Solo si USE_LOCAL_EMBEDDINGS=false o para narrativas)
# ===================================
OPENAI_API_KEY=                    # Opcional en arquitectura híbrida
OPENAI_MODEL=gpt-4o-mini           # gpt-4o-mini recomendado (económico)
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# ===================================
# ANTHROPIC (Alternativa a OpenAI para narrativas)
# ===================================
# ANTHROPIC_API_KEY=
# ANTHROPIC_MODEL=claude-3-haiku-20240307
```

**Variables con valores por defecto (no requieren modificación):**

```env
# API
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Redis (Opcional - el sistema funciona sin Redis)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# ChromaDB (Para RAG)
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Logging
LOG_LEVEL=INFO
```

### 6. Inicialización de la base de datos

```bash
# Ejecutar migraciones para crear las tablas
alembic upgrade head
```

**Resultado esperado:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial tables
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Add narratives table
```

### 7. Población de la base de datos con datos de prueba

```bash
# Crear usuarios de prueba y datos iniciales
python scripts/seed_db.py
```

**Credenciales de prueba generadas:**

| Rol | Email | Password |
|-----|-------|----------|
| Administrador | `admin@roger.cl` | `admin123` |
| Curador | `curador@roger.cl` | `curador123` |
| Investigador | `investigador@roger.cl` | `investigador123` |
| Usuario Estándar | `user@roger.cl` | `user123` |

**Resultado esperado:**
```
[OK] Created user: admin@roger.cl (administrador)
[OK] Created user: curador@roger.cl (curador)
[OK] Created image: Vista panorámica del puerto de Valparaíso (1928)
[SUCCESS] Database seeding completed successfully!
```

### 8. (Opcional) Creación de usuario administrador personalizado

```bash
python scripts/create_admin.py
# Solicitará email, username y password
```

### 9. (Opcional) Indexación de documentos en la base de conocimiento RAG

```bash
# Requiere OpenAI API Key configurada
python scripts/index_knowledge_base.py
```

### 10. Ejecución del servidor

```bash
# Opción 1: Usando uvicorn directamente
uvicorn app.main:app --reload

# Opción 2: Usando el script main.py
python -m app.main

# Opción 3: Con parámetros personalizados
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**El servidor estará disponible en:**
- API: `http://localhost:8000`
- Documentación (Swagger): `http://localhost:8000/api/v1/docs`
- Redoc: `http://localhost:8000/api/v1/redoc`
- Health Check: `http://localhost:8000/health`

---

## Configuración del Frontend (Leila)

### 1. Navegación al directorio del frontend

```bash
cd leila
```

### 2. Instalación de dependencias

```bash
# Usando npm
npm install

# O usando pnpm (más rápido)
pnpm install
```

### 3. Configuración de variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env
```

**Editar `leila/.env`:**

**Variable obligatoria:**

```env
# ===================================
# URL DEL BACKEND (OBLIGATORIO)
# ===================================
VITE_API_URL=http://localhost:8000/api/v1
# En desarrollo: http://localhost:8000/api/v1
# En producción: https://tu-dominio.com/api/v1
```

**Variables opcionales (con valores por defecto):**

```env
# Application Settings
VITE_APP_NAME=ROGER
VITE_APP_DESCRIPTION=Archivo Robert Gerstmann

# Feature Flags
VITE_ENABLE_SEMANTIC_SEARCH=true    # Habilita búsqueda con IA
VITE_ENABLE_AI_NARRATIVES=true      # Habilita generación de narrativas

# Analytics (Opcional)
# VITE_GOOGLE_ANALYTICS_ID=
# VITE_MATOMO_URL=
# VITE_MATOMO_SITE_ID=
```

### 4. Ejecución del servidor de desarrollo

```bash
npm run dev
```

**El frontend estará disponible en:**
- `http://localhost:5173`

---

## Testing

### Backend (Valeria)

```bash
cd valeria

# Ejecutar todos los tests
pytest

# Con reporte de cobertura
pytest --cov=app --cov-report=html

# Solo tests unitarios
pytest -m unit

# Solo tests de integración
pytest -m integration

# Excluir tests que requieren IA (útil sin API key)
pytest -m "not ai"
```

### Frontend (Leila)

```bash
cd leila

# Tests unitarios
npm run test

# Tests E2E
npm run test:e2e

# Linting
npm run lint

# Formateo de código
npm run format
```

---

## Notas Importantes

### Arquitectura de IA

**ROGER utiliza una arquitectura HÍBRIDA para minimizar costos (reducción del 97%):**

Ver análisis completo en: [docs/AI_ARCHITECTURE.md](docs/AI_ARCHITECTURE.md)

#### Opción 1: Híbrida (Recomendada)

```
- Embeddings (búsqueda):     Sentence Transformers (Local - Sin costo)
- Detección de objetos:      YOLOv8 (Local - Sin costo)
- Clustering:                Sklearn + UMAP (Local - Sin costo)
- Narrativas:                OpenAI GPT-4o-mini (~$10/año)
```

**Ventajas:**
- Costo anual: aproximadamente $10 (versus $229 con OpenAI puro)
- No requiere GPU
- Calidad premium en narrativas
- Implementación sencilla

**Configuración `.env`:**
```env
USE_LOCAL_EMBEDDINGS=true
USE_LOCAL_OBJECT_DETECTION=true
OPENAI_API_KEY=sk-xxx  # Solo para narrativas
```

---

#### Opción 2: 100% Local (Requiere GPU)

```
- Embeddings:      Sentence Transformers (Local)
- Detección:       YOLOv8 (Local)
- Narrativas:      LLaMA 3.1 8B / Mistral 7B (Local)
```

**Ventajas:**
- Costo: $0 (sin costo)
- Privacidad total
- Ideal para investigación

**Requisitos:**
- GPU con 16GB+ VRAM (RTX 3090/4090, A100)
- O CPU potente (generación lenta: aproximadamente 5 tokens/seg)

**Configuración `.env`:**
```env
USE_LOCAL_EMBEDDINGS=true
USE_LOCAL_LLM=true
LOCAL_LLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct
```

---

#### Opción 3: 100% OpenAI (Más simple pero costoso)

```
- Embeddings:      OpenAI text-embedding-3-small
- Detección:       GPT-4 Vision
- Narrativas:      GPT-4o-mini
```

**Costo:** Aproximadamente $229/año

**Configuración `.env`:**
```env
USE_LOCAL_EMBEDDINGS=false
OPENAI_API_KEY=sk-xxx
```

---

### Obtención de API Key de OpenAI (Para Opción 1 o 3)

**Proceso para obtener una API Key:**
1. Acceder a https://platform.openai.com/
2. Crear una cuenta
3. Navegar a la sección de API Keys y generar una nueva clave
4. Agregar créditos a la cuenta ($5 inicial)
5. Copiar la clave en el archivo `.env`

### Comparación de Costos

| Componente | OpenAI Puro | Híbrida | 100% Local |
|------------|-------------|---------|------------|
| Setup inicial (10K imágenes) | $103 | $2.70 | $0 |
| Mensual (1K imágenes) | $10.53 | $0.27 | $0 |
| Año 1 | $229 | $6 | $0 |
| Año 5 | $733 | $19 | $0 |

**Recomendación:** Arquitectura Híbrida (ahorro del 97% versus OpenAI puro)

### Seguridad

**Antes de realizar commit:**
- Nunca incluir el archivo `.env` en el repositorio
- Nunca incluir API keys en el código
- Cambiar `SECRET_KEY` en entornos de producción
- Utilizar `.env.example` únicamente con valores de ejemplo

### Resolución de Problemas

**Error: "No module named 'app'"**
```bash
# Verificar que se encuentra en la carpeta valeria/
cd valeria
# Confirmar que el entorno virtual está activado
```

**Error: "Database not found"**
```bash
# Ejecutar migraciones
alembic upgrade head
```

**Error: "Redis connection failed"**
- Redis es opcional, el sistema funcionará sin él
- Para instalarlo: https://redis.io/download
- O comentar la configuración de Redis en main.py

**Error al ejecutar tests: "No OpenAI API key"**
```bash
# Excluir tests que requieren IA
pytest -m "not ai"
```

---

## Flujo de Desarrollo

### 1. Iniciar el backend

```bash
cd valeria
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
uvicorn app.main:app --reload
```

### 2. Iniciar el frontend (en terminal separada)

```bash
cd leila
npm run dev
```

### 3. Verificación de la API

Acceder a http://localhost:8000/api/v1/docs

**Endpoints disponibles:**
- `POST /api/v1/auth/login` - Autenticación de usuario
- `POST /api/v1/auth/register` - Registro de usuario
- `GET /api/v1/auth/me` - Obtener usuario actual
- `GET /health` - Verificación de estado del sistema

### 4. Ejemplo de uso con curl

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@roger.cl","password":"admin123"}'

# Respuesta esperada:
# {
#   "access_token": "eyJ...",
#   "refresh_token": "eyJ...",
#   "token_type": "bearer",
#   "user": {...}
# }
```

---

## Estructura del Proyecto

```
roger/
├── valeria/          # Backend (FastAPI + Python)
│   ├── app/
│   │   ├── main.py   # Entry point
│   │   ├── config/   # Configuración
│   │   ├── features/ # Slices (vertical)
│   │   └── infrastructure/  # Infraestructura compartida
│   ├── scripts/      # Scripts de utilidad
│   ├── tests/        # Tests
│   └── requirements.txt
│
├── leila/            # Frontend (SvelteKit + TypeScript)
│   ├── src/
│   │   ├── lib/      # Componentes, stores, services
│   │   └── routes/   # Rutas de la aplicación
│   └── package.json
│
├── docs/             # Documentación
├── .gitignore
├── README.md
└── SETUP.md          # Este archivo
```

---

## Próximos Pasos

1. Setup completado
2. Backend en ejecución
3. Frontend en ejecución
4. Obtener OpenAI API Key (opcional)
5. Implementar funcionalidades adicionales
6. Desplegar en producción

---

## Funcionalidades Pendientes de Implementación

### Completado (100% Backend + Frontend Base)

**Backend - Valeria:**
- Arquitectura hexagonal con vertical slices
- Autenticación JWT con 7 roles (RBAC)
- CRUD completo de imágenes
- Búsqueda avanzada + semántica (RAG)
- Generación de narrativas con IA
- Sistema de trazabilidad (VERAZ/VEROSÍMIL)
- Base de datos PostgreSQL + migraciones Alembic
- Scripts de utilidad (seed, create_admin, index_kb)

**Frontend - Leila:**
- Componentes base (Layout, Header, Footer)
- Componentes de visualización (ImageCard, ImageGrid, ImageViewer)
- Stores de Svelte (auth, images, search, notifications)
- Servicios API completos
- Rutas públicas (Home, Gallery, Login, About)
- Sistema de notificaciones (Toast)

### Pendientes de Implementar

#### Alta Prioridad

1. **Mapa Interactivo** (`/map` route)
   - Integración con Leaflet o Google Maps
   - Visualización geográfica de imágenes por ubicación
   - Filtrado por región/zona

2. **Panel de Administración** (`/admin/*` routes)
   - Gestión de usuarios (crear, editar, eliminar, roles)
   - Moderación de narrativas (aprobar/rechazar)
   - Gestión de colecciones
   - Estadísticas y analytics

3. **Perfil de Usuario** (`/profile` route)
   - Visualización y edición de perfil
   - Cambio de contraseña
   - Historial de narrativas generadas
   - Preferencias de usuario

4. **Upload de Imágenes**
   - Interfaz para subir nuevas fotografías
   - Procesamiento y optimización de imágenes
   - Extracción de metadatos EXIF
   - Validación de formatos

5. **Colecciones**
   - Agrupación de imágenes por colecciones temáticas
   - CRUD de colecciones
   - Vista de colección individual

#### Media Prioridad

6. **Búsqueda Avanzada UI**
   - Filtros facetados más completos
   - Autocomplete en búsqueda
   - Historial de búsquedas
   - Búsquedas guardadas

7. **Compartir y Exportar**
   - Compartir imágenes por URL
   - Exportar resultados de búsqueda (PDF, Excel)
   - Generar citas bibliográficas

8. **Comparador de Imágenes**
   - Visualización de dos o más imágenes lado a lado
   - Comparación de metadatos
   - Línea de tiempo visual

9. **Comentarios y Colaboración**
   - Sistema de comentarios en imágenes
   - Reporte de errores en metadatos
   - Sugerencias de corrección

10. **Notificaciones en Tiempo Real**
    - WebSocket para notificaciones
    - Alertas de nuevas imágenes
    - Notificaciones de aprobación de narrativas

#### Baja Prioridad

11. **Multilenguaje (i18n)**
    - Español (por defecto)
    - Inglés
    - Alemán (idioma de Gerstmann)

12. **PWA (Progressive Web App)**
    - Modo offline
    - Instalación en dispositivos
    - Cache de imágenes

13. **Integración con Redes Sociales**
    - Login con Google, Facebook
    - Compartir en redes sociales

14. **API Pública**
    - Documentación para desarrolladores externos
    - Rate limiting
    - API keys para terceros

15. **Visualizaciones Avanzadas**
    - Timeline histórico interactivo
    - Grafos de relaciones entre imágenes
    - Estadísticas y dashboards

### Mejoras Técnicas Pendientes

- **Tests**: Aumentar cobertura de tests (unitarios, integración, E2E)
- **Performance**: Implementar lazy loading, pagination infinita
- **SEO**: Meta tags, sitemap, robots.txt
- **Accesibilidad**: ARIA labels, navegación por teclado
- **Docker**: Dockerfiles para backend y frontend
- **CI/CD**: GitHub Actions para deploy automático
- **Monitoring**: Sentry para errores, analytics
- **Backup**: Sistema de backup automatizado de base de datos

### Slices Adicionales del Backend

Según la documentación original, faltan estos slices:
- `manage_collections/` - Gestión de colecciones
- `upload_images/` - Carga y procesamiento de imágenes
- `moderate_content/` - Moderación por curadores
- `export_data/` - Exportación de datos
- `analytics/` - Estadísticas y métricas

---

## Estado del Proyecto

**Completado:** Aproximadamente 60%
- Backend core: 100%
- Frontend core: 80%
- Features avanzados: 30%
- Tests: 20%
- Deploy/DevOps: 0%

**Siguiente Milestone:** Implementación de mapa interactivo y panel de administración

---

## Soporte

En caso de problemas durante la instalación:
1. Revisar la sección de Resolución de Problemas
2. Verificar que todas las dependencias estén instaladas
3. Confirmar que los puertos 8000 y 5173 estén disponibles
4. Consultar los logs: `valeria/logs/` y consola del navegador

**Logs útiles:**
```bash
# Ver logs del backend
tail -f valeria/logs/app.log

# Ver logs de PostgreSQL (Linux/Mac)
tail -f /var/log/postgresql/postgresql-14-main.log

# Ver logs de Redis
redis-cli monitor
```

---

## Despliegue en Producción (Futuro)

### Opciones recomendadas

**Backend:**
- Railway, Render, DigitalOcean App Platform
- PostgreSQL managed database
- Redis managed instance (opcional)

**Frontend:**
- Vercel, Netlify, Cloudflare Pages
- Deploy automático desde Git

**Solución completa (Backend + Frontend):**
- Docker + Docker Compose
- AWS (EC2 + RDS + S3)
- Google Cloud Platform
- Azure

---

**Última actualización:** Febrero 2026
**Versión:** 1.0.0-beta
