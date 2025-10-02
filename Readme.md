# 🐳 API de Tareas con Docker y PostgreSQL

## 📋 Descripción
API de Tareas desarrollada en Flask con PostgreSQL, dockerizada con múltiples entornos (QA y Producción).

## 📁 Estructura del Proyecto
```
mi-app-tareas/
├── app.py                    # Aplicación Flask principal
├── Dockerfile               # Imagen de la aplicación
├── docker-compose.yml       # Orquestación de servicios
├── requirements.txt         # Dependencias Python
├── index.html              # Frontend simple
├── qa.env                  # Variables de entorno QA
├── prod.env               # Variables de entorno PROD
└── scripts/
    └── create-multiple-postgresql-databases.sh
```

## 🚀 Guía de Instalación y Ejecución

### 1. 🔨 Construir las Imágenes

Primero, construye la imagen de tu aplicación:

```cmd
rem Construir la imagen con tag específico
docker build -t mi-app-tareas:v1.0 .

rem Verificar que se creó correctamente
docker images | findstr mi-app-tareas
```

### 2. 🏃‍♂️ Ejecutar los Contenedores

Levantar todos los servicios con Docker Compose:

```cmd
rem Levantar todos los contenedores en modo detached (background)
docker-compose up -d

rem Ver el estado de los contenedores
docker-compose ps

rem Ver logs de todos los servicios
docker-compose logs -f

rem Ver logs de un servicio específico
docker-compose logs -f app-qa
```

### 3. 🌐 Acceder a la Aplicación

Una vez que los contenedores estén ejecutándose:

#### 📱 **Aplicaciones Web:**
- **QA Environment**: http://localhost:5001
- **Production Environment**: http://localhost:5002

#### 🔍 **Endpoints de la API:**

**QA (Puerto 5001):**
- `GET http://localhost:5001/api` - Información de la API
- `GET http://localhost:5001/health` - Estado de salud
- `GET http://localhost:5001/tareas` - Ver todas las tareas
- `POST http://localhost:5001/tareas` - Crear nueva tarea
- `PUT http://localhost:5001/tareas/<id>/completar` - Completar tarea
- `DELETE http://localhost:5001/tareas/<id>` - Eliminar tarea

**Producción (Puerto 5002):**
- `GET http://localhost:5002/api` - Información de la API
- `GET http://localhost:5002/health` - Estado de salud
- `GET http://localhost:5002/tareas` - Ver todas las tareas
- `POST http://localhost:5002/tareas` - Crear nueva tarea
- `PUT http://localhost:5002/tareas/<id>/completar` - Completar tarea
- `DELETE http://localhost:5002/tareas/<id>` - Eliminar tarea

### 4. 🗄️ Conectarse a las Bases de Datos

#### **📊 Información de conexión:**
```
Host: localhost
Puerto: 5432
Usuario: postgres
Contraseña: password123
```

#### **🎯 Bases de datos disponibles:**
- **`tareas_qa`** - Para el entorno de QA (datos de prueba)
- **`tareas_prod`** - Para el entorno de producción (datos reales)

#### **💻 Desde Windows CMD:**

**Método recomendado - Acceso directo a PostgreSQL:**
```cmd
rem 1. Conectar al contenedor PostgreSQL y acceder a bash
docker-compose exec postgres bash

rem 2. Una vez dentro del contenedor, conectar a PostgreSQL
psql -U postgres

rem 3. Comandos SQL útiles:
rem -- Listar bases de datos
\l

rem -- Conectar a base QA
\c tareas_qa

rem -- Ver tablas
\dt

rem -- Ver datos
SELECT * FROM tareas;

rem -- Conectar a base PROD
\c tareas_prod

rem -- Ver datos de producción
SELECT * FROM tareas;

rem -- Salir de psql
\q

rem -- Salir del contenedor
exit
```

**Método alternativo - Si tienes psql instalado en Windows:**
```cmd
rem Conectar directamente a base QA
psql -h localhost -p 5432 -U postgres -d tareas_qa

rem Conectar directamente a base PROD
psql -h localhost -p 5432 -U postgres -d tareas_prod
```

#### **🖥️ Desde herramientas gráficas (pgAdmin, DBeaver, HeidiSQL):**

**Para base de datos QA:**
```
Nombre conexión: Tareas QA
Host: localhost
Puerto: 5432
Usuario: postgres
Contraseña: password123
Base de datos: tareas_qa
```

**Para base de datos PROD:**
```
Nombre conexión: Tareas PROD
Host: localhost
Puerto: 5432
Usuario: postgres
Contraseña: password123
Base de datos: tareas_prod
```

#### **📋 Comandos SQL útiles:**
```sql
-- Una vez conectado con: docker-compose exec postgres bash → psql -U postgres

-- Listar todas las bases de datos
\l

-- Conectar a base específica
\c tareas_qa

-- Ver todas las tablas
\dt

-- Ver contenido completo de la tabla tareas
SELECT * FROM tareas;

-- Ver solo tareas recientes
SELECT id, titulo, entorno, fecha_creacion FROM tareas ORDER BY fecha_creacion DESC LIMIT 5;

-- Ver tareas por entorno
SELECT * FROM tareas WHERE entorno = 'qa';

-- Contar tareas
SELECT COUNT(*) FROM tareas;

-- Cambiar a base de producción
\c tareas_prod

-- Ver tareas de producción
SELECT * FROM tareas WHERE entorno = 'production';

-- Salir de psql
\q
```

#### **🔍 Verificación rápida desde CMD (una sola línea):**

**Ver datos QA:**
```cmd
docker-compose exec postgres psql -U postgres -d tareas_qa -c "SELECT * FROM tareas;"
```

