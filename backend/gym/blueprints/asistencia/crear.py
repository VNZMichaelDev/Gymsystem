from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Asistencia import Asistencia
from gym.extensions import db

asistencias_bp = Blueprint("crear_asistencia", __name__)

@asistencias_bp.post("/")
@jwt_required()
def crear_asistencia():
    data = request.get_json()

    # Obtener los datos de la asistencia
    id_cliente = data.get("id_cliente")
    hora_salida = data.get("hora_salida")

    # Crear la nueva asistencia
    nueva_asistencia = Asistencia(
        id_cliente=id_cliente,
        hora_salida=hora_salida
    )

    db.session.add(nueva_asistencia)
    db.session.commit()

    return jsonify(nueva_asistencia.to_dict()), 201  # Devolver la asistencia creada
