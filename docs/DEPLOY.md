# ROGER — Pasos para poner operativo en producción

Runbook ejecutable. Usa los artefactos `*.prod` del repo. Si algún paso falla,
detente y resuélvelo antes de continuar — no encadenes errores.

## Índice

| # | Paso |
|---|---|
| 0 | Pre-requisitos del servidor UCN |
| 1 | Obtener el código |
| 2 | Configurar `.env.prod` |
| 3 | Certificados TLS |
| 4 | Build de imágenes |
| 5 | Primer arranque |
| 6 | Migraciones Alembic |
| 7 | Crear usuario administrador |
| 8 | Indexar Knowledge Bases en Qdrant |
| 9 | Verificación end-to-end |
| 10 | Deploys posteriores |
| 11 | Backups |
| 12 | Rollback |
| 13 | Logs y observabilidad básica |
| 14 | Apagar / reiniciar |

---

## 0. Pre-requisitos del servidor UCN

Verificar en la VM destino:

```bash
docker --version              # >= 24.0
docker compose version        # >= v2.20 (plugin, no docker-compose legacy)
df -h /                       # >= 20 GB libres recomendado
free -h                       # >= 4 GB RAM (Qdrant + Valeria + Redis + Leila + Nginx)
```

Puertos requeridos en el firewall UCN: **80** y **443** entrantes. El resto
queda en la red interna del compose y no se expone al host.

Salidas necesarias (Firewall UCN debe permitirlas):
`api.groq.com`, `huggingface.co`, `pypi.org`, `registry.npmjs.org`,
`download.pytorch.org` (este solo si se activan analizadores con torch).

---

## 1. Obtener el código

```bash
sudo mkdir -p /opt/roger && sudo chown $USER /opt/roger
cd /opt/roger
git clone https://github.com/godiecl/roger.git .
git checkout main          # ⚠️ la rama de producción es main, NO DLeon96
```

Para deploys posteriores: `git fetch && git checkout main && git pull --ff-only`.

---

## 2. Configurar `.env.prod`

```bash
cp .env.prod.example .env.prod
chmod 600 .env.prod         # solo el dueño puede leerlo
```

Generar y completar los `CAMBIAR_*`:

```bash
echo "SECRET_KEY=$(openssl rand -hex 32)"
echo "REDIS_PASSWORD=$(openssl rand -base64 24)"
echo "QDRANT_API_KEY=$(openssl rand -base64 32)"
```

Pegar esos tres valores en `.env.prod`. Después completar a mano:

- `GROQ_API_KEY` — desde la consola de Groq.
- `SMTP_USER` / `SMTP_PASSWORD` / `SMTP_FROM` — credenciales del correo UCN.
- `FRONTEND_URL` — URL pública (mientras TI UCN no asigne dominio, usar
  `https://<IP_pública>`).
- `CORS_ORIGINS` — debe coincidir exactamente con `FRONTEND_URL`.
- `TLS_CERT_DIR` — path en el host donde van a vivir los cert (default
  `/etc/roger/certs`).

Validar que no queda ningún `CAMBIAR_` en el archivo:

```bash
grep -n CAMBIAR_ .env.prod && echo "FALTAN VARIABLES" || echo "OK"
```

---

## 3. Certificados TLS

Si TI UCN ya entregó el cert:

```bash
sudo mkdir -p /etc/roger/certs
sudo cp <ruta-recibida>/fullchain.pem /etc/roger/certs/
sudo cp <ruta-recibida>/privkey.pem   /etc/roger/certs/
sudo chmod 644 /etc/roger/certs/fullchain.pem
sudo chmod 600 /etc/roger/certs/privkey.pem
```

Si **aún no hay cert**: comentar temporalmente el bloque `listen 443 ssl` en
`nginx.conf` para arrancar solo HTTP. Marcar como deuda y descomentar cuando
llegue el cert. **No** auto-generar self-signed para una URL pública.

