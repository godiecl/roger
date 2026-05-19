# ROGER — Guía de deploy en servidor UCN

## Requisitos del servidor

- Docker Engine 24+
- Docker Compose v2 (plugin, no el binario legacy)
- Git
- `sqlite3` (para backups): `apt-get install sqlite3`
- Puertos 80 y 443 abiertos en el firewall

Verificar:
```bash
docker --version          # Docker version 24+
docker compose version    # Docker Compose version v2+
git --version
sqlite3 --version
```

---

## Primera instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/godiecl/roger.git /opt/roger
cd /opt/roger
git checkout DLeon96    # rama de desarrollo activa
```

### 2. Crear el archivo de variables de entorno

```bash
cp .env.example .env
```

Editar `.env` y completar **todos** los valores marcados con `CAMBIAR`:

```bash
nano .env
```

Valores obligatorios:

| Variable | Cómo obtenerla |
|---|---|
| `SECRET_KEY` | `openssl rand -hex 32` |
| `REDIS_PASSWORD` | `openssl rand -base64 24` |
| `GROQ_API_KEY` | Crear cuenta gratuita en [console.groq.com](https://console.groq.com) |
| `SMTP_USER` / `SMTP_PASSWORD` | Credenciales del correo UCN institucional |
| `FRONTEND_URL` | IP del servidor, ej. `http://192.168.1.100` |

### 3. Crear directorios de datos

```bash
mkdir -p /opt/roger/data /opt/roger/storage/images
```

### 4. (Cuando TI UCN entregue el cert) Copiar certificado TLS

```bash
mkdir -p /etc/roger/certs
cp roger.crt /etc/roger/certs/
cp roger.key /etc/roger/certs/
chmod 600 /etc/roger/certs/roger.key
```

Además, editar `nginx.conf` y reemplazar `roger.ucn.cl` con el dominio real.

### 5. Construir las imágenes

```bash
cd /opt/roger
docker compose build
```

La primera vez tarda ~5–10 minutos. Los builds posteriores son más rápidos por el caché de capas.

### 6. Aplicar migraciones de base de datos

```bash
docker compose run --rm valeria-migrate
```

Debe mostrar algo como:
```
INFO  [alembic.runtime.migration] Running upgrade -> 001, initial_tables
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, add_narratives_table
...
```

### 7. Levantar todos los servicios

```bash
docker compose up -d
```

### 8. Crear el usuario administrador

```bash
docker compose exec valeria python scripts/create_admin.py
```

Ingresa el email, nombre de usuario y contraseña del primer admin cuando lo pida.

### 9. Verificar que todo funciona

```bash
# Health del backend
curl http://localhost/health

# Estado de los contenedores
docker compose ps

# Logs en tiempo real
docker compose logs -f
```

La aplicación estará disponible en `http://IP-DEL-SERVIDOR`.

---

## Orden de arranque automático

Los servicios arrancan en este orden (definido por `depends_on` en docker-compose.yml):

```
redis  →  valeria-migrate  →  valeria  →  leila  →  nginx
```

`valeria-migrate` corre una sola vez y se detiene. Si ya aplicó las migraciones,
en el siguiente `docker compose up` detecta que no hay nada nuevo y sale en segundos.

---

## Deploys posteriores (actualizar código)

```bash
cd /opt/roger
git pull origin DLeon96
docker compose build
docker compose run --rm valeria-migrate   # aplica migraciones nuevas si las hay
docker compose up -d
```

Docker Compose reemplaza solo los contenedores cuya imagen cambió. Redis y sus datos no se tocan.

---

## Configurar backup automático

```bash
# Copiar el script al servidor
chmod +x /opt/roger/scripts/backup.sh

# Crear directorio de backups
mkdir -p /opt/roger/backups

# Agregar al cron (ejecutar a las 03:00 cada día)
crontab -e
```

Agregar esta línea:
```
0 3 * * * /opt/roger/scripts/backup.sh >> /var/log/roger-backup.log 2>&1
```

Verificar que funciona:
```bash
/opt/roger/scripts/backup.sh
ls -lh /opt/roger/backups/
```

---

## Comandos útiles

```bash
# Ver estado de todos los servicios
docker compose ps

# Ver logs de un servicio específico
docker compose logs -f valeria
docker compose logs -f nginx

# Reiniciar un servicio sin afectar los demás
docker compose restart valeria

# Detener todo (sin borrar datos)
docker compose down

# Detener y borrar volúmenes (DESTRUCTIVO — borra Redis)
docker compose down -v

# Entrar al contenedor del backend
docker compose exec valeria bash

# Correr un script de utilidad
docker compose exec valeria python scripts/seed_db.py
docker compose exec valeria python scripts/index_knowledge_base.py
```

---

## Resolución de problemas

**El backend no arranca:**
```bash
docker compose logs valeria
# Revisar que .env tiene SECRET_KEY y GROQ_API_KEY completos
```

**Redis no conecta:**
```bash
docker compose logs redis
# Verificar que REDIS_PASSWORD en .env coincide con el valor en redis command
```

**nginx da 502 Bad Gateway:**
```bash
# Esperar a que valeria y leila pasen el healthcheck (puede tardar ~60s en frío)
docker compose ps
# Cuando ambos muestren "healthy", nginx debería funcionar
```

**Migraciones fallan:**
```bash
docker compose run --rm valeria-migrate
# Leer el error. Generalmente es DATABASE_URL mal formada o falta de permisos en ./data/
```

**No puedo escribir en ./data:**
```bash
# En el servidor
ls -la /opt/roger/data/
# Si es propiedad de root y docker no puede escribir:
chmod 777 /opt/roger/data
```

---

## Activar TLS cuando llegue el dominio UCN

1. Recibir `roger.crt` y `roger.key` de TI UCN
2. Copiarlos:
   ```bash
   mkdir -p /etc/roger/certs
   cp roger.crt /etc/roger/certs/
   cp roger.key /etc/roger/certs/
   chmod 600 /etc/roger/certs/roger.key
   ```
3. Editar `nginx.conf`: reemplazar `roger.ucn.cl` con el dominio real
4. Editar `.env`: actualizar `FRONTEND_URL=https://dominio-real.ucn.cl`
5. Reiniciar nginx:
   ```bash
   docker compose restart nginx
   ```

---

## Desarrollo local (sin Docker)

Ver instrucciones en `valeria/README.md` y `leila/README.md`.
Stack dev: `uvicorn app.main:app --reload` + `npm run dev`.
