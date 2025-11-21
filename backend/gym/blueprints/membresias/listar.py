from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Membresia import Membresia

listar_bp = Blueprint("listar_membresias", __name__)

@listar_bp.get("/")
@jwt_required()
def listar_membresias():
    membresias = Membresia.query.all()  # Obtener todas las membresías

    return jsonify([membresia.to_dict() for membresia in membresias])
