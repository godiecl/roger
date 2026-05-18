# Diseño: Narrativa Comunitaria y Engagement — ROGER

**Fecha:** 2026-05-17
**Estado:** Aprobado
**Scope:** Backend (FastAPI) + Frontend (SvelteKit)

---

## Contexto

El viewer de imágenes actualmente tiene 3 tabs: Fotografía / Narrativa IA / Línea de Tiempo. Este diseño extiende el sistema de narrativas con:

1. Contexto histórico auto-generado por visita (público, sin auth)
2. Sistema de likes y reportes con control de spam por IP
3. Flujo de curación: los contextos con likes pueden ser anclados por curadores
4. Curadores pueden crear narrativas manuales marcadas como Veraz
5. Línea de Tiempo enriquecida con eventos reales de Wikipedia
6. Badge de reportes pendientes en panel de admin

---

## 1. Schema

### Tabla nueva: `image_contexts`

Almacena todos los contextos históricos generados on-demand. Múltiples registros por imagen.

```sql
id              INTEGER PRIMARY KEY
image_id        INTEGER NOT NULL               -- referencia a photographs/images
text            TEXT NOT NULL                  -- párrafo generado por LLM
provider        VARCHAR(50) NOT NULL           -- groq | openai | anthropic
generation_time_ms INTEGER NOT NULL
is_anchored     BOOLEAN DEFAULT FALSE
anchored_by     INTEGER REFERENCES users(id)   -- nullable
anchored_at     DATETIME                       -- nullable
like_count      INTEGER DEFAULT 0              -- desnormalizado
report_count    INTEGER DEFAULT 0              -- desnormalizado
created_at      DATETIME NOT NULL
updated_at      DATETIME NOT NULL
```

Sin unique constraint en `image_id` — se generan N contextos por imagen, uno por visita.

### Tabla nueva: `content_likes`

Likes polimórficos para contextos y narrativas. Deleteable (toggle).

```sql
id           INTEGER PRIMARY KEY
content_type VARCHAR(20) NOT NULL   -- 'context' | 'narrative'
content_id   INTEGER NOT NULL
ip_hash      VARCHAR(64) NOT NULL   -- SHA256 de la IP, nunca la IP en crudo
created_at   DATETIME NOT NULL

UNIQUE (content_type, content_id, ip_hash)
```

### Tabla nueva: `content_reports`

Reportes polimórficos. One-way — no se pueden eliminar.

```sql
id           INTEGER PRIMARY KEY
content_type VARCHAR(20) NOT NULL   -- 'context' | 'narrative'
content_id   INTEGER NOT NULL
ip_hash      VARCHAR(64) NOT NULL
reason       TEXT                   -- nullable, texto libre del usuario
status       VARCHAR(20) DEFAULT 'pending'  -- 'pending' | 'reviewed' | 'dismissed'
created_at   DATETIME NOT NULL

UNIQUE (content_type, content_id, ip_hash)
```

### Modificación a `narratives` (existente)

Agregar tres columnas:

```sql
like_count    INTEGER DEFAULT 0
report_count  INTEGER DEFAULT 0
is_manual     BOOLEAN DEFAULT FALSE  -- True cuando el curador escribe la narrativa a mano
```

### Migración Alembic

```
008 — add_image_contexts_likes_reports
```

---

## 2. Anti-spam

4 capas en orden de activación:

| Capa | Dónde | Mecanismo |
|------|-------|-----------|
| 1 | Cliente | Botones like/report deshabilitados 3s al abrir el viewer (silencioso, sin countdown) |
| 2 | Cliente | Estado `localStorage` por content_id — restaura like/report entre recargas |
| 3 | Backend | `UNIQUE(content_type, content_id, ip_hash)` — hard gate en DB, retorna 409 si duplicado |
| 4 | Backend | Rate limit 10 acciones/IP/5min — middleware existente en `valeria/app/infrastructure/middleware/rate_limit` |

