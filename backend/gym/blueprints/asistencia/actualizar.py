from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Asistencia import Asistencia
from gym.extensions import db

actualizar_bp = Blueprint("actualizar_asistencia", __name__)

@actualizar_bp.put("/<int:id_asistencia>")
@jwt_required()
def actualizar_asistencia(id_asistencia):
    asistencia = Asistencia.query.get_or_404(id_asistencia)

    data = request.get_json()

    asistencia.hora_salida = data.get("hora_salida", asistencia.hora_salida)

    db.session.commit()

    return jsonify(asistencia.to_dict())
