from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://paolaco1308_db_user:admin321@mediasuperior.ephlbzn.mongodb.net/mediasuperior")
try:
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=False,
        serverSelectionTimeoutMS=10000
    )
    db = client.get_default_database()
    print("Conexión segura establecida con MongoDB Atlas")
except Exception as e:
    print("Conexión segura falló, intentando modo escolar...")
    try:
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=10000
        )
        db = client.get_default_database()
        print("Conexión establecida con MongoDB Atlas (modo escolar sin SSL)")
    except Exception as e:
        db = None
        print("No se pudo conectar con MongoDB Atlas:", e)
    
    # Configurar colecciones
    users_collection = db.users
    eventos_collection = db.eventos
    tareas_collection = db.tareas
    mensajes_collection = db.mensajes
    ajustes_collection = db.ajustes
    
    # Crear índices
    users_collection.create_index([("email", 1)], unique=True)
    eventos_collection.create_index([("user_id", 1), ("fecha", 1)])
    tareas_collection.create_index([("user_id", 1), ("estado", 1)])
    ajustes_collection.create_index([("user_id", 1)], unique=True)
    
except Exception as e:
    print(f"❌ Error conectando a MongoDB: {e}")
    print("⚠️ Usando modo desarrollo sin base de datos")
    users_collection = None
    eventos_collection = None
    tareas_collection = None
    mensajes_collection = None
    ajustes_collection = None

# Datos de ejemplo
ANUNCIOS_RECIENTES = [
    {"titulo": "Convocatoria Becas 2025", "emisor": "Control Escolar", "fecha": "15/ENE/2026", "prioridad": "alta"},
    {"titulo": "Inicio de Clases 2026", "emisor": "Dirección Académica", "fecha": "10/ENE/2026", "prioridad": "alta"},
    {"titulo": "Período de Inscripción", "emisor": "Control Escolar", "fecha": "05/DIC/2025", "prioridad": "media"},
    {"titulo": "Vacaciones de Diciembre", "emisor": "Administración", "fecha": "20/DIC/2025", "prioridad": "baja"}
]

HORARIOS_TUTORIA = {
    "Grupo A": "Lunes 10:00 AM",
    "Grupo B": "Miércoles 2:00 PM",
    "Grupo C": "Viernes 11:00 AM",
    "Asesorías Individuales": "Jueves 3:00-5:00 PM"
}