**Ver datos PROD:**
```cmd
docker-compose exec postgres psql -U postgres -d tareas_prod -c "SELECT * FROM tareas;"
```

**Contar registros por base:**
```cmd
docker-compose exec postgres psql -U postgres -d tareas_qa -c "SELECT COUNT(*) as total_qa FROM tareas;"
docker-compose exec postgres psql -U postgres -d tareas_prod -c "SELECT COUNT(*) as total_prod FROM tareas;"
```

### 5. ✅ Verificar que Todo Funciona

#### **🔍 Verificación Rápida:**
```cmd
rem 1. Verificar contenedores ejecutándose
docker-compose ps

rem 2. Verificar salud de la base de datos
curl http://localhost:5001/health
curl http://localhost:5002/health

rem 3. Verificar API funcionando
curl http://localhost:5001/api
curl http://localhost:5002/api
```

#### **🧪 Prueba Completa:**

1. **Abrir el navegador** en http://localhost:5001 (QA)
2. **Crear una tarea** usando la interfaz web
3. **Verificar en la base de datos QA**:
   ```cmd
   docker exec -it tareas-postgres psql -U postgres -d tareas_qa -c "SELECT * FROM tareas;"
   ```
4. **Repetir para producción** en http://localhost:5002
5. **Verificar en la base de datos PROD**:
   ```cmd
   docker exec -it tareas-postgres psql -U postgres -d tareas_prod -c "SELECT * FROM tareas;"
   ```

#### **📊 Verificar Logs:**
```cmd
rem Logs de todos los servicios
docker-compose logs

rem Logs solo de la aplicación QA
docker-compose logs app-qa

rem Logs solo de PostgreSQL
docker-compose logs postgres

rem Seguir logs en tiempo real
docker-compose logs -f app-qa
```

#### **🎯 Verificar Separación de Datos:**

**Crear tarea en QA y verificar que NO aparece en PROD:**
```cmd
rem 1. Crear tarea en QA (puerto 5001) desde navegador
rem 2. Verificar que existe en base QA:
docker exec -it tareas-postgres psql -U postgres -d tareas_qa -c "SELECT COUNT(*) FROM tareas;"

rem 3. Verificar que NO existe en base PROD:
docker exec -it tareas-postgres psql -U postgres -d tareas_prod -c "SELECT COUNT(*) FROM tareas;"
```

## 🛠️ Comandos Útiles

### **Gestión de Contenedores:**
```cmd
rem Parar todos los servicios
docker-compose down

rem Parar y eliminar volúmenes (CUIDADO: borra datos)
docker-compose down -v

rem Reiniciar un servicio específico
docker-compose restart app-qa

rem Reconstruir y reiniciar
docker-compose up --build -d
```

### **Debugging:**
```cmd
rem Ejecutar comando dentro de contenedor (si tiene bash)
docker exec -it tareas-app-qa bash

rem Si no tiene bash, usar sh
docker exec -it tareas-app-qa sh

rem Ver información del contenedor
docker inspect tareas-app-qa

rem Ver uso de recursos
docker stats
```

### **Base de Datos:**
```cmd
rem Backup de base QA
docker exec tareas-postgres pg_dump -U postgres tareas_qa > backup_qa.sql

rem Backup de base PROD
docker exec tareas-postgres pg_dump -U postgres tareas_prod > backup_prod.sql

rem Restaurar backup (ejemplo)
docker exec -i tareas-postgres psql -U postgres -d tareas_qa < backup_qa.sql
```

## 🔧 Configuración de Entornos

### **QA Environment (qa.env):**
```env
FLASK_ENV=qa
FLASK_DEBUG=true
APP_PORT=5000
DB_HOST=postgres
DB_NAME=tareas_qa
DB_USER=postgres
DB_PASSWORD=password123
DB_PORT=5432
```

### **Production Environment (prod.env):**
```env
FLASK_ENV=production
FLASK_DEBUG=false
APP_PORT=5000
DB_HOST=postgres
DB_NAME=tareas_prod
DB_USER=postgres
DB_PASSWORD=password123
DB_PORT=5432
```

## 🚨 Troubleshooting

### **Problema: Contenedor no inicia**
```cmd
rem Ver logs detallados
docker-compose logs nombre_servicio

rem Verificar configuración
docker-compose config
```

### **Problema: No se puede conectar a la BD**
```cmd
rem Verificar que PostgreSQL está corriendo
docker-compose ps postgres

rem Verificar salud de PostgreSQL
docker exec tareas-postgres pg_isready -U postgres

rem Verificar que las bases existen
docker exec tareas-postgres psql -U postgres -l
```

### **Problema: Puerto ya en uso**
```cmd
rem Verificar qué usa el puerto (Windows)
netstat -an | findstr :5001

rem Cambiar puertos en docker-compose.yml si es necesario
```

### **Problema: Error "imagen no encontrada"**
```cmd
rem Asegúrate de construir primero la imagen
docker build -t mi-app-tareas:v1.0 .

rem O usa build automático en docker-compose.yml
rem build: .
```

## 📝 Notas Importantes

- ⚠️ **Datos Persistentes**: Los datos de PostgreSQL se guardan en el volumen `postgres_data`
- 🔐 **Seguridad**: En producción real, cambiar las credenciales por defecto
- 🌐 **Red**: Todos los servicios están en la red `tareas-network` para comunicarse
- 🔄 **Reinicio**: Los contenedores se reinician automáticamente (`restart: unless-stopped`)

---

**¡Tu aplicación está lista! 🎉**

Accede a:
- **QA**: http://localhost:5001
- **Producción**: http://localhost:5002