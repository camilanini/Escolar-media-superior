from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime, timedelta
from bson import ObjectId

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-")
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

ALUMNO_DATA = {
    "nombre_completo": "Mark Corona",
    "curp": "CORM950515HDFRNL09",
    "numero_control": "2025001",
    "especialidad": "Programación",
    "semestre": "5",
    "grupo": "B",
    "turno": "Matutino"
}

HORARIOS_TUTORIA = {
    "5A": "1:00 PM",
    "5B": "1:00 PM",
    "Miercoles": "1:00 PM",
    "Viernes": "1:00 PM"
}


@app.route("/")
def index():
    """Página principal"""
    anuncios = []
    if db is not None:
        try:
            anuncios = list(db.anuncios.find().sort("fecha", -1).limit(2))
        except Exception as e:
            print(f"Error al obtener anuncios: {e}")
    
    if not anuncios:
        anuncios = [
            {
                "titulo": "Convocatoria Becas 2025",
                "emisor": "Control Escolar",
                "fecha": "07/OCT/2025",
                "prioridad": "alta"
            },
            {
                "titulo": "Suspensión de Clases",
                "emisor": "Control Escolar",
                "fecha": "06/OCT/2025",
                "prioridad": "media"
            }
        ]
    
    return render_template("index.html", 
                         alumno=ALUMNO_DATA,
                         anuncios=anuncios,
                         horarios_tutoria=HORARIOS_TUTORIA)


@app.route("/perfil")
def perfil():
    """Página de perfil del estudiante"""
    return render_template("perfil.html", alumno=ALUMNO_DATA)

@app.route("/editar_perfil", methods=["GET", "POST"])
def editar_perfil():
    """Editar información del perfil - AHORA FUNCIONAL"""
    if request.method == "POST":
        try:
            nuevo_nombre = request.form.get("nombre_completo", "").strip()
            nuevo_curp = request.form.get("curp", "").strip()
            nuevo_numero_control = request.form.get("numero_control", "").strip()
            nueva_especialidad = request.form.get("especialidad", "").strip()
            nuevo_semestre = request.form.get("semestre", "").strip()
            nuevo_grupo = request.form.get("grupo", "").strip()
            nuevo_turno = request.form.get("turno", "").strip()
            
            campos = [nuevo_nombre, nuevo_curp, nuevo_numero_control, nueva_especialidad, nuevo_semestre, nuevo_grupo, nuevo_turno]
            if not all(campos):
                flash("❌ Por favor completa todos los campos", "danger")
                return redirect(url_for("editar_perfil"))
            
            if db is not None:
                try:
                    db.perfiles.update_one(
                        {"numero_control": ALUMNO_DATA["numero_control"]},
                        {"$set": {
                            "nombre_completo": nuevo_nombre,
                            "curp": nuevo_curp,
                            "numero_control": nuevo_numero_control,
                            "especialidad": nueva_especialidad,
                            "semestre": nuevo_semestre,
                            "grupo": nuevo_grupo,
                            "turno": nuevo_turno,
                            "actualizado_en": datetime.now()
                        }},
                        upsert=True
                    )
                    flash("✅ Perfil guardado en base de datos", "info")
                except Exception as e:
                    flash(f"⚠ No se pudo guardar en BD: {e}", "warning")
            
            ALUMNO_DATA["nombre_completo"] = nuevo_nombre
            ALUMNO_DATA["curp"] = nuevo_curp
            ALUMNO_DATA["numero_control"] = nuevo_numero_control
            ALUMNO_DATA["especialidad"] = nueva_especialidad
            ALUMNO_DATA["semestre"] = nuevo_semestre
            ALUMNO_DATA["grupo"] = nuevo_grupo
            ALUMNO_DATA["turno"] = nuevo_turno
            
            flash("✅ Perfil actualizado correctamente", "success")
            return redirect(url_for("perfil"))
            
        except Exception as e:
            flash(f"❌ Error al actualizar perfil: {str(e)}", "danger")
            return redirect(url_for("editar_perfil"))
    
    return render_template("editar_perfil.html", alumno=ALUMNO_DATA)


@app.route("/agenda")
def agenda():
    """Página de agenda interactiva"""
    eventos = []
    if db is not None:
        try:
            eventos = list(db.eventos.find().sort("fecha", 1))
        except Exception as e:
            print(f"Error al obtener eventos: {e}")
    
    # Si no hay eventos en BD, usar datos de ejemplo
    if not eventos:
        eventos = [
            {
                "_id": "1",
                "titulo": "Clase de Programación",
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "hora_inicio": "10:00",
                "hora_fin": "11:30",
                "descripcion": "Clase regular de programación",
                "tipo": "academico"
            },
            {
                "_id": "2",
                "titulo": "Tutoría",
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "hora_inicio": "12:00",
                "hora_fin": "13:00",
                "descripcion": "Sesión de tutoría grupal",
                "tipo": "tutoria"
            }
        ]
    
    # Obtener eventos de hoy
    hoy = datetime.now().strftime("%Y-%m-%d")
    eventos_hoy = [evento for evento in eventos if evento.get('fecha') == hoy]
    
    # Eventos próximos (próximos 7 días)
    fecha_limite = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    eventos_proximos = [e for e in eventos if e.get('fecha') > hoy and e.get('fecha') <= fecha_limite]
    
    return render_template("agenda.html", 
                         eventos=eventos,
                         eventos_hoy=eventos_hoy,
                         eventos_proximos=eventos_proximos,
                         alumno=ALUMNO_DATA)

