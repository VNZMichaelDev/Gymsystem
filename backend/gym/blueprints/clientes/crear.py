from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Cliente import Cliente
from gym.extensions import db

clientes_bp = Blueprint("clientes", __name__)

@clientes_bp.get("/<int:id_cliente>")
@jwt_required()
def obtener_cliente(id_cliente):
    """Obtener un cliente específico por ID"""
    cliente = Cliente.query.get(id_cliente)
    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404
    
    return jsonify(cliente.to_dict(include_membresia=True))

@clientes_bp.post("/")
@jwt_required()
def crear_cliente():
    data = request.get_json()

    # Obtener los datos del cliente del JSON
    tipo_documento = data.get("tipo_documento")
    numero_documento = data.get("numero_documento")
    nombre = data.get("nombre")
    apellido_paterno = data.get("apellido_paterno")
    apellido_materno = data.get("apellido_materno")
    correo = data.get("correo")
    telefono = data.get("telefono")
    fecha_registro = data.get("fecha_registro")
    id_membresia = data.get("id_membresia")

    # Crear un nuevo cliente
    nuevo_cliente = Cliente(
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        nombre=nombre,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        correo=correo,
        telefono=telefono,
        fecha_registro=fecha_registro,
        id_membresia=id_membresia
    )

    db.session.add(nuevo_cliente)
    db.session.commit()

    return jsonify(nuevo_cliente.to_dict()), 201  # Devuelve el cliente recién creado