MATERIAS = [
    {"nombre": "Programación Avanzada", "horario": "Lun/Mie 8:00-10:00", "profesor": "Lic. García", "calificacion": 8.5, "aula": "Lab 3"},
    {"nombre": "Matemáticas Discretas", "horario": "Mar/Jue 10:00-12:00", "profesor": "Mtro. López", "calificacion": 7.5, "aula": "Aula 201"},
    {"nombre": "Base de Datos", "horario": "Mie/Vie 2:00-4:00", "profesor": "Prof. Martínez", "calificacion": 9.0, "aula": "Lab 2"},
    {"nombre": "Inglés Técnico", "horario": "Lun/Mie 4:00-6:00", "profesor": "Mrs. Smith", "calificacion": 8.0, "aula": "Aula 105"},
    {"nombre": "Desarrollo Web", "horario": "Mar/Jue 8:00-10:00", "profesor": "Ing. Rodríguez", "calificacion": 9.5, "aula": "Lab 1"},
    {"nombre": "Ética Profesional", "horario": "Vie 10:00-12:00", "profesor": "Dra. Fernández", "calificacion": 8.8, "aula": "Aula 302"}
]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' in session:
        if users_collection:
            try:
                user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
                if user:
                    return {
                        'id': str(user['_id']),
                        'nombre_completo': user.get('nombre', 'Usuario'),
                        'email': user.get('email', ''),
                        'especialidad': user.get('especialidad', 'Programación'),
                        'semestre': str(user.get('semestre', '1')),
                        'grupo': user.get('grupo', 'A'),
                        'turno': user.get('turno', 'Matutino'),
                        'numero_control': user.get('numero_control', ''),
                        'curp': user.get('curp', ''),
                        'fecha_registro': user.get('fecha_registro', datetime.now()),
                        'avatar': user.get('avatar', 'default.png')
                    }
            except:
                pass
        
        # Modo demo si no hay conexión a DB
        return {
            'id': session.get('user_id', 'demo_id'),
            'nombre_completo': session.get('user_name', 'Camila Corona'),
            'email': session.get('user_email', 'camila@ejemplo.com'),
            'especialidad': 'Programación',
            'semestre': '5',
            'grupo': 'B',
            'turno': 'Vespertino',
            'numero_control': '2025001',
            'curp': 'CORM950515HDFRNL09',
            'avatar': 'default.png'
        }
    return None

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Por favor ingresa email y contraseña', 'error')
            return render_template('login.html')
        
        try:
            if users_collection:
                user = users_collection.find_one({'email': email})
                
                if user and check_password_hash(user['password'], password):
                    session['user_id'] = str(user['_id'])
                    session['user_name'] = user['nombre']
                    session['user_email'] = user['email']
                    
                    # Crear ajustes por defecto si no existen
                    if ajustes_collection:
                        ajustes_exist = ajustes_collection.find_one({'user_id': str(user['_id'])})
                        if not ajustes_exist:
                            ajustes_por_defecto = {
                                'user_id': str(user['_id']),
                                'notif_anuncios': True,
                                'notif_tareas': True,
                                'notif_tutoria': True,
                                'notif_email': False,
                                'tema': 'claro',
                                'font_size': 'medium',
                                'animaciones': True,
                                'perfil_publico': True,
                                'mostrar_email': False,
                                'mostrar_calificaciones': False,
                                'fecha_actualizacion': datetime.now()
                            }
                            ajustes_collection.insert_one(ajustes_por_defecto)
                    
                    flash('¡Inicio de sesión exitoso!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Credenciales incorrectas', 'error')
            else:
                # Modo demo
                if email == "demo@ejemplo.com" and password == "demo123":
                    session['user_id'] = 'demo_user_id'
                    session['user_name'] = 'Camila Corona'
                    session['user_email'] = 'demo@ejemplo.com'
                    flash('¡Inicio de sesión exitoso (modo demo)!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Credenciales incorrectas', 'error')
                    
        except Exception as e:
            print(f"Error en login: {e}")
            flash('Error en el servidor. Por favor intenta más tarde.', 'error')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not nombre or not email or not password:
            flash('Todos los campos son requeridos', 'error')
            return render_template('registro.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('registro.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('registro.html')
        
        try:
            if users_collection:
                if users_collection.find_one({'email': email}):
                    flash('El correo ya está registrado', 'error')
                    return render_template('registro.html')
                
                hashed_password = generate_password_hash(password)
                nuevo_usuario = {
                    'nombre': nombre,
                    'email': email,
                    'password': hashed_password,
                    'especialidad': request.form.get('especialidad', 'Programación'),
                    'semestre': int(request.form.get('semestre', 1)),
                    'grupo': request.form.get('grupo', 'A'),
                    'turno': request.form.get('turno', 'Matutino'),
                    'fecha_registro': datetime.now(),
                    'avatar': 'default.png',
                    'activo': True
                }
                
                result = users_collection.insert_one(nuevo_usuario)
                user_id = str(result.inserted_id)
                
                # Crear ajustes por defecto
                if ajustes_collection:
                    ajustes_por_defecto = {
                        'user_id': user_id,
                        'notif_anuncios': True,
                        'notif_tareas': True,
                        'notif_tutoria': True,
                        'notif_email': False,
                        'tema': 'claro',
                        'font_size': 'medium',
                        'animaciones': True,
                        'perfil_publico': True,
                        'mostrar_email': False,
                        'mostrar_calificaciones': False,
                        'fecha_actualizacion': datetime.now()
                    }
                    ajustes_collection.insert_one(ajustes_por_defecto)
                
                flash('¡Registro exitoso! Por favor inicia sesión', 'success')
                return redirect(url_for('login'))
            else:
                flash('¡Registro exitoso! Por favor inicia sesión', 'success')
                return redirect(url_for('login'))
                
        except Exception as e:
            print(f"Error en registro: {e}")
            flash('Error en el servidor. Por favor intenta más tarde.', 'error')
    
    return render_template('registro.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def index():
    alumno = get_current_user()
    
    eventos_proximos = []
    if eventos_collection and alumno:
        hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        eventos_db = eventos_collection.find({
            'user_id': alumno['id'],
            'fecha': {'$gte': hoy.strftime('%Y-%m-%d')}
        }).sort('fecha', 1).limit(5)
        
        for evento in eventos_db:
            evento['_id'] = str(evento['_id'])
            eventos_proximos.append(evento)
    
    return render_template("index.html", 
                         alumno=alumno,
                         anuncios=ANUNCIOS_RECIENTES[:3],
                         horarios_tutoria=HORARIOS_TUTORIA,
                         eventos_proximos=eventos_proximos)

@app.route("/perfil")
@login_required
def perfil():
    alumno = get_current_user()
    return render_template("perfil.html", alumno=alumno)

@app.route("/agenda")
@login_required
def agenda():
    alumno = get_current_user()
    
    eventos_mes = []
    if eventos_collection and alumno:
        hoy = datetime.now()
        primer_dia_mes = hoy.replace(day=1)
        ultimo_dia_mes = hoy.replace(day=28) + timedelta(days=4)
        ultimo_dia_mes = ultimo_dia_mes.replace(day=1) - timedelta(days=1)
        
        eventos_db = eventos_collection.find({
            'user_id': alumno['id'],
            'fecha': {
                '$gte': primer_dia_mes.strftime('%Y-%m-%d'),
                '$lte': ultimo_dia_mes.strftime('%Y-%m-%d')
            }
        })
        
        for evento in eventos_db:
            evento['_id'] = str(evento['_id'])
            eventos_mes.append(evento)
    
    return render_template("agenda.html", 
                         alumno=alumno, 
                         eventos=eventos_mes,
                         mes_actual=datetime.now().month,
                         año_actual=datetime.now().year)

@app.route("/materias")
@login_required
def materias():
    alumno = get_current_user()
    return render_template("materias.html", 
                         materias=MATERIAS, 
                         alumno=alumno)

@app.route("/anuncios")
@login_required
def anuncios():
    alumno = get_current_user()
    return render_template("anuncios.html", 
                         anuncios=ANUNCIOS_RECIENTES, 
                         alumno=alumno)

@app.route("/tutoria")
@login_required
def tutoria():
    alumno = get_current_user()
    
    historial_tutoria = [
        {"fecha": "Viernes 10/Ene", "tema": "Planificación Proyecto Final", "completada": True},
        {"fecha": "Miércoles 08/Ene", "tema": "Revisión de Avances", "completada": True},
        {"fecha": "Viernes 03/Ene", "tema": "Metodologías Ágiles", "completada": True},
        {"fecha": "Miércoles 18/Dic", "tema": "Preparación Exámenes", "completada": True}
    ]
    
    return render_template("tutoria.html", 
                         horarios=HORARIOS_TUTORIA,
                         historial=historial_tutoria,
                         alumno=alumno)

@app.route("/compañeros")
@login_required
def compañeros():
    alumno = get_current_user()
    
    compañeros = []
    if users_collection and alumno:
        try:
            compañeros_db = users_collection.find({
                'especialidad': alumno['especialidad'],
                'semestre': int(alumno['semestre']),
                '_id': {'$ne': ObjectId(alumno['id'])},
                'activo': True
            }).limit(20)
            
            for comp in compañeros_db:
                comp['_id'] = str(comp['_id'])
                comp.pop('password', None)
                comp.pop('email', None)
                compañeros.append(comp)
        except:
            pass
    
    return render_template("compañeros.html", 
                         alumno=alumno,
                         compañeros=compañeros)

@app.route("/ajustes", methods=["GET", "POST"])
@login_required
def ajustes():
    alumno = get_current_user()
    
    ajustes_actuales = {}
    if ajustes_collection and alumno:
        ajustes_db = ajustes_collection.find_one({'user_id': alumno['id']})
        if ajustes_db:
            ajustes_actuales = ajustes_db
    
    if request.method == "POST":
        try:
            nuevos_ajustes = {
                'user_id': alumno['id'],
                'notif_anuncios': request.form.get('notif_anuncios') == 'on',
                'notif_tareas': request.form.get('notif_tareas') == 'on',
                'notif_tutoria': request.form.get('notif_tutoria') == 'on',
                'notif_email': request.form.get('notif_email') == 'on',
                'tema': request.form.get('tema', 'claro'),
                'font_size': request.form.get('font_size', 'medium'),
                'animaciones': request.form.get('animaciones') == 'on',
                'perfil_publico': request.form.get('perfil_publico') == 'on',
                'mostrar_email': request.form.get('mostrar_email') == 'on',
                'mostrar_calificaciones': request.form.get('mostrar_calificaciones') == 'on',
                'fecha_actualizacion': datetime.now()
            }
            
            if ajustes_collection and alumno:
                ajustes_collection.update_one(
                    {'user_id': alumno['id']},
                    {'$set': nuevos_ajustes},
                    upsert=True
                )
            
            flash("Ajustes guardados correctamente", "success")
            return redirect(url_for("ajustes"))
            
        except Exception as e:
            print(f"Error guardando ajustes: {e}")
            flash("Error al guardar ajustes", "error")
    
    return render_template("ajustes.html", 
                         alumno=alumno,
                         ajustes=ajustes_actuales)

@app.route("/editar_perfil", methods=["GET", "POST"])
@login_required
def editar_perfil():
    alumno = get_current_user()
    
    if request.method == "POST":
        try:
            if users_collection and alumno:
                datos_actualizados = {
                    'nombre': request.form.get("nombre_completo", alumno['nombre_completo']),
                    'especialidad': request.form.get("especialidad", alumno['especialidad']),
                    'semestre': int(request.form.get("semestre", alumno['semestre'])),
                    'grupo': request.form.get("grupo", alumno['grupo']),
                    'turno': request.form.get("turno", alumno['turno']),
                    'curp': request.form.get("curp", alumno.get('curp', '')),
                    'numero_control': request.form.get("numero_control", alumno.get('numero_control', '')),
                    'fecha_actualizacion': datetime.now()
                }
                
                users_collection.update_one(
                    {'_id': ObjectId(alumno['id'])},
                    {'$set': datos_actualizados}
                )
                
                session['user_name'] = datos_actualizados['nombre']
            
            flash("Perfil actualizado correctamente", "success")
            return redirect(url_for("perfil"))
            
        except Exception as e:
            print(f"Error actualizando perfil: {e}")
            flash("Error al actualizar el perfil", "error")
    
    return render_template("editar_perfil.html", alumno=alumno)

# ============= API ROUTES =============

@app.route("/api/eliminar_cuenta", methods=["POST"])
@login_required
def eliminar_cuenta():
    alumno = get_current_user()
    
    try:
        if users_collection and alumno:
            users_collection.update_one(
                {'_id': ObjectId(alumno['id'])},
                {'$set': {'activo': False, 'fecha_eliminacion': datetime.now()}}
            )
        
        # Eliminar datos relacionados
        if eventos_collection and alumno:
            eventos_collection.delete_many({'user_id': alumno['id']})
        
        if tareas_collection and alumno:
            tareas_collection.delete_many({'user_id': alumno['id']})
        
        if ajustes_collection and alumno:
            ajustes_collection.delete_one({'user_id': alumno['id']})
        
        session.clear()
        
        return jsonify({'success': True, 'redirect': url_for('login')})
        
    except Exception as e:
        print(f"Error eliminando cuenta: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/eliminar_tarea/<tarea_id>", methods=["DELETE"])
@login_required
def eliminar_tarea(tarea_id):
    alumno = get_current_user()
    
    try:
        if tareas_collection and alumno:
            result = tareas_collection.delete_one({
                '_id': ObjectId(tarea_id),
                'user_id': alumno['id']
            })
            
            if result.deleted_count > 0:
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Tarea no encontrada'}), 404
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error eliminando tarea: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/eliminar_evento/<evento_id>", methods=["DELETE"])
@login_required
def eliminar_evento(evento_id):
    alumno = get_current_user()
    
    try:
        if eventos_collection and alumno:
            result = eventos_collection.delete_one({
                '_id': ObjectId(evento_id),
                'user_id': alumno['id']
            })
            
            if result.deleted_count > 0:
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Evento no encontrado'}), 404
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error eliminando evento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/eventos", methods=["GET", "POST"])
@login_required
def api_eventos():
    alumno = get_current_user()
    
    if request.method == "GET":
        try:
            eventos = []
            if eventos_collection and alumno:
                eventos_db = eventos_collection.find({'user_id': alumno['id']})
                for evento in eventos_db:
                    evento['_id'] = str(evento['_id'])
                    eventos.append(evento)
            
            return jsonify({'success': True, 'eventos': eventos})
            
        except Exception as e:
            print(f"Error obteniendo eventos: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == "POST":
        try:
            data = request.get_json()
            
            if not data.get('titulo') or not data.get('fecha'):
                return jsonify({'success': False, 'error': 'Título y fecha son requeridos'}), 400
            
            nuevo_evento = {
                'titulo': data.get('titulo'),
                'fecha': data.get('fecha'),
                'hora': data.get('hora', ''),
                'descripcion': data.get('descripcion', ''),
                'tipo': data.get('tipo', 'personal'),
                'prioridad': data.get('prioridad', 'media'),
                'fecha_creacion': datetime.now()
            }
            
            if eventos_collection and alumno:
                nuevo_evento['user_id'] = alumno['id']
                result = eventos_collection.insert_one(nuevo_evento)
                nuevo_evento['_id'] = str(result.inserted_id)
            
            return jsonify({'success': True, 'evento': nuevo_evento})
            
        except Exception as e:
            print(f"Error creando evento: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/compañero/<compañero_id>")
@login_required
def api_compañero(compañero_id):
    alumno = get_current_user()
    
    try:
        if users_collection:
            compañero = users_collection.find_one({
                '_id': ObjectId(compañero_id),
                'activo': True
            })
            
            if compañero:
                respuesta = {
                    '_id': str(compañero['_id']),
                    'nombre': compañero.get('nombre', ''),
                    'especialidad': compañero.get('especialidad', ''),
                    'semestre': compañero.get('semestre', 1),
                    'grupo': compañero.get('grupo', ''),
                    'turno': compañero.get('turno', ''),
                    'fecha_registro': compañero.get('fecha_registro', ''),
                    'avatar': compañero.get('avatar', 'default.png')
                }
                
                # Mostrar email si el usuario lo permite
                ajustes_compañero = ajustes_collection.find_one({'user_id': str(compañero['_id'])})
                if ajustes_compañero and ajustes_compañero.get('mostrar_email', False):
                    respuesta['email'] = compañero.get('email', '')
                
                return jsonify(respuesta)
        
        return jsonify({'error': 'Compañero no encontrado'}), 404
        
    except Exception as e:
        print(f"Error obteniendo compañero: {e}")
        return jsonify({'error': 'Error del servidor'}), 500

@app.route("/api/ajustes/exportar")
@login_required
def api_exportar_datos():
    alumno = get_current_user()
    
    try:
        datos = {
            'usuario': alumno,
            'exportado_en': datetime.now().isoformat(),
            'eventos': [],
            'tareas': [],
            'ajustes': {}
        }
        
        if eventos_collection and alumno:
            eventos = eventos_collection.find({'user_id': alumno['id']})
            for evento in eventos:
                evento['_id'] = str(evento['_id'])
                datos['eventos'].append(evento)
        
        if tareas_collection and alumno:
            tareas = tareas_collection.find({'user_id': alumno['id']})
            for tarea in tareas:
                tarea['_id'] = str(tarea['_id'])
                datos['tareas'].append(tarea)
        
        if ajustes_collection and alumno:
            ajustes = ajustes_collection.find_one({'user_id': alumno['id']})
            if ajustes:
                ajustes['_id'] = str(ajustes['_id'])
                datos['ajustes'] = ajustes
        
        return jsonify({'success': True, 'datos': datos})
        
    except Exception as e:
        print(f"Error exportando datos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.context_processor
def inject_user_data():
    alumno = get_current_user()
    
    ajustes_usuario = {}
    if ajustes_collection and alumno:
        ajustes_db = ajustes_collection.find_one({'user_id': alumno['id']})
        if ajustes_db:
            ajustes_usuario = ajustes_db
    
    return dict(
        alumno=alumno,
        ajustes=ajustes_usuario,
        current_year=datetime.now().year
    )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    
    print(f"🚀 Iniciando Media Superior Platform en puerto {port}")
    print(f"📊 Modo: {'Desarrollo' if debug else 'Producción'}")
    print(f"🔗 MongoDB: {'Conectado' if users_collection else 'Modo desarrollo'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)