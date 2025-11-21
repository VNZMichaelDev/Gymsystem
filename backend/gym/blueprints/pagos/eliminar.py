from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Pago import Pago
from gym.extensions import db

eliminar_bp = Blueprint("eliminar_pago", __name__)

@eliminar_bp.delete("/<int:id_pago>")
@jwt_required()
def eliminar_pago(id_pago):
    pago = Pago.query.get_or_404(id_pago)
    db.session.delete(pago)
    db.session.commit()

    return jsonify({"message": "Pago eliminado exitosamente"}), 200