**Reglas:**
- Like: toggle (se puede dar y quitar). `like_count` sube y baja.
- Reporte: one-way. Una vez enviado, bloqueado para esa IP en ese contenido. `report_count` solo sube.
- IP nunca se almacena en crudo — siempre `SHA256(ip_address)`.

---

## 3. Backend — Nuevo slice `generate_context/`

Prefijo de ruta: `/api/v1/context`

### Estructura del slice

```
features/generate_context/
├── domain/
│   ├── context.py              # Entidad Context
│   └── context_port.py         # IContextRepository, IContextGenerator
├── application/
│   └── generate_context_usecase.py
├── infrastructure/
│   ├── adapters/
│   │   ├── context_generator.py    # Llama LLM con RAG Gerstmann
│   │   └── context_repository.py
│   └── persistence/
│       └── context_model.py        # SQLAlchemy model
└── interfaces/api/
    ├── routes.py
    └── schemas.py
```

### Endpoints

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `POST` | `/context/generate/{image_id}` | público | Genera contexto nuevo (siempre), persiste y retorna |
| `GET` | `/context/image/{image_id}/anchored` | público | Retorna contextos anclados para mostrar en viewer |
| `POST` | `/context/{id}/like` | público, IP | Toggle like — `{liked: bool, like_count: int}` |
| `POST` | `/context/{id}/report` | público, IP | One-way — 409 si ya reportó |
| `POST` | `/context/{id}/anchor` | curador/admin | Ancla el contexto |
| `DELETE` | `/context/{id}/anchor` | curador/admin | Desancla el contexto |
| `GET` | `/context/pending` | curador/admin | Cola: contextos con likes > 0, no anclados, orden DESC like_count |
| `GET` | `/context/pending-reports-count` | admin | Total de `content_reports` con status='pending' — para badge en panel admin |

### Lógica de `generate_context`

1. Recibe `image_id`
2. Llama LLM con prompt de contexto histórico, usando RAG Gerstmann (cuando esté poblado)
3. Persiste el contexto en `image_contexts` (sin importar si ya existen otros para la misma imagen)
4. Retorna el nuevo contexto con su `id`

El badge de este contexto es siempre **Verosímil** (generado por IA).

### Lógica de `anchor`

- `is_anchored = True`, `anchored_by = user_id`, `anchored_at = now`
- El contexto anclado aparece en `GET /context/image/{image_id}/anchored`
- Badge: **Verosímil** (sigue siendo IA aunque el curador lo ancle)

---

## 4. Backend — Extensiones a `generate_narrative/` (existente)

Agregar al router existente:

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `POST` | `/narratives/{id}/like` | público, IP | Toggle like en narrativa curada |
| `POST` | `/narratives/{id}/report` | público, IP | One-way report en narrativa curada |

Las narrativas creadas manualmente por curador se crean con el endpoint existente `POST /narratives` (ya protegido). El campo `is_manual` se agrega al request body — el curador lo envía como `true` cuando escribe la narrativa a mano. El backend lo persiste y el frontend usa ese campo para decidir el badge.

**Badge logic (determinista, sin inferir del rol):**
- `is_manual = True` → **Veraz** — el curador afirma que el contenido es información verificada
- `is_manual = False` (default) → **Verosímil** — generado por LLM

---

## 5. Backend — Modificación a `generate_timeline/`

### Flujo actualizado de `TimelineGenerator`

1. Recibir `photograph_date` y `photograph_location`
2. **Extraer año:** si `photograph_date` tiene año explícito, usarlo. Si no, llamar LLM para estimarlo desde `photograph_description`
3. **Llamar Wikipedia Search API:**
   ```
   GET https://en.wikipedia.org/w/api.php
     ?action=query&list=search
     &srsearch={location}+{year}
     &format=json&srlimit=20
   ```
4. **LLM selecciona:** de los 20 resultados, el LLM elige los 5-8 más relevantes al contexto de la foto
5. **Persistir:** eventos de Wikipedia con `source_type='veraz'`
6. Si Wikipedia no responde o no hay resultados: fallback a eventos LLM con `source_type='verosimil'` (comportamiento actual)

