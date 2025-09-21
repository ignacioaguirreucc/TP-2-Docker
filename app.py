from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os

# Crear la aplicación Flask
app = Flask(__name__)

# Habilitar CORS para que el frontend pueda conectarse
CORS(app)

# Lista para almacenar las tareas (en memoria por ahora)
tareas = []
contador_id = 1

@app.route('/')
def frontend():
    """Servir el frontend"""
    return send_from_directory('..', 'index.html')

@app.route('/api')
def inicio():
    """Página de inicio con información de la API"""
    return {
        "mensaje": "🚀 API de Tareas funcionando!",
        "version": "1.0",
        "endpoints": {
            "GET /": "Frontend de la aplicación",
            "GET /api": "Información de la API",
            "GET /tareas": "Ver todas las tareas",
            "POST /tareas": "Crear nueva tarea",
            "PUT /tareas/<id>/completar": "Completar una tarea",
            "DELETE /tareas/<id>": "Eliminar una tarea"
        }
    }

@app.route('/tareas', methods=['GET'])
def obtener_tareas():
    """Obtener todas las tareas"""
    return jsonify({
        "tareas": tareas,
        "total": len(tareas)
    })

@app.route('/tareas', methods=['POST'])
def crear_tarea():
    """Crear una nueva tarea"""
    global contador_id
    
    datos = request.get_json()
    
    if not datos or 'titulo' not in datos:
        return jsonify({"error": "El título es obligatorio"}), 400
    
    nueva_tarea = {
        "id": contador_id,
        "titulo": datos['titulo'],
        "descripcion": datos.get('descripcion', ''),
        "completada": False,
        "fecha_creacion": datetime.now().isoformat()
    }
    
    tareas.append(nueva_tarea)
    contador_id += 1
    
    return jsonify({
        "mensaje": "Tarea creada exitosamente",
        "tarea": nueva_tarea
    }), 201

@app.route('/tareas/<int:tarea_id>/completar', methods=['PUT'])
def completar_tarea(tarea_id):
    """Marcar una tarea como completada"""
    for tarea in tareas:
        if tarea['id'] == tarea_id:
            tarea['completada'] = True
            tarea['fecha_completada'] = datetime.now().isoformat()
            return jsonify({
                "mensaje": "Tarea completada",
                "tarea": tarea
            })
    
    return jsonify({"error": "Tarea no encontrada"}), 404

@app.route('/tareas/<int:tarea_id>', methods=['DELETE'])
def eliminar_tarea(tarea_id):
    """Eliminar una tarea"""
    global tareas
    tareas_originales = len(tareas)
    tareas = [t for t in tareas if t['id'] != tarea_id]
    
    if len(tareas) < tareas_originales:
        return jsonify({"mensaje": "Tarea eliminada exitosamente"})
    else:
        return jsonify({"error": "Tarea no encontrada"}), 404

if __name__ == '__main__':
    print("🚀 Iniciando API de Tareas...")
    print("📝 Accede a http://localhost:5000 para ver la API")
    app.run(debug=True, host='0.0.0.0', port=5000)