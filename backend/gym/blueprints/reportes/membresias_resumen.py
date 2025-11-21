from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Membresia import Membresia
from gym.models.Cliente import Cliente
from gym.extensions import db
from sqlalchemy import func

membresias_resumen_bp = Blueprint('membresias_resumen', __name__)


@membresias_resumen_bp.get('/membresias_resumen')
@jwt_required()
def membresias_resumen():
    """
    Retorna un resumen de las membresías:
    - total: cantidad de membresías
    - mas_cara: { id, nombre, precio }
    - mas_barata: { id, nombre, precio }
    - con_mas_clientes: { id, nombre, precio, clientes }
    - con_menos_clientes: { id, nombre, precio, clientes }
    """
    try:
        total = Membresia.query.count() or 0

        mas_cara = Membresia.query.order_by(Membresia.precio.desc()).first()
        mas_barata = Membresia.query.order_by(Membresia.precio.asc()).first()

        # Obtener conteo de clientes por membresía (incluir 0)
        counts = (
            db.session.query(
                Membresia.id_membresia,
                Membresia.nombre,
                Membresia.precio,
                func.count(Cliente.id_cliente).label('clientes')
            )
            .outerjoin(Cliente, Cliente.id_membresia == Membresia.id_membresia)
            .group_by(Membresia.id_membresia)
            .order_by(func.count(Cliente.id_cliente).desc())
            .all()
        )

        # Transformar a lista para buscar max/min
        counts_list = [
            { 'id_membresia': c[0], 'nombre': c[1], 'precio': c[2], 'clientes': int(c[3]) }
            for c in counts
        ]

        con_mas_clientes = counts_list[0] if counts_list else None
        con_menos_clientes = counts_list[-1] if counts_list else None

        return jsonify({
            'total': int(total),
            'mas_cara': {
                'id_membresia': mas_cara.id_membresia,
                'nombre': mas_cara.nombre,
                'precio': mas_cara.precio
            } if mas_cara else None,
            'mas_barata': {
                'id_membresia': mas_barata.id_membresia,
                'nombre': mas_barata.nombre,
                'precio': mas_barata.precio
            } if mas_barata else None,
            'con_mas_clientes': con_mas_clientes,
            'con_menos_clientes': con_menos_clientes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
