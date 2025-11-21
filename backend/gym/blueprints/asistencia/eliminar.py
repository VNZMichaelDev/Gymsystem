from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Asistencia import Asistencia
from gym.extensions import db

eliminar_bp = Blueprint("eliminar_asistencia", __name__)

@eliminar_bp.delete("/<int:id_asistencia>")
@jwt_required()
def eliminar_asistencia(id_asistencia):
    asistencia = Asistencia.query.get_or_404(id_asistencia)
    db.session.delete(asistencia)
    db.session.commit()

    return jsonify({"message": "Asistencia eliminada exitosamente"}), 200