Ajustar `nginx.conf` si el dominio real ya está definido — reemplazar
`roger.ucn.cl` por el dominio asignado (10 sitios identificados; ver el
inventario que dejé en el chat o `grep -rn roger.ucn.cl` para auditar).

---

## 4. Build de imágenes

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod build
```

Tarda 8-15 min la primera vez (descarga node:20-alpine, python:3.13-slim,
qdrant, redis, nginx + instala todas las deps de Valeria y Leila).

Verificar que las imágenes quedaron:

```bash
docker images | grep roger
# roger/valeria   prod   <hash>   <size>
# roger/leila     prod   <hash>   <size>
```

---

## 5. Primer arranque

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

Esperar ~60 segundos y verificar healthchecks:

```bash
docker compose -f docker-compose.prod.yml ps
```

Todos los servicios deben aparecer en estado `running` y `(healthy)`:

```
NAME                IMAGE                STATUS
roger-redis-1       redis:7-alpine       Up 1m (healthy)
roger-qdrant-1      qdrant/qdrant:...    Up 1m (healthy)
roger-valeria-1     roger/valeria:prod   Up 1m (healthy)
roger-leila-1       roger/leila:prod     Up 1m
roger-nginx-1       nginx:1.27-alpine    Up 1m (healthy)
```

Si algún servicio está `unhealthy` o reiniciando, abrir logs:

```bash
docker compose -f docker-compose.prod.yml logs valeria --tail=100
docker compose -f docker-compose.prod.yml logs qdrant  --tail=50
```

Causas frecuentes la primera vez:
- `SECRET_KEY` vacío → Valeria no arranca (fail-fast en settings).
- `REDIS_PASSWORD` con caracteres raros sin escapar → redis-cli no autentica.
- Cert TLS faltante → nginx no levanta el bloque 443.

---

## 6. Migraciones Alembic

Se aplican **automáticamente** al arrancar Valeria (lo hace
[entrypoint.prod.sh](../valeria/entrypoint.prod.sh) antes de uvicorn).
**No correr `alembic upgrade head` manual** salvo que el entrypoint falle.

Verificar estado:

```bash
docker compose -f docker-compose.prod.yml exec valeria alembic current
# Debe mostrar 011 (head)
```

---

## 7. Crear usuario administrador

Una sola vez, con los contenedores corriendo:

```bash
docker compose -f docker-compose.prod.yml exec valeria \
    python scripts/create_admin.py
```

Pide email/password interactivos. Guardar las credenciales en un gestor de
secretos del equipo, **no en .env ni en repo**.

---

## 8. Indexar Knowledge Bases en Qdrant

Qdrant arranca con colecciones vacías. Sin esto, las narrativas RAG van a
devolver "sin contexto":

```bash
docker compose -f docker-compose.prod.yml exec valeria \
    python scripts/index_knowledge_base.py
```

Verificar que las colecciones existen:

```bash
docker compose -f docker-compose.prod.yml exec valeria python - <<'PY'
import asyncio
from qdrant_client import AsyncQdrantClient
import os
async def main():
    c = AsyncQdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])
    r = await c.get_collections()
    for col in r.collections:
        n = (await c.count(col.name, exact=True)).count
        print(f"{col.name}: {n} puntos")
    await c.close()
asyncio.run(main())
PY
```

Esperado: al menos `historical_kb`, `gazetteer_kb` (más los que indexe el script).

---

## 9. Verificación end-to-end

**Backend health**:
```bash
curl -fsS https://<dominio_o_ip>/api/v1/health
# {"status":"ok"}
```

**Frontend**:
- Abrir `https://<dominio_o_ip>/` en navegador → ver el home de ROGER.
- Cargar `/mapa` → debe mostrar el mapa centrado en Chile (sin pines hasta
  que se siembren georefs, esto es esperado).
- Hacer login con el admin recién creado.

