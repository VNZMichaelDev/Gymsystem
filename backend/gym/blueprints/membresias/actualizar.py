from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Membresia import Membresia
from gym.extensions import db

actualizar_bp = Blueprint("actualizar_membresia", __name__)

@actualizar_bp.put("/<int:id_membresia>")
@jwt_required()
def actualizar_membresia(id_membresia):
    membresia = Membresia.query.get_or_404(id_membresia)

    data = request.get_json()

    membresia.nombre = data.get("nombre", membresia.nombre)
    membresia.duracion_dias = data.get("duracion_dias", membresia.duracion_dias)
    membresia.precio = data.get("precio", membresia.precio)

    db.session.commit()

    return jsonify(membresia.to_dict())