@app.route("/agenda/agregar", methods=["POST"])
def agregar_evento():
    """Agregar nuevo evento a la agenda"""
    if db is None:
        flash("Error: Base de datos no disponible", "danger")
        return redirect(url_for('agenda'))
    
    try:
        nuevo_evento = {
            "titulo": request.form.get("titulo"),
            "descripcion": request.form.get("descripcion"),
            "fecha": request.form.get("fecha"),
            "hora_inicio": request.form.get("hora_inicio"),
            "hora_fin": request.form.get("hora_fin"),
            "tipo": request.form.get("tipo", "personal"),
            "creado_en": datetime.now()
        }
        
        if db is not None:
            db.eventos.insert_one(nuevo_evento)
        
        flash("✅ Evento agregado correctamente", "success")
    except Exception as e:
        flash(f"❌ Error al agregar evento: {e}", "danger")
    
    return redirect(url_for('agenda'))

@app.route("/agenda/eliminar/<evento_id>", methods=["POST"])
def eliminar_evento(evento_id):
    """Eliminar evento de la agenda"""
    if db is None:
        flash("Error: Base de datos no disponible", "danger")
        return redirect(url_for('agenda'))
    
    try:
        if db is not None:
            db.eventos.delete_one({"_id": ObjectId(evento_id)})
        flash("✅ Evento eliminado correctamente", "success")
    except Exception as e:
        flash(f"❌ Error al eliminar evento: {e}", "danger")
    
    return redirect(url_for('agenda'))

@app.route("/materias")
def materias():
    """Página de materias con calificaciones y tareas"""
    # Datos de ejemplo seguros
    materias_data = [
        {"nombre": "Programación", "horario": "J14", "profesor": "Lic. García", "creditos": 5},
        {"nombre": "Matemáticas", "horario": "L25", "profesor": "Mtro. López", "creditos": 5},
        {"nombre": "Historia", "horario": "M04", "profesor": "Prof. Martínez", "creditos": 4},
        {"nombre": "Inglés", "horario": "V03", "profesor": "Mrs. Smith", "creditos": 4}
    ]
    
    tareas_pendientes = [
        {"_id": "1", "materia": "Programación", "titulo": "Sistema Gestión", "fecha_entrega": "2025-10-25", "descripcion": "Desarrollar sistema web"},
        {"_id": "2", "materia": "Matemáticas", "titulo": "Examen Unidad 3", "fecha_entrega": "2025-10-20", "descripcion": "Álgebra y ecuaciones"}
    ]
    
    Calificaciones = [
        {"materia": "Programación", "parcial1": 8.5, "parcial2": 9.0, "parcial3": 8.8, "promedio": 8.8},
        {"materia": "Matemáticas", "parcial1": 9.2, "parcial2": 8.7, "parcial3": 9.5, "promedio": 9.1}
    ]
    
    return render_template("materias.html", 
                         materias=materias_data,
                         tareas=tareas_pendientes,
                         Calificaciones=Calificaciones,
                         alumno=ALUMNO_DATA)

