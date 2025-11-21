from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Membresia import Membresia
from gym.extensions import db

membresias_por_precio_bp = Blueprint('membresias_por_precio', __name__)


@membresias_por_precio_bp.get('/membresias_por_precio')
@jwt_required()
def membresias_por_precio():
    """Devuelve la lista de membresías con su nombre y precio.

    Respuesta: [ { nombre, precio }, ... ]
    """
    try:
        rows = db.session.query(
            Membresia.nombre,
            Membresia.precio
        ).order_by(Membresia.precio.desc()).all()

        result = [{'nombre': nombre, 'precio': float(precio) if precio is not None else 0.0} for nombre, precio in rows]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Error al obtener membresías por precio: {str(e)}'}), 500
