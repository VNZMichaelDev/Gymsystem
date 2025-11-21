from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Cliente import Cliente
from gym.models.Pago import Pago
from gym.extensions import db
from datetime import datetime

pagos_pendientes_bp = Blueprint("pagos_pendientes", __name__)

@pagos_pendientes_bp.get("/pagos_pendientes")
@jwt_required()
def pagos_pendientes():
    # Obtener pagos con estado "Pendiente"
    try:
        pagos_pendientes = db.session.query(
            Cliente.nombre,
            Cliente.apellido_paterno,
            Cliente.apellido_materno,
            Cliente.numero_documento,
            Pago.monto,
            Pago.fecha_pago,
            Pago.estado,
            Pago.id_pago
        ).join(Cliente, Pago.id_cliente == Cliente.id_cliente)\
         .filter(Pago.estado == "Pendiente")\
         .order_by(Pago.fecha_pago.desc()).all()

        return jsonify([{
            'id_pago': id_pago,
            'cliente': f"{nombre} {apellido_paterno} {apellido_materno}",
            'numero_documento': numero_documento,
            'monto': float(monto),
            'fecha_pago': fecha_pago,
            'estado': estado
        } for nombre, apellido_paterno, apellido_materno, numero_documento, monto, fecha_pago, estado, id_pago in pagos_pendientes])
    
    except Exception as e:
        return jsonify({"error": f"Error al obtener pagos pendientes: {str(e)}"}), 500