---

## 6. Frontend

### Tab "Narrativa" — nuevo flujo

Al abrir el tab, dos llamadas en paralelo:

```
POST /context/generate/{image_id}   → contexto fresco de esta visita
GET  /context/image/{image_id}/anchored → contextos/narrativas fijadas
```

**Layout del tab:**

```
┌─────────────────────────────────────────┐
│ [skeleton 3 líneas]                     │  ← mientras genera
│  → reemplazado por contexto generado    │
│                                         │
│  Badge: Verosímil                       │
│  [LikeReportBar]                        │
├─────────────────────────────────────────┤
│ Fijadas por curador (si existen)        │
│                                         │
│  Narrativa 1  Badge: Veraz              │
│  [LikeReportBar]                        │
│                                         │
│  Narrativa 2  Badge: Verosímil          │
│  [LikeReportBar]                        │
└─────────────────────────────────────────┘
```

Si el contexto falla: mensaje "No se pudo generar el contexto" + botón Reintentar.

### Componente nuevo: `LikeReportBar.svelte`

Props: `contentType: 'context' | 'narrative'`, `contentId: number`, `likeCount: number`

**Comportamiento:**
- Al montar: lee `localStorage` → `roger_like_{type}_{id}` y `roger_report_{type}_{id}`
- Botones deshabilitados 3s desde mount (capa 1 anti-spam)
- **Like:** toggle visual inmediato (optimistic UI) + `POST /context/{id}/like` o `/narratives/{id}/like`
- **Report:** abre confirmación ("¿Reportar este contenido?") → POST → estado permanente "Reportado"
- Errores de red: revertir estado optimista, mostrar toast

### Skeleton en lugar de spinners

- Contexto generándose → `<div class="skeleton h-4 w-full">` × 4 líneas
- Imagen cargando → skeleton del aspect-ratio de la foto
- Narrativas ancladas cargando → skeleton de tarjeta completa

### Badge de reportes en `/admin`

`GET /context/pending-reports-count` retorna `{ count: number }` — total de `content_reports` con `status='pending'`.

El panel admin muestra:

```
Reportes pendientes  [badge: 12]
```

Al hacer click navega a la vista de reportes donde el admin puede marcar como `reviewed` o `dismissed`.

---

## 7. Archivos a crear / modificar

### Backend (`valeria/`)

**Nuevos:**
- `features/generate_context/` — slice completo (domain, application, infrastructure, interfaces)
- `alembic/versions/008_add_image_contexts_likes_reports.py`

**Modificados:**
- `features/generate_narrative/interfaces/api/routes.py` — endpoints like/report + campo `is_manual`
- `features/generate_narrative/interfaces/api/schemas.py` — campo `is_manual` en request/response
- `features/generate_timeline/infrastructure/adapters/timeline_generator.py` — Wikipedia API
- `app/main.py` — registrar router de `generate_context`
- `app/infrastructure/database/session.py` — registrar `ContextModel` en `init_db()`
- `alembic/env.py` — importar nuevos modelos

### Frontend (`leila/`)

**Nuevos:**
- `lib/components/viewer/LikeReportBar.svelte`

**Modificados:**
- `lib/components/viewer/ImageViewer.svelte` — tab Narrativa con nuevo flujo
- `routes/(protected)/admin/+page.svelte` — badge de reportes pendientes

---

## 8. Invariantes

- IP nunca en crudo en DB — siempre `SHA256(ip)`
- `content_reports` nunca se eliminan — solo cambian `status`
- Contextos con `like_count = 0` y `report_count = 0` pueden limpiarse con job futuro
- Badge Veraz solo cuando `is_manual = True` y autor es curador/admin
- Wikipedia como fuente → `source_type = 'veraz'`; LLM solo → `source_type = 'verosimil'`
- Si Wikipedia falla: fallback silencioso a LLM, no error al usuario
