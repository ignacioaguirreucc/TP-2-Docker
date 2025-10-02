# decisiones.md

## 🎯 Decisiones Técnicas del Proyecto

### 1. Elección de la Aplicación
**Aplicación:** Gestor de Tareas (Task Manager)  
**Tecnología:** Flask (Python) + PostgreSQL

**Justificación:**
- **Sencillez:** API REST con operaciones CRUD básicas ideal para demostrar containerización
- **Frontend integrado:** HTML/CSS/JS vanilla incluido para verificación visual
- **Stack común:** Python+PostgreSQL es ampliamente usado en producción
- **Multiambiente:** Diseñada específicamente para soportar QA y PROD mediante variables de entorno

---

### 2. Imagen Base del Dockerfile
**Elección:** `python:3.11-slim`

**Justificación:**
- **Oficial:** Mantenida por Docker y la comunidad Python
- **Liviana:** Versión `slim` reduce tamaño (~150MB vs ~900MB de la completa)
- **Compatibilidad:** Python 3.11 es estable y compatible con psycopg2-binary
- **Seguridad:** Actualizaciones regulares de seguridad

---

### 3. Base de Datos
**Elección:** PostgreSQL 15 Alpine

**Justificación:**
- **Robustez:** Base de datos empresarial con soporte completo para transacciones
- **Multibase:** Soporta múltiples bases de datos en una sola instancia (tareas_qa y tareas_prod)
- **Alpine:** Imagen reducida (~80MB vs ~150MB) manteniendo funcionalidad completa
- **Healthcheck:** Permite verificar disponibilidad antes de iniciar aplicaciones

---

### 4. Estructura del Dockerfile

**Decisiones clave:**
```dockerfile
FROM python:3.11-slim          # Base optimizada
WORKDIR /app                    # Organización clara
COPY requirements.txt .         # Cache de dependencias
RUN pip install --no-cache-dir  # Reduce tamaño de imagen
COPY app.py index.html .        # Solo archivos necesarios
EXPOSE 5000                     # Documentación del puerto
ENV PYTHONUNBUFFERED=1          # Logs inmediatos
CMD ["python", "app.py"]        # Ejecución directa
```

**Orden de instrucciones:** Maximiza cache de Docker copiando dependencias antes que el código fuente

---

### 5. Configuración QA vs PROD

**Variables de entorno:**
```bash
# qa.env
FLASK_ENV=qa
FLASK_DEBUG=true      # Logs detallados
DB_NAME=tareas_qa     # Base datos separada

# prod.env
FLASK_ENV=production
FLASK_DEBUG=false     # Sin debug en producción
DB_NAME=tareas_prod   # Base datos aislada
```

**Ventajas:**
- **Misma imagen:** `mi-app-tareas:v1.0` funciona en ambos entornos
- **Aislamiento:** Bases de datos completamente separadas
- **Logging diferenciado:** DEBUG en QA, WARNING en PROD
- **Puertos distintos:** 5001 (QA) y 5002 (PROD) para acceso simultáneo

---

### 6. Estrategia de Persistencia

**Volumen PostgreSQL:**
```yaml
volumes:
  postgres_data:
    driver: local
    labels:
      - "backup=daily"
```

**Ventajas:**
- **Persistencia:** Datos sobreviven a reinicios/recreaciones de contenedores
- **Performance:** Volúmenes nativos de Docker son más rápidos que bind mounts
- **Portabilidad:** Funciona igual en Windows, Mac y Linux

---

### 7. Versionado y Publicación

**Estrategia de tags:**
```bash
mi-app-tareas:latest    # Desarrollo continuo
mi-app-tareas:v1.0      # Versión estable
mi-app-tareas:v1.1      # Próxima versión
```

**Convención:** [SemVer](https://semver.org/)
- **Major (v2.0):** Cambios incompatibles (nueva base de datos, nuevo framework)
- **Minor (v1.1):** Nuevas funcionalidades compatibles (nuevo endpoint)
- **Patch (v1.0.1):** Correcciones de bugs

**Publicación en Docker Hub:**
```bash
docker build -t mi-app-tareas:v1.0 .
docker tag mi-app-tareas:v1.0 usuario/mi-app-tareas:v1.0
docker push usuario/mi-app-tareas:v1.0
```

---

### 8. Evidencia de Funcionamiento

**✅ Aplicaciones corriendo:**
- QA: http://localhost:5001 (Badge amarillo "QA")
- PROD: http://localhost:5002 (Badge rojo "PRODUCTION")

**✅ Conexión a base de datos:**
```json
GET /health
{
  "status": "healthy",
  "database": "connected",
  "entorno": "qa"
}
```

**✅ Persistencia de datos:**
1. Crear tarea → Detener contenedor → Reiniciar → Tarea sigue presente
2. Volumen `postgres_data` conserva todas las tablas y registros

**✅ Aislamiento entre entornos:**
- Tareas creadas en QA NO aparecen en PROD
- Cada ambiente tiene su propia base de datos independiente

---

### 9. Problemas y Soluciones

| Problema | Causa | Solución |
|----------|-------|----------|
| Error conexión DB | `DB_HOST=localhost` en .env | Cambiar a `DB_HOST=postgres` (nombre del servicio) |
| Puerto ya en uso | Conflicto con otros servicios | Usar puertos 5001/5002 en lugar de 5000 |
| Tareas no persisten | Sin volumen configurado | Agregar `postgres_data:/var/lib/postgresql/data` |
| No se crean múltiples BD | PostgreSQL solo crea DB por defecto | Script `create-multiple-postgresql-databases.sh` |

---

### 10. Ventajas del Diseño

✅ **Reproducibilidad:** `docker-compose up` levanta todo el stack en cualquier máquina  
✅ **Escalabilidad:** Fácil agregar nuevos entornos (staging, demo)  
✅ **Mantenibilidad:** Configuración centralizada en archivos `.env`  
✅ **Seguridad:** Credenciales fuera del código, separación por ambientes  
✅ **Portabilidad:** Funciona idéntico en desarrollo, QA y producción
