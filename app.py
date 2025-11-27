from flask import Flask, render_template, request, redirect, url_for, flash, session
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

ANUNCIOS_RECIENTES = [
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
    },
    {
        "titulo": "Cambio Horarios",
        "emisor": "Dirección",
        "fecha": "04/OCT/2025",
        "prioridad": "baja"
    }
]

HORARIOS_TUTORIA = {
    "5A": "1:00 PM",
    "5B": "1:00 PM",
    "Miercoles": "1:00 PM",
    "Viernes": "1:00 PM"
}

MATERIAS = [
    {"nombre": "Programación", "horario": "J14", "profesor": "Lic. García"},
    {"nombre": "Matemáticas", "horario": "L25", "profesor": "Mtro. López"},
    {"nombre": "Historia", "horario": "M04", "profesor": "Prof. Martínez"},
    {"nombre": "Inglés", "horario": "V03", "profesor": "Mrs. Smith"}
]

@app.route("/")
def index():
    """Página principal con resumen del estudiante"""
    return render_template("index.html", 
                         alumno=ALUMNO_DATA,
                         anuncios=ANUNCIOS_RECIENTES[:2],  # Solo 2 más recientes
                         horarios_tutoria=HORARIOS_TUTORIA)

@app.route("/perfil")
def perfil():
    """Página de perfil del estudiante"""
    return render_template("perfil.html", alumno=ALUMNO_DATA)

@app.route("/agenda")
def agenda():
    """Página de agenda y calendario"""
    eventos = [
        {"fecha": "1 de octubre", "hora": "10:00 AM - 11:30 AM", "descripcion": "Clase de Programación"},
        {"fecha": "1 de octubre", "hora": "12:00 PM", "descripcion": "Tutoría"},
        {"fecha": "3 de octubre", "hora": "2:00 PM", "descripcion": "Club de Matemáticas"}
    ]
    return render_template("agenda.html", eventos=eventos, alumno=ALUMNO_DATA)

@app.route("/materias")
def materias():
    """Página de materias y horarios"""
    return render_template("materias.html", materias=MATERIAS, alumno=ALUMNO_DATA)

@app.route("/anuncios")
def anuncios():
    """Página de anuncios generales"""
    return render_template("anuncios.html", anuncios=ANUNCIOS_RECIENTES, alumno=ALUMNO_DATA)

@app.route("/tutoria")
def tutoria():
    """Página de tutoría y horarios"""
    historial_tutoria = [
        {"fecha": "Viernes", "tema": "Proyecto"},
        {"fecha": "Miércoles", "tema": "Tutoría"},
        {"fecha": "Viernes", "tema": "Proyecto"}
    ]
    return render_template("tutoria.html", 
                         horarios=HORARIOS_TUTORIA,
                         historial=historial_tutoria,
                         alumno=ALUMNO_DATA)

@app.route("/editar_perfil", methods=["GET", "POST"])
def editar_perfil():
    """Editar información del perfil"""
    if request.method == "POST":
        flash("Perfil actualizado correctamente", "success")
        return redirect(url_for("perfil"))
    
    return render_template("editar_perfil.html", alumno=ALUMNO_DATA)

if __name__ == "_main_":
    app.run(debug=True)

