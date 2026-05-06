# Valeria — Backend API

**V**isibiliz**a**cion de co**L**eccion**e**s pat**R**imoniales por medio de **I**nteligencia **A**rtificial

API REST desarrollada con FastAPI para el proyecto ROGER. Gestiona el archivo fotográfico del Fondo Robert Gerstmann, incluyendo la jerarquía física (colecciones, cajas, rollos, fotografías), taxonomía operativa, flujo de contribuciones y generación de narrativas con IA.

---

## Requisitos

- Python 3.13
- conda (recomendado) o un entorno virtual Python estándar
- Redis (opcional en desarrollo — la aplicación arranca sin él)

---

## Instalación

### Opción A — conda (recomendado)

```bash
conda env create -f environment.yml
conda activate valeria
pip install -r requirements.txt
```

### Opción B — venv estándar

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

---

## Configuración

Copiar el archivo de ejemplo y editar las variables necesarias:

```bash
cp .env.example .env
```

Las variables mínimas para que el servidor arranque son:

```env
SECRET_KEY=cambia-esto-por-un-valor-secreto-largo
DATABASE_URL=sqlite+aiosqlite:///./valeria.db
```

Para que funcionen las narrativas y el chat con IA, agregar la clave del proveedor LLM. El proveedor por defecto es **Groq** (capa gratuita disponible en [console.groq.com](https://console.groq.com)):

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
```

Para envío de correos (registro, cambio de email), configurar las variables SMTP:

```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=tu-correo@ucn.cl
SMTP_PASSWORD=tu-contraseña
SMTP_FROM=tu-correo@ucn.cl
FRONTEND_URL=http://localhost:5173
```

El resto de las variables tienen valores por defecto que funcionan en desarrollo.

---

## Base de datos

Aplicar todas las migraciones antes de arrancar por primera vez:

```bash
alembic upgrade head
```

Esto crea el archivo `valeria.db` con el esquema completo. La base de datos incluye siete migraciones que cubren autenticación, proyectos, taxonomía, archivo físico, contribuciones y etiquetas.

Para crear un usuario administrador inicial:

```bash
python scripts/create_admin.py
```

---

## Ejecución

```bash
uvicorn app.main:app --reload
```

El servidor queda disponible en `http://localhost:8000`.

La documentación interactiva de la API está en:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

---

## Estructura del proyecto

```
app/
├── main.py
├── config/
│   └── settings.py
├── features/
│   ├── authenticate/        # JWT, roles, gestión de usuarios
│   ├── archive/             # Colecciones, cajas, rollos, fotografías, archivos
│   ├── taxonomy/            # Metadatos técnicos, cronológicos, geográficos
│   ├── contributions/       # Flujo de propuesta y aprobación de metadatos
│   ├── tagging/             # Vocabulario controlado de etiquetas
│   ├── manage_projects/     # Proyectos colaborativos
│   ├── generate_narrative/  # Narrativas con IA (RAG)
│   ├── search_filter/       # Búsqueda semántica y por filtros
│   ├── view_images/         # Galería pública de imágenes
│   └── analysis/            # Jobs de análisis automatizado
└── infrastructure/
    ├── database/
    ├── ai/
    ├── analysis/            # Analizadores de archivos (Pillow, ExifTool)
    ├── cache/
    └── middleware/
```

Cada feature sigue arquitectura hexagonal con vertical slices: `domain/`, `application/`, `infrastructure/`, `interfaces/`.

---

## Roles de usuario

| Rol | Descripción |
|-----|-------------|
| `administrador` | Acceso completo |
| `curador` | Gestión del archivo y aprobación de contribuciones |
| `mesa_evaluadora` | Revisión y aprobación de contribuciones |
| `digitalizador` | Carga de archivos fotográficos |
| `investigador` | Acceso a búsqueda avanzada y proyectos |
| `colaborador` | Puede proponer metadatos (rol por defecto al registrarse) |
| `usuario_estandar` | Solo lectura |

---

## Base de datos

En desarrollo se usa **SQLite** (archivo `valeria.db` en la raíz del proyecto). Para producción se recomienda PostgreSQL; basta con cambiar la variable `DATABASE_URL`:

```env
DATABASE_URL=postgresql+asyncpg://usuario:contraseña@localhost:5432/roger
```

Comandos útiles de Alembic:

```bash
# Aplicar migraciones pendientes
alembic upgrade head

# Crear una migración nueva
alembic revision --autogenerate -m "descripcion"

# Revertir la última migración
alembic downgrade -1
```

---

## Scripts

```bash
# Crear usuario administrador
python scripts/create_admin.py

# Poblar la base de datos con datos de prueba
python scripts/seed_db.py

# Indexar documentos en la base de conocimiento RAG
python scripts/index_knowledge_base.py
```

---

## Análisis de metadatos técnicos

El servidor extrae automáticamente los metadatos EXIF de una fotografía cuando se registra un archivo master (JPG o TIFF). Para archivos RAW (CR3), es necesario tener instalado **ExifTool** y que el ejecutable `exiftool` esté en el PATH del sistema.

---

## Tecnologías principales

- FastAPI 0.115+ / Uvicorn
- SQLAlchemy 2.0+ (async) / Alembic / aiosqlite
- Pydantic 2.10+
- python-jose (JWT) / bcrypt
- Sentence Transformers (embeddings semánticos)
- Pillow (extracción de EXIF)
- Groq / OpenAI / Anthropic (LLM agnóstico)
- Redis (caché, opcional en desarrollo)
- structlog

---

&copy; 2025 Universidad Católica del Norte
