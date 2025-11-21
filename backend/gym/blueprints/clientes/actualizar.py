from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Cliente import Cliente
from gym.extensions import db

actualizar_bp = Blueprint("actualizar_cliente", __name__)

@actualizar_bp.put("/<int:id_cliente>")
@jwt_required()
def actualizar_cliente(id_cliente):
    cliente = Cliente.query.get_or_404(id_cliente)

    data = request.get_json()

    cliente.nombre = data.get("nombre", cliente.nombre)
    cliente.apellido_paterno = data.get("apellido_paterno", cliente.apellido_paterno)
    cliente.apellido_materno = data.get("apellido_materno", cliente.apellido_materno)
    cliente.correo = data.get("correo", cliente.correo)
    cliente.telefono = data.get("telefono", cliente.telefono)
    cliente.fecha_registro = data.get("fecha_registro", cliente.fecha_registro)
    cliente.id_membresia = data.get("id_membresia", cliente.id_membresia)

    db.session.commit()

    return jsonify(cliente.to_dict())
