from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "clave-secreta"
MONGO_URI = "mongodb+srv://paolaco1308_db_user:admin321@mediasuperior.ephlbzn.mongodb.net/mediasuperior"

db = None
client = None

def conectar_mongodb():
    """Conectar a TU MongoDB Atlas"""
    global db, client
    try:
        print(f"🔗 Intentando conectar a: {MONGO_URI.split('@')[1]}")
        
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,  
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            retryWrites=True,
            w="majority"
        )
        
        # Probar la conexión
        client.admin.command('ping')
        print("✅ Ping exitoso a MongoDB Atlas")
        
        # Obtener la base de datos (ya está especificada en la URI)
        db = client.get_database()
        
        print(f"📊 Conectado a base de datos: {db.name}")
        
        # Listar colecciones disponibles
        colecciones = db.list_collection_names()
        print(f"📚 Colecciones encontradas: {colecciones}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        db = None
        client = None
        return False

# ==================== RUTAS PRINCIPALES ====================

@app.route("/")
def index():
    """Página principal CON DATOS REALES"""
    # Conectar si no está conectado
    if db is None:
        conectar_mongodb()
    
    alumno = None
    anuncios = []
    
    if db:
        try:
            # 1. BUSCAR ALUMNO EN MONGODB
            alumno = db.alumnos.find_one({"numero_control": "2025001"})
            
            if alumno:
                print(f"✅ Alumno encontrado: {alumno['nombre_completo']}")
                # Convertir ObjectId a string
                alumno['_id_str'] = str(alumno['_id'])
            else:
                print("⚠️  No se encontró alumno 2025001, usando datos de ejemplo")
                alumno = {
                    "nombre_completo": "Mark Corona",
                    "numero_control": "2025001",
                    "especialidad": "Programación",
                    "semestre": "5",
                    "grupo": "B",
                    "turno": "Matutino",
                    "curp": "CORM950515HDFRNL09"
                }
            
            # 2. BUSCAR ANUNCIOS EN MONGODB
            anuncios_cursor = db.anuncios.find().sort("fecha", -1).limit(3)
            anuncios = list(anuncios_cursor)
            
            if anuncios:
                print(f"✅ {len(anuncios)} anuncios encontrados")
                for a in anuncios:
                    a['_id_str'] = str(a['_id'])
            else:
                print("⚠️  No hay anuncios, usando datos de ejemplo")
                anuncios = [
                    {"titulo": "Sin anuncios en BD", "emisor": "Sistema", "fecha": datetime.now(), "prioridad": "baja"},
                    {"titulo": "Inserta datos primero", "emisor": "Admin", "fecha": datetime.now(), "prioridad": "media"}
                ]
                
        except Exception as e:
            print(f"❌ Error en consulta: {e}")
            flash(f"Error de base de datos: {str(e)}", "error")
            # Datos de emergencia
            alumno = {
                "nombre_completo": "Mark Corona (Modo Emergencia)",
                "numero_control": "2025001",
                "especialidad": "Programación"
            }
            anuncios = []
    else:
        flash("⚠️  No hay conexión a MongoDB", "warning")
        alumno = {
            "nombre_completo": "Mark Corona (Sin conexión)",
            "numero_control": "2025001"
        }
        anuncios = []
    
    return render_template("index.html", 
                         alumno=alumno,
                         anuncios=anuncios[:2],
                         horarios_tutoria={"5B": "1:00 PM"})

@app.route("/crear-datos-iniciales")
def crear_datos_iniciales():
    """Crear datos de ejemplo en TU MongoDB"""
    if not db:
        conectar_mongodb()
    
    if not db:
        return "❌ No se pudo conectar a MongoDB"
    
    try:
        # 1. Insertar alumno de ejemplo
        alumno_data = {
            "numero_control": "2025001",
            "nombre_completo": "Mark Corona",
            "curp": "CORM950515HDFRNL09",
            "especialidad": "Programación",
            "semestre": "5",
            "grupo": "B",
            "turno": "Matutino",
            "email": "mark@ejemplo.com",
            "telefono": "5512345678",
            "fecha_registro": datetime.now()
        }
        
        # Eliminar si ya existe
        db.alumnos.delete_one({"numero_control": "2025001"})
        resultado_alumno = db.alumnos.insert_one(alumno_data)
        
        # 2. Insertar anuncios de ejemplo
        anuncios_data = [
            {
                "titulo": "Convocatoria Becas 2025",
                "contenido": "Se abren convocatorias para becas de excelencia...",
                "emisor": "Control Escolar",
                "fecha": datetime(2025, 10, 7),
                "prioridad": "alta",
                "destinatarios": ["5B", "5A"]
            },
            {
                "titulo": "Suspensión de Clases",
                "contenido": "Por motivo de... se suspenden clases el viernes",
                "emisor": "Dirección",
                "fecha": datetime(2025, 10, 6),
                "prioridad": "media",
                "destinatarios": ["Todos"]
            },
            {
                "titulo": "Reunión de Padres",
                "contenido": "Se cita a reunión de padres de familia...",
                "emisor": "Tutoría",
                "fecha": datetime(2025, 10, 5),
                "prioridad": "baja",
                "destinatarios": ["5B"]
            }
        ]
        
        db.anuncios.delete_many({})
        resultado_anuncios = db.anuncios.insert_many(anuncios_data)
        
        # 3. Insertar materias
        materias_data = [
            {"nombre": "Programación", "horario": "J14", "profesor": "Lic. García", "semestre": "5"},
            {"nombre": "Matemáticas", "horario": "L25", "profesor": "Mtro. López", "semestre": "5"},
            {"nombre": "Base de Datos", "horario": "M34", "profesor": "Ing. Pérez", "semestre": "5"}
        ]
        
        db.materias.delete_many({"semestre": "5"})
        resultado_materias = db.materias.insert_many(materias_data)
        
        return f'''
        <h1>✅ DATOS INSERTADOS EN TU MONGODB ATLAS</h1>
        <p>Alumno creado con ID: {resultado_alumno.inserted_id}</p>
        <p>Anuncios creados: {len(resultado_anuncios.inserted_ids)}</p>
        <p>Materias creadas: {len(resultado_materias.inserted_ids)}</p>
        <hr>
        <p><strong>Colecciones en {db.name}:</strong></p>
        <ul>
            <li>alumnos: {db.alumnos.count_documents({})} registros</li>
            <li>anuncios: {db.anuncios.count_documents({})} registros</li>
            <li>materias: {db.materias.count_documents({})} registros</li>
        </ul>
        <br>
        <a href="/" class="btn btn-primary">Ir al Inicio</a> |
        <a href="/test-conexion" class="btn btn-secondary">Probar Conexión</a>
        '''
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.route("/test-conexion")
def test_conexion():
    """Probar la conexión a TU MongoDB"""
    if db is None:
        conectar_mongodb()
    
    if db:
        try:
            # Estadísticas
            colecciones = db.list_collection_names()
            stats = {
                "alumnos": db.alumnos.count_documents({}),
                "anuncios": db.anuncios.count_documents({}),
                "materias": db.materias.count_documents({})
            }
            
            # Probar un alumno
            alumno_ejemplo = db.alumnos.find_one()
            
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Conexión MongoDB</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .success {{ color: green; font-weight: bold; }}
                    .info {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
                    .btn {{ display: inline-block; padding: 10px 15px; margin: 5px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <h1 class="success">✅ CONECTADO A TU MONGODB ATLAS</h1>
                
                <div class="info">
                    <p><strong>Base de datos:</strong> {db.name}</p>
                    <p><strong>Cluster:</strong> mediasuperior.ephlbzn.mongodb.net</p>
                    <p><strong>Usuario:</strong> paolaco1308_db_user</p>
                    <p><strong>Colecciones:</strong> {', '.join(colecciones) if colecciones else 'Ninguna'}</p>
                </div>
                
                <h3>📊 Estadísticas:</h3>
                <ul>
                    <li>Alumnos: {stats['alumnos']}</li>
                    <li>Anuncios: {stats['anuncios']}</li>
                    <li>Materias: {stats['materias']}</li>
                </ul>
                
                {f'<h3>👤 Alumno de ejemplo:</h3><pre>{alumno_ejemplo}</pre>' if alumno_ejemplo else '<p>⚠️ No hay alumnos registrados</p>'}
                
                <br>
                <a href="/crear-datos-iniciales" class="btn">Crear Datos de Ejemplo</a>
                <a href="/" class="btn">Ir al Inicio</a>
                <a href="/perfil" class="btn">Ver Perfil</a>
            </body>
            </html>
            '''
        except Exception as e:
            return f"❌ Error en la conexión: {str(e)}"
    else:
        return '''
        <h1>❌ NO HAY CONEXIÓN</h1>
        <p>No se pudo conectar a MongoDB Atlas.</p>
        <p>Posibles causas:</p>
        <ul>
            <li>Tu IP no está en la lista de permitidas en Atlas</li>
            <li>Problemas de red/firewall</li>
            <li>Credenciales incorrectas</li>
        </ul>
        <p>URI usada: mongodb+srv://paolaco1308_db_user:*******@mediasuperior.ephlbzn.mongodb.net/mediasuperior</p>
        '''

# ==================== RUTAS EXISTENTES MODIFICADAS ====================

@app.route("/perfil")
def perfil():
    """Perfil con datos reales de MongoDB"""
    if db is None:
        conectar_mongodb()
    
    alumno = None
    if db:
        alumno = db.alumnos.find_one({"numero_control": "2025001"})
        if alumno and '_id' in alumno:
            alumno['_id_str'] = str(alumno['_id'])
    
    if not alumno:
        flash("⚠️  No se encontraron datos en MongoDB. Usando datos de ejemplo.", "warning")
        alumno = {
            "nombre_completo": "Mark Corona",
            "curp": "CORM950515HDFRNL09",
            "numero_control": "2025001",
            "especialidad": "Programación",
            "semestre": "5",
            "grupo": "B",
            "turno": "Matutino"
        }
    
    return render_template("perfil.html", alumno=alumno)

@app.route("/editar_perfil", methods=["GET", "POST"])
def editar_perfil():
    """Editar perfil en MongoDB REAL"""
    if db is None:
        conectar_mongodb()
    
    if not db:
        flash("Error de conexión a la base de datos", "error")
        return redirect(url_for("perfil"))
    
    # Obtener alumno actual
    alumno = db.alumnos.find_one({"numero_control": "2025001"})
    
    if not alumno:
        flash("Alumno no encontrado en la base de datos", "error")
        return redirect(url_for("perfil"))
    
    if request.method == "POST":
        try:
            update_data = {
                "nombre_completo": request.form.get("nombre_completo"),
                "curp": request.form.get("curp"),
                "numero_control": request.form.get("numero_control"),
                "especialidad": request.form.get("especialidad"),
                "semestre": request.form.get("semestre"),
                "grupo": request.form.get("grupo"),
                "turno": request.form.get("turno"),
                "email": request.form.get("email", ""),
                "telefono": request.form.get("telefono", ""),
                "ultima_actualizacion": datetime.now()
            }
            
            resultado = db.alumnos.update_one(
                {"_id": alumno['_id']},
                {"$set": update_data}
            )
            
            if resultado.modified_count > 0:
                flash("✅ Perfil actualizado en MongoDB Atlas", "success")
            else:
                flash("ℹ️ No se realizaron cambios", "info")
            
            return redirect(url_for("perfil"))
            
        except Exception as e:
            flash(f"❌ Error al actualizar: {str(e)}", "error")
    
    # Preparar datos para el template
    if '_id' in alumno:
        alumno['_id_str'] = str(alumno['_id'])
    
    return render_template("editar_perfil.html", alumno=alumno)

@app.route("/anuncios")
def anuncios():
    """Anuncios desde MongoDB"""
    if db is None:
        conectar_mongodb()
    
    anuncios_lista = []
    if db:
        try:
            anuncios_cursor = db.anuncios.find().sort("fecha", -1)
            anuncios_lista = list(anuncios_cursor)
            for a in anuncios_lista:
                a['_id_str'] = str(a['_id'])
        except:
            pass
    
    if not anuncios_lista:
        anuncios_lista = [
            {"titulo": "No hay anuncios en la BD", "emisor": "Sistema", "fecha": datetime.now(), "prioridad": "baja"},
            {"titulo": "Usa /crear-datos-iniciales", "emisor": "Admin", "fecha": datetime.now(), "prioridad": "alta"}
        ]
    
    alumno = db.alumnos.find_one({"numero_control": "2025001"}) if db else None
    
    return render_template("anuncios.html", 
                         anuncios=anuncios_lista, 
                         alumno=alumno or {"nombre_completo": "Mark Corona"})


print("🚀 Iniciando conexión a MongoDB Atlas...")
if conectar_mongodb():
    print("✅ Aplicación lista con MongoDB Atlas")
else:
    print("⚠️  Aplicación en modo sin conexión a MongoDB")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)