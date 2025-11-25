from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime

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
    anuncios = [
        {
            "titulo": "Convocatoria Becas 2025",
            "emisor": "Control Escolar",
            "fecha": "07/OCT/2025",
            "prioridad": "alta",
            "contenido": "Se informa a todos los estudiantes interesados que está abierta la convocatoria para becas 2025. Los requisitos y formato de solicitud están disponibles en control escolar."
        },
        {
            "titulo": "Suspensión de Clases",
            "emisor": "Control Escolar",
            "fecha": "06/OCT/2025",
            "prioridad": "media",
            "contenido": "Por actividades administrativas, se suspenden labores académicas el próximo viernes. Las clases se reanudarán el lunes en horario normal."
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
    """Editar información del perfil"""
    if request.method == "POST":
        flash("✅ Perfil actualizado correctamente", "success")
        return redirect(url_for("perfil"))
    
    return render_template("editar_perfil.html", alumno=ALUMNO_DATA)

@app.route("/agenda")
def agenda():
    """Página de agenda"""
    return render_template("agenda.html", alumno=ALUMNO_DATA)

@app.route("/materias")
def materias():
    """Página de materias"""
    return render_template("materias.html", alumno=ALUMNO_DATA)

@app.route("/anuncios")
def anuncios():
    """Página de anuncios"""
    anuncios_data = [
        {
            "titulo": "Convocatoria Becas 2025",
            "emisor": "Control Escolar",
            "fecha": "07/OCT/2025",
            "prioridad": "alta",
            "tipo": "academico",
            "contenido": "Se informa a todos los estudiantes interesados que está abierta la convocatoria para becas 2025. Los requisitos y formato de solicitud están disponibles en control escolar."
        },
        {
            "titulo": "Suspensión de Clases", 
            "emisor": "Control Escolar",
            "fecha": "06/OCT/2025",
            "prioridad": "media",
            "tipo": "administrativo",
            "contenido": "Por actividades administrativas, se suspenden labores académicas el próximo viernes. Las clases se reanudarán el lunes en horario normal."
        }
    ]
    
    return render_template("anuncios.html", 
                         anuncios=anuncios_data,
                         pagina_actual=1,
                         total_paginas=1,
                         filtro_actual='todos',
                         alumno=ALUMNO_DATA)

@app.route("/tutoria")
def tutoria():
    """Página de tutoría"""
    return render_template("tutoria.html", 
                         horarios=HORARIOS_TUTORIA,
                         alumno=ALUMNO_DATA)

if __name__ == "_main_":
    app.run(host="0.0.0.0", port=5000, debug=False)