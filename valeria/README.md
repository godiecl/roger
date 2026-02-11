# Valeria - Backend API

**V**isibiliz**A**cion de co**L**eccion**E**s pat**R**imoniales por medio de **I**nteligencia **A**rtificial

Backend API desarrollado con FastAPI para el proyecto ROGER, que proporciona servicios de gestión de colecciones patrimoniales, búsqueda semántica y generación de narrativas con IA.

---

## Estado del Proyecto

**Versión:** 0.1.0
**Completado:** ~70%

### Funcionalidades Implementadas

- ✅ Autenticación JWT con sistema de roles (RBAC)
- ✅ Gestión completa de usuarios con 7 roles diferentes
- ✅ CRUD de imágenes patrimoniales
- ✅ Búsqueda avanzada con filtros múltiples
- ✅ Búsqueda semántica con embeddings
- ✅ Generación de narrativas con IA y trazabilidad (VERAZ/VEROSÍMIL)
- ✅ Sistema de gestión de metadatos
- ✅ Base de datos con migraciones Alembic
- ✅ Arquitectura hexagonal con vertical slices
- ✅ Scripts de utilidad (seed, create_admin)

### Pendiente

- 🔲 Georreferenciación y mapas
- 🔲 Sistema de moderación de contenido
- 🔲 Gestión de colecciones
- 🔲 Líneas de tiempo paralelas
- 🔲 Detección de objetos con Computer Vision
- 🔲 Sistema de exportación de datos
- 🔲 Tests de integración completos

---

## Requisitos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)

---

## Instalación

### 1. Crear entorno virtual

```bash
python -m venv venv
```

### 2. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
# Dependencias principales
pip install -r requirements.txt

# Dependencias de desarrollo (opcional)
pip install -r requirements-dev.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env
```

Editar el archivo `.env` con la configuración necesaria:
- `DATABASE_URL` - URL de conexión a la base de datos
- `SECRET_KEY` - Clave secreta para JWT
- `OPENAI_API_KEY` - API key de OpenAI (opcional, para narrativas con IA)

### 5. Inicializar base de datos

```bash
# Ejecutar migraciones
alembic upgrade head

# (Opcional) Poblar con datos de prueba
python scripts/seed_db.py
```

---

## Ejecución

### Servidor de desarrollo

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

### Documentación de la API

Una vez el servidor esté corriendo, la documentación interactiva estará disponible en:

- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc

---

## Testing

```bash
# Ejecutar todos los tests
pytest

# Con reporte de cobertura
pytest --cov=app --cov-report=html

# Solo tests unitarios
pytest -m unit

# Solo tests de integración
pytest -m integration

# Excluir tests que requieren IA
pytest -m "not ai"
```

---

## Arquitectura

El proyecto utiliza **Arquitectura Hexagonal** combinada con **Vertical Slices**:

```
app/
├── main.py                 # Entry point
├── config/                 # Configuración
├── features/               # Features (vertical slices)
│   ├── authenticate/       # Autenticación
│   ├── manage_images/      # Gestión de imágenes
│   ├── search_images/      # Búsqueda de imágenes
│   └── generate_narratives/ # Generación de narrativas
└── infrastructure/         # Infraestructura compartida
    ├── database/
    ├── ai/
    └── security/
```

Cada feature contiene:
- `domain/` - Entidades y lógica de negocio
- `application/` - Casos de uso
- `infrastructure/` - Adaptadores (repositorios, servicios externos)
- `presentation/` - Controladores (rutas API)

---

## Scripts Útiles

```bash
# Crear usuario administrador
python scripts/create_admin.py

# Poblar base de datos con datos de prueba
python scripts/seed_db.py

# Indexar documentos en base de conocimiento RAG
python scripts/index_knowledge_base.py
```

---

## Base de Datos

**Desarrollo:** SQLite (archivo `roger.db`)
**Producción:** PostgreSQL (recomendado)

Las migraciones se gestionan con **Alembic**:

```bash
# Crear nueva migración
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

---

## Tecnologías

- **Framework:** FastAPI 0.115+
- **ORM:** SQLAlchemy 2.0+
- **Validación:** Pydantic 2.10+
- **Base de datos:** SQLite / PostgreSQL
- **Migraciones:** Alembic
- **Autenticación:** JWT con python-jose
- **Hashing:** bcrypt
- **IA:** OpenAI API, LangChain, Sentence Transformers
- **Vector DB:** ChromaDB (desarrollo) / Qdrant (producción)
- **Testing:** pytest

---

## Estructura de Datos

### Usuarios
- Sistema de roles: administrador, curador, investigador, digitalizador, colaborador, usuario estándar
- Autenticación con JWT (access token + refresh token)
- Tokens con expiración de 30 minutos (renovables si hay actividad)

### Imágenes
- Metadatos completos (título, descripción, año, ubicación, etc.)
- Soporte para múltiples formatos
- Sistema de embeddings para búsqueda semántica

### Narrativas
- Generadas con IA usando RAG (Retrieval-Augmented Generation)
- Trazabilidad completa de fuentes
- Clasificación: VERAZ (verificado) / VEROSÍMIL (inferido)

---

## Documentación Adicional

- Ver archivo raíz `SETUP.md` para guía completa de instalación
- Ver carpeta `docs/` para documentación técnica detallada
- Ver `docs/AI_ARCHITECTURE.md` para arquitectura de IA

---

## Credenciales de Prueba

Después de ejecutar `python scripts/seed_db.py`:

| Rol | Email | Password |
|-----|-------|----------|
| Administrador | admin@roger.cl | admin123 |
| Curador | curador@roger.cl | curador123 |
| Investigador | investigador@roger.cl | investigador123 |
| Usuario | user@roger.cl | user123 |

---

&copy; 2025 Universidad Católica del Norte