@app.route("/anuncios")
def anuncios():
    """Página de anuncios con paginación real"""
    pagina = request.args.get('pagina', 1, type=int)
    anuncios_por_pagina = 5
    filtro = request.args.get('filtro', 'todos')
    
    anuncios_data = []
    total_anuncios = 0
    
    if db is not None:
        try:
            # Aplicar filtros
            query = {}
            if filtro != 'todos':
                query = {"tipo": filtro}
            
            # Obtener anuncios paginados
            skip = (pagina - 1) * anuncios_por_pagina
            anuncios_data = list(db.anuncios.find(query)
                                .sort("fecha", -1)
                                .skip(skip)
                                .limit(anuncios_por_pagina))
            
            total_anuncios = db.anuncios.count_documents(query)
        except Exception as e:
            print(f"Error al obtener anuncios: {e}")
    
    # Si no hay datos en BD, usar datos de ejemplo
    if not anuncios_data:
        anuncios_data = [
            {
                "_id": "1",
                "titulo": "Convocatoria Becas 2025",
                "emisor": "Control Escolar",
                "fecha": "07/OCT/2025",
                "prioridad": "alta",
                "tipo": "academico",
                "contenido": "Se informa a todos los estudiantes interesados que está abierta la convocatoria para becas 2025. Los requisitos y formato de solicitud están disponibles en control escolar."
            },
            {
                "_id": "2",
                "titulo": "Suspensión de Clases", 
                "emisor": "Control Escolar",
                "fecha": "06/OCT/2025",
                "prioridad": "media",
                "tipo": "administrativo",
                "contenido": "Por actividades administrativas, se suspenden labores académicas el próximo viernes. Las clases se reanudarán el lunes en horario normal."
            },
            {
                "_id": "3",
                "titulo": "Cambio Horarios",
                "emisor": "Dirección",
                "fecha": "04/OCT/2025",
                "prioridad": "baja",
                "tipo": "academico",
                "contenido": "A partir de la próxima semana habrá ajustes en los horarios de algunas materias. Favor de verificar su horario actualizado."
            },
            {
                "_id": "4",
                "titulo": "Inscripción Clubes Deportivos",
                "emisor": "Departamento de Educación Física",
                "fecha": "03/OCT/2025",
                "prioridad": "media",
                "tipo": "deportivo",
                "contenido": "Las inscripciones para los clubes deportivos estarán abiertas hasta el viernes. Vóley, Fútbol, Básquetbol disponibles."
            },
            {
                "_id": "5",
                "titulo": "Concurso de Programación",
                "emisor": "Departamento de Informática",
                "fecha": "02/OCT/2025",
                "prioridad": "alta",
                "tipo": "academico",
                "contenido": "Se invita a todos los estudiantes de programación a participar en el concurso anual. Premios para los primeros lugares."
            }
        ]
        total_anuncios = len(anuncios_data)
    
    total_paginas = (total_anuncios + anuncios_por_pagina - 1) // anuncios_por_pagina
    
    return render_template("anuncios.html", 
                         anuncios=anuncios_data,
                         pagina_actual=pagina,
                         total_paginas=total_paginas,
                         filtro_actual=filtro,
                         alumno=ALUMNO_DATA)


@app.route("/tutoria")
def tutoria():
    """Página de tutoría con funcionalidades completas"""
    # Obtener sesiones de tutoría
    sesiones_tutoria = []
    confirmaciones = []
    
    if db is not None:
        try:
            sesiones_tutoria = list(db.sesiones_tutoria.find().sort("fecha", 1))
            # Verificar si el alumno ya confirmó asistencia a las próximas sesiones
            confirmaciones = list(db.confirmaciones_tutoria.find({
                "alumno_id": ALUMNO_DATA["numero_control"]
            }))
        except Exception as e:
            print(f"Error al obtener datos de tutoría: {e}")
    
    # Datos de ejemplo
    if not sesiones_tutoria:
        sesiones_tutoria = [
            {
                "_id": "1",
                "fecha": "2025-10-20",
                "fecha_display": "Viernes 20 de Octubre",
                "tema": "Avance de proyectos semestrales",
                "hora": "1:00 PM",
                "lugar": "Sala de Tutores",
                "estado": "pendiente"
            },
            {
                "_id": "2",
                "fecha": "2025-10-27",
                "fecha_display": "Viernes 27 de Octubre", 
                "tema": "Preparación para exámenes parciales",
                "hora": "1:00 PM",
                "lugar": "Sala de Tutores",
                "estado": "pendiente"
            }
        ]
    
    historial_tutoria = [
        {"fecha": "Viernes 6 de Octubre", "tema": "Proyecto", "estado": "completada"},
        {"fecha": "Miércoles 4 de Octubre", "tema": "Tutoría", "estado": "completada"},
        {"fecha": "Viernes 29 de Septiembre", "tema": "Proyecto", "estado": "completada"}
    ]
    
    return render_template("tutoria.html", 
                         horarios=HORARIOS_TUTORIA,
                         historial=historial_tutoria,
                         sesiones=sesiones_tutoria,
                         confirmaciones=confirmaciones,
                         alumno=ALUMNO_DATA)

@app.route("/tutoria/confirmar", methods=["POST"])
def confirmar_asistencia():
    """Confirmar asistencia a sesión de tutoría"""
    if db is None:
        flash("Error: Base de datos no disponible", "danger")
        return redirect(url_for('tutoria'))
    
    try:
        sesion_id = request.form.get("sesion_id")
        
        # Verificar si ya confirmó
        confirmacion_existente = db.confirmaciones_tutoria.find_one({
            "alumno_id": ALUMNO_DATA["numero_control"],
            "sesion_id": sesion_id
        })
        
        if confirmacion_existente:
            flash("⚠ Ya habías confirmado asistencia a esta sesión", "warning")
        else:
            confirmacion = {
                "alumno_id": ALUMNO_DATA["numero_control"],
                "alumno_nombre": ALUMNO_DATA["nombre_completo"],
                "sesion_id": sesion_id,
                "fecha_confirmacion": datetime.now(),
                "estado": "confirmado"
            }
            
            db.confirmaciones_tutoria.insert_one(confirmacion)
            flash("✅ Asistencia confirmada correctamente", "success")
            
    except Exception as e:
        flash(f"❌ Error al confirmar asistencia: {e}", "danger")
    
    return redirect(url_for('tutoria'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "_main_":
    app.run(debug=True)