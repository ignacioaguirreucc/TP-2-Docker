from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from datetime import datetime
import os
import logging

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)

# Configuración por entorno
ENVIRONMENT = os.getenv('FLASK_ENV', 'development')
DEBUG_MODE = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
APP_PORT = int(os.getenv('APP_PORT', '5000'))

# Configuración de logging según entorno
if ENVIRONMENT == 'production':
    logging.basicConfig(level=logging.WARNING)
    app.logger.setLevel(logging.WARNING)
elif ENVIRONMENT == 'qa':
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

# Configuración de base de datos desde variables de entorno
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'tareas_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password123'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        app.logger.info(f"✅ Conexión exitosa a BD: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        return conn
    except psycopg2.Error as e:
        app.logger.error(f"❌ Error conectando a la base de datos: {e}")
        return None

def init_db():
    """Inicializar base de datos y crear tabla si no existe"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tareas (
                    id SERIAL PRIMARY KEY,
                    titulo VARCHAR(200) NOT NULL,
                    descripcion TEXT,
                    completada BOOLEAN DEFAULT FALSE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_completada TIMESTAMP,
                    entorno VARCHAR(20) DEFAULT %s
                )
            ''', (ENVIRONMENT,))
            conn.commit()
            cur.close()
            conn.close()
            app.logger.info("✅ Base de datos inicializada correctamente")
        except psycopg2.Error as e:
            app.logger.error(f"❌ Error inicializando base de datos: {e}")

@app.route('/')
def frontend():
    """Servir el frontend"""
    return send_from_directory('.', 'index.html')

@app.route('/api')
def inicio():
    """Información de la API"""
    return {
        "mensaje": f"🚀 API de Tareas funcionando en {ENVIRONMENT.upper()}!",
        "version": "3.0",
        "entorno": ENVIRONMENT,
        "debug": DEBUG_MODE,
        "puerto": APP_PORT,
        "base_datos": {
            "host": DB_CONFIG['host'],
            "database": DB_CONFIG['database'],
            "puerto": DB_CONFIG['port']
        },
        "endpoints": {
            "GET /": "Frontend de la aplicación",
            "GET /api": "Información de la API",
            "GET /health": "Estado de salud del servicio",
            "GET /tareas": "Ver todas las tareas",
            "POST /tareas": "Crear nueva tarea",
            "PUT /tareas/<id>/completar": "Completar una tarea",
            "DELETE /tareas/<id>": "Eliminar una tarea"
        }
    }

@app.route('/health')
def health_check():
    """Endpoint de salud para monitoreo"""
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
            return jsonify({
                "status": "healthy",
                "entorno": ENVIRONMENT,
                "database": "connected",
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "status": "unhealthy",
                "entorno": ENVIRONMENT,
                "database": "disconnected",
                "timestamp": datetime.now().isoformat()
            }), 503
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "entorno": ENVIRONMENT,
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route('/tareas', methods=['GET'])
def obtener_tareas():
    """Obtener todas las tareas desde PostgreSQL"""
    app.logger.info(f"GET /tareas - Entorno: {ENVIRONMENT}")
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a base de datos"}), 500
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM tareas ORDER BY fecha_creacion DESC')
        tareas = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convertir datetime a string para JSON
        for tarea in tareas:
            if tarea['fecha_creacion']:
                tarea['fecha_creacion'] = tarea['fecha_creacion'].isoformat()
            if tarea['fecha_completada']:
                tarea['fecha_completada'] = tarea['fecha_completada'].isoformat()
        
        app.logger.info(f"✅ Consultadas {len(tareas)} tareas")
        return jsonify({
            "tareas": tareas,
            "total": len(tareas),
            "entorno": ENVIRONMENT
        })
    except psycopg2.Error as e:
        app.logger.error(f"❌ Error consultando tareas: {e}")
        return jsonify({"error": f"Error consultando tareas: {str(e)}"}), 500

@app.route('/tareas', methods=['POST'])
def crear_tarea():
    """Crear nueva tarea en PostgreSQL"""
    datos = request.get_json()
    app.logger.info(f"POST /tareas - Entorno: {ENVIRONMENT} - Datos: {datos}")
    
    if not datos or 'titulo' not in datos:
        return jsonify({"error": "El título es obligatorio"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a base de datos"}), 500
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('''
            INSERT INTO tareas (titulo, descripcion, entorno) 
            VALUES (%s, %s, %s) 
            RETURNING *
        ''', (datos['titulo'], datos.get('descripcion', ''), ENVIRONMENT))
        
        nueva_tarea = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        # Convertir datetime a string
        if nueva_tarea['fecha_creacion']:
            nueva_tarea['fecha_creacion'] = nueva_tarea['fecha_creacion'].isoformat()
        
        app.logger.info(f"✅ Tarea creada: ID {nueva_tarea['id']}")
        return jsonify({
            "mensaje": "Tarea creada exitosamente",
            "tarea": nueva_tarea,
            "entorno": ENVIRONMENT
        }), 201
    except psycopg2.Error as e:
        app.logger.error(f"❌ Error creando tarea: {e}")
        return jsonify({"error": f"Error creando tarea: {str(e)}"}), 500

@app.route('/tareas/<int:tarea_id>/completar', methods=['PUT'])
def completar_tarea(tarea_id):
    """Completar tarea en PostgreSQL"""
    app.logger.info(f"PUT /tareas/{tarea_id}/completar - Entorno: {ENVIRONMENT}")
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a base de datos"}), 500
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('''
            UPDATE tareas 
            SET completada = TRUE, fecha_completada = CURRENT_TIMESTAMP 
            WHERE id = %s 
            RETURNING *
        ''', (tarea_id,))
        
        tarea = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if tarea:
            # Convertir datetime a string
            if tarea['fecha_creacion']:
                tarea['fecha_creacion'] = tarea['fecha_creacion'].isoformat()
            if tarea['fecha_completada']:
                tarea['fecha_completada'] = tarea['fecha_completada'].isoformat()
                
            app.logger.info(f"✅ Tarea {tarea_id} completada")
            return jsonify({
                "mensaje": "Tarea completada",
                "tarea": tarea,
                "entorno": ENVIRONMENT
            })
        else:
            return jsonify({"error": "Tarea no encontrada"}), 404
            
    except psycopg2.Error as e:
        app.logger.error(f"❌ Error completando tarea: {e}")
        return jsonify({"error": f"Error completando tarea: {str(e)}"}), 500

@app.route('/tareas/<int:tarea_id>', methods=['DELETE'])
def eliminar_tarea(tarea_id):
    """Eliminar tarea de PostgreSQL"""
    app.logger.info(f"DELETE /tareas/{tarea_id} - Entorno: {ENVIRONMENT}")
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a base de datos"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute('DELETE FROM tareas WHERE id = %s', (tarea_id,))
        rows_affected = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        
        if rows_affected > 0:
            app.logger.info(f"✅ Tarea {tarea_id} eliminada")
            return jsonify({"mensaje": "Tarea eliminada exitosamente", "entorno": ENVIRONMENT})
        else:
            return jsonify({"error": "Tarea no encontrada"}), 404
            
    except psycopg2.Error as e:
        app.logger.error(f"❌ Error eliminando tarea: {e}")
        return jsonify({"error": f"Error eliminando tarea: {str(e)}"}), 500

if __name__ == '__main__':
    print(f"🚀 Iniciando API de Tareas en entorno: {ENVIRONMENT.upper()}")
    print(f"🔧 Debug: {DEBUG_MODE}")
    print(f"🌐 Puerto: {APP_PORT}")
    print(f"📊 Inicializando base de datos...")
    init_db()
    print(f"📝 Accede a http://localhost:{APP_PORT} para usar la aplicación")
    app.run(debug=DEBUG_MODE, host='0.0.0.0', port=APP_PORT)