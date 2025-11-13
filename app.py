from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")
MONGO_URI = "mongodb+srv://paolaco1308_db_user:admin321@mediasuperior.ephlbzn.mongodb.net/mediasuperior"

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

estudiante = {
    "nombre": "Paola Camila Corona Guzmán",
    "semestre": "Quinto Semestre",
    "especialidad": "Programación",
    "turno": "Matutino",
    "grupo": "5B",
    "numero_control": "12345678"
}

materias = [
    {"nombre": "Matemáticas V", "grupo": "07", "profesor": "Luis García"},
    {"nombre": "Historia", "grupo": "M04", "profesor": "Ana Martínez"},
    {"nombre": "Programación", "grupo": "J14", "profesor": "Carlos Rodríguez"},
    {"nombre": "Inglés", "grupo": "A10", "profesor": "María López"}
]

tareas = [
    {"materia": "Matemáticas V", "descripcion": "Ejercicios de álgebra", "fecha": "2025-10-10"},
    {"materia": "Historia", "descripcion": "Investigación sobre la Revolución", "fecha": "2025-10-12"},
    {"materia": "Programación", "descripcion": "Proyecto final", "fecha": "2025-10-15"},
    {"materia": "Inglés", "descripcion": "Presentación oral", "fecha": "2025-10-08"}
]

anuncios = [
    {"titulo": "Entrega de Calificaciones", "fecha": "06/oct/2025", "tipo": "General"},
    {"titulo": "Convocatoria Becas 2025", "fecha": "07/oct/2025", "tipo": "General"},
    {"titulo": "Suspensión de Clases", "fecha": "06/oct/2025", "tipo": "General"},
    {"titulo": "Cambio Horarios", "fecha": "04/oct/2025", "tipo": "General"}
]

actividades = [
    {"nombre": "Voleibol", "horario": "Lunes y Miércoles 4:00 PM"},
    {"nombre": "Fútbol", "horario": "Martes y Jueves 4:00 PM"},
    {"nombre": "Basketball", "horario": "Viernes 3:00 PM"},
    {"nombre": "Pintura", "horario": "Sábados 10:00 AM"}
]

@app.route("/")
def index():
    return render_template("index.html", 
                          estudiante=estudiante, 
                          materias=materias, 
                          tareas=tareas, 
                          anuncios=anuncios,
                          actividades=actividades)

@app.route("/perfil")
def perfil():
    return render_template("perfil.html", estudiante=estudiante)

@app.route("/agenda")
def agenda():
    return render_template("agenda.html", estudiante=estudiante, tareas=tareas)

@app.route("/materias")
def materias_route():
    return render_template("materias.html", estudiante=estudiante, materias=materias)

@app.route("/anuncios")
def anuncios_route():
    return render_template("anuncios.html", estudiante=estudiante, anuncios=anuncios)

@app.route("/tutoria")
def tutoria():
    return render_template("tutoria.html", estudiante=estudiante)

@app.route("/actividades")
def actividades_route():
    return render_template("actividades.html", estudiante=estudiante, actividades=actividades)

@app.route("/calificaciones")
def calificaciones():
    return render_template("calificaciones.html", estudiante=estudiante, materias=materias)

if __name__ == "_main_":
    app.run(debug=True)