from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Membresia import Membresia
from gym.extensions import db

eliminar_bp = Blueprint("eliminar_membresia", __name__)

@eliminar_bp.delete("/<int:id_membresia>")
@jwt_required()
def eliminar_membresia(id_membresia):
    membresia = Membresia.query.get_or_404(id_membresia)
    db.session.delete(membresia)
    db.session.commit()

    return jsonify({"message": "Membresía eliminada exitosamente"}), 200
