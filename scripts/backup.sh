#!/bin/bash
# =============================================================================
# ROGER — Script de backup diario
#
# Qué respalda:
#   - Base de datos SQLite (backup atómico vía sqlite3 .backup)
#   - Directorio storage/ (fotografías y uploads)
#   - Directorio chroma_db/ (índice vectorial ChromaDB)
#
# Retención: 30 días. Los backups más antiguos se eliminan automáticamente.
#
# INSTALACIÓN (ejecutar una vez en el servidor UCN como root o usuario con cron):
#
#   1. Copiar este archivo al servidor:
#        scp scripts/backup.sh usuario@servidor-ucn:/opt/roger/backup.sh
#        chmod +x /opt/roger/backup.sh
#
#   2. Crear el directorio de backups:
#        mkdir -p /opt/roger/backups
#
#   3. Agregar al crontab del servidor (cron diario a las 03:00):
#        crontab -e
#        0 3 * * * /opt/roger/backup.sh >> /var/log/roger-backup.log 2>&1
#
#   4. Verificar que funciona:
#        /opt/roger/backup.sh
#        ls -lh /opt/roger/backups/
#
# RESTAURAR (en caso de falla):
#   Ver sección "Plan de rollback" al final de este archivo.
# =============================================================================

set -euo pipefail

# ─── Configuración ─────────────────────────────────────────────────────────────
ROGER_DIR="${ROGER_DIR:-/opt/roger}"          # directorio raíz del deploy
BACKUP_DIR="${BACKUP_DIR:-/opt/roger/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_PREFIX="[ROGER backup ${TIMESTAMP}]"

# ─── Funciones ─────────────────────────────────────────────────────────────────
log() { echo "${LOG_PREFIX} $*"; }
die() { echo "${LOG_PREFIX} ERROR: $*" >&2; exit 1; }

# ─── Verificar dependencias ────────────────────────────────────────────────────
command -v sqlite3  >/dev/null || die "sqlite3 no encontrado. Instalar: apt-get install sqlite3"
command -v tar      >/dev/null || die "tar no encontrado"
command -v docker   >/dev/null || die "docker no encontrado"

# ─── Crear directorio de backups si no existe ──────────────────────────────────
mkdir -p "${BACKUP_DIR}"

# ─── 1. Backup de SQLite ───────────────────────────────────────────────────────
# Usa sqlite3 .backup para un snapshot atómico y consistente, seguro con
# escrituras concurrentes. NO usar cp directamente sobre el .db en uso.
DB_SOURCE="${ROGER_DIR}/data/valeria.db"
DB_DEST="${BACKUP_DIR}/valeria_${TIMESTAMP}.db"

if [ -f "${DB_SOURCE}" ]; then
    log "Respaldando base de datos SQLite..."
    sqlite3 "${DB_SOURCE}" ".backup '${DB_DEST}'"
    log "Base de datos → ${DB_DEST} ($(du -sh "${DB_DEST}" | cut -f1))"
else
    die "Base de datos no encontrada en ${DB_SOURCE}"
fi

# ─── 2. Backup de storage/ (fotografías) ──────────────────────────────────────
STORAGE_SOURCE="${ROGER_DIR}/storage"
STORAGE_DEST="${BACKUP_DIR}/storage_${TIMESTAMP}.tar.gz"

if [ -d "${STORAGE_SOURCE}" ]; then
    log "Respaldando storage/..."
    tar -czf "${STORAGE_DEST}" -C "${ROGER_DIR}" storage/
    log "Storage → ${STORAGE_DEST} ($(du -sh "${STORAGE_DEST}" | cut -f1))"
else
    log "AVISO: directorio storage/ no encontrado, omitiendo"
fi

# ─── 3. Backup de chroma_db/ (índice vectorial) ────────────────────────────────
CHROMA_SOURCE="${ROGER_DIR}/chroma_db"
CHROMA_DEST="${BACKUP_DIR}/chroma_${TIMESTAMP}.tar.gz"

if [ -d "${CHROMA_SOURCE}" ]; then
    log "Respaldando chroma_db/..."
    tar -czf "${CHROMA_DEST}" -C "${ROGER_DIR}" chroma_db/
    log "ChromaDB → ${CHROMA_DEST} ($(du -sh "${CHROMA_DEST}" | cut -f1))"
else
    log "AVISO: chroma_db/ no encontrado, omitiendo (puede no estar indexado aún)"
fi

# ─── 4. Limpiar backups viejos ─────────────────────────────────────────────────
log "Eliminando backups con más de ${RETENTION_DAYS} días..."
find "${BACKUP_DIR}" -name "valeria_*.db"     -mtime "+${RETENTION_DAYS}" -delete
find "${BACKUP_DIR}" -name "storage_*.tar.gz" -mtime "+${RETENTION_DAYS}" -delete
find "${BACKUP_DIR}" -name "chroma_*.tar.gz"  -mtime "+${RETENTION_DAYS}" -delete

# ─── 5. Health check post-backup ──────────────────────────────────────────────
log "Verificando health del backend..."
if curl -sf http://localhost/health > /dev/null 2>&1; then
    log "Backend healthy"
else
    log "AVISO: backend no responde en /health — verificar manualmente"
fi

log "Backup completado."

# =============================================================================
# PLAN DE ROLLBACK
#
# Ante falla grave (datos corruptos, migración fallida, deploy roto):
#
# 1. PARAR LOS CONTENEDORES:
#      cd /opt/roger && docker compose down
#
# 2. RESTAURAR LA BASE DE DATOS:
#      # Identificar el backup más reciente
#      ls -lt /opt/roger/backups/valeria_*.db | head -1
#
#      # Reemplazar el .db actual
#      cp /opt/roger/data/valeria.db /opt/roger/data/valeria.db.broken
#      cp /opt/roger/backups/valeria_YYYYMMDD_HHMMSS.db /opt/roger/data/valeria.db
#
# 3. RESTAURAR STORAGE (solo si se perdieron archivos):
#      tar -xzf /opt/roger/backups/storage_YYYYMMDD_HHMMSS.tar.gz -C /opt/roger/
#
# 4. VOLVER A LA VERSIÓN ANTERIOR DEL CÓDIGO (si el deploy rompió algo):
#      cd /opt/roger
#      git log --oneline -10          # identificar el commit anterior
#      git checkout <commit-anterior>
#      docker compose build
#
# 5. ARRANCAR:
#      docker compose run --rm valeria-migrate
#      docker compose up -d
#
# 6. VERIFICAR:
#      curl http://localhost/health
#      docker compose logs --tail=50 valeria
# =============================================================================