**Storage**:
```bash
curl -I https://<dominio_o_ip>/storage/images/<algún_path_existente>.jpg
# 200 OK (nginx sirve directo, no pasa por Valeria)
```

---

## 10. Deploys posteriores

```bash
cd /opt/roger
git fetch && git pull --ff-only origin main
docker compose -f docker-compose.prod.yml --env-file .env.prod build
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

`docker compose up -d` solo recrea los servicios cuya imagen cambió. Las
migraciones se aplican automáticamente. **Sin downtime** si los cambios son
solo de Leila; si tocan Valeria, hay ~5s de cortes mientras el contenedor
nuevo arranca y nginx detecta el healthcheck.

---

## 11. Backups

`scripts/backup.sh` (ya en el repo) respalda `./data/` (SQLite), `./storage/`
(imágenes) y opcionalmente los snapshots de Qdrant. Ejecutarlo desde el host:

```bash
./scripts/backup.sh /var/backups/roger/
```

Programarlo en cron diario (recomendado 03:00 UTC):

```cron
0 3 * * * cd /opt/roger && ./scripts/backup.sh /var/backups/roger/ >> /var/log/roger-backup.log 2>&1
```

Retener mínimo 7 días, idealmente 30. Verificar mensualmente que un backup
se restaura limpio en una VM aparte.

---

## 12. Rollback

Si un deploy rompe algo en prod:

```bash
cd /opt/roger
git log --oneline -5                  # ver el commit anterior estable
git checkout <commit_anterior>        # checkout, NO reset
docker compose -f docker-compose.prod.yml --env-file .env.prod build
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

**Ojo con migraciones**: si el deploy que rompió incluía migración nueva, el
rollback de código NO revierte la BD. Para eso:

```bash
docker compose -f docker-compose.prod.yml exec valeria alembic downgrade -1
```

Solo aplicable si la migración es reversible (mirar el `downgrade()` antes).
En caso de duda, restaurar el backup de SQLite previo al deploy.

---

## 13. Logs y observabilidad básica

```bash
# Logs en vivo de un servicio:
docker compose -f docker-compose.prod.yml logs -f valeria

# Últimas N líneas de todos:
docker compose -f docker-compose.prod.yml logs --tail=50

# Filtrar errores:
docker compose -f docker-compose.prod.yml logs valeria | grep -iE "error|exception"
```

Los logs están rotados a `10m × 5` archivos por servicio (definido en
`docker-compose.prod.yml`). No crecen sin tope. Si se necesita más historial,
enviar a journald o un colector externo (no incluido en este corte).

---

## 14. Apagar / reiniciar

```bash
# Parada limpia (mantiene volúmenes Redis/Qdrant):
docker compose -f docker-compose.prod.yml down

# Reinicio sin recrear:
docker compose -f docker-compose.prod.yml restart

# Apagar y BORRAR datos (⚠️ destructivo, perderás Qdrant + Redis cache):
docker compose -f docker-compose.prod.yml down -v
```

Los datos en `./data/`, `./storage/` y `./logs/` están en bind mounts del
host, no se borran con `down -v` (sí los volúmenes nombrados `redis_data` y
`qdrant_data`).

---

## Pendientes que NO se cierran con este runbook

Cosas que requieren coordinación externa antes del deploy real:

- [ ] **Dominio UCN** confirmado por TI UCN — reemplazar `roger.ucn.cl` placeholder
      en `nginx.conf:29`, `.env.prod`, `leila/.../+page.svelte` (10 sitios, ver
      inventario en historial de chat).
- [ ] **Certificado TLS** emitido para ese dominio (formato fullchain.pem + privkey.pem).
- [ ] **DNS A record** apuntando al IP de la VM (lo hace TI UCN).
- [ ] **Apertura de 80/443** en el firewall UCN.
- [ ] **Cuenta SMTP** activa con el correo `noreply@<dominio>` o equivalente.

Sin esos 5, el sistema puede correr en `http://<IP>` para pruebas internas,
pero no es deploy de producción.
