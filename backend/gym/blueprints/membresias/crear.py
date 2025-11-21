from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Membresia import Membresia
from gym.extensions import db

membresias_bp = Blueprint("crear_membresia", __name__)

@membresias_bp.post("/")
@jwt_required()
def crear_membresia():
    data = request.get_json()

    # Obtener los datos de la membresía
    nombre = data.get("nombre")
    duracion_dias = data.get("duracion_dias")
    precio = data.get("precio")

    # Crear la nueva membresía
    nueva_membresia = Membresia(
        nombre=nombre,
        duracion_dias=duracion_dias,
        precio=precio
    )

    db.session.add(nueva_membresia)
    db.session.commit()

    return jsonify(nueva_membresia.to_dict()), 201  # Devolver la membresía creada
