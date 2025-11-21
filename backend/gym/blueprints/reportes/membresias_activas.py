from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Cliente import Cliente
from gym.models.Membresia import Membresia
from gym.extensions import db
from sqlalchemy import func
from datetime import datetime

membresias_activas_bp = Blueprint("membresias_activas", __name__)


@membresias_activas_bp.get("/membresias_activas")
@jwt_required()
def membresias_activas():
    """Obtener membresías con la cantidad de clientes. Acepta fecha_inicio/fecha_fin opcionales para filtrar por fecha de registro del cliente."""
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    # Default: last 4 months if no dates provided
    if not fecha_inicio and not fecha_fin:
        hoy = datetime.now()
        m = hoy.month - 3
        y = hoy.year
        while m <= 0:
            m += 12
            y -= 1
        inicio_mes = datetime(year=y, month=m, day=1)
        fecha_inicio = inicio_mes.strftime('%Y-%m-%d')
        fecha_fin = hoy.strftime('%Y-%m-%d')

    try:
        cantidad_clientes = func.count(Cliente.id_cliente).label('cantidad_clientes')

        query = db.session.query(
            Membresia.id_membresia,
            Membresia.nombre.label('membresia'),
            Membresia.precio.label('precio'),
            Membresia.duracion_dias.label('duracion_dias'),
            cantidad_clientes
        ).outerjoin(Cliente, Membresia.id_membresia == Cliente.id_membresia)

        if fecha_inicio:
            query = query.filter(Cliente.fecha_registro >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Cliente.fecha_registro <= fecha_fin)

        membresias_activas = query.group_by(Membresia.id_membresia, Membresia.nombre, Membresia.precio, Membresia.duracion_dias)\
            .order_by(cantidad_clientes.desc()).all()

        return jsonify([{
            'id_membresia': id_membresia,
            'membresia': membresia,
            'precio': float(precio) if precio else 0,
            'duracion_dias': duracion_dias,
            'cantidad_clientes': cantidad_clientes
        } for id_membresia, membresia, precio, duracion_dias, cantidad_clientes in membresias_activas])

    except Exception as e:
        return jsonify({"error": f"Error al obtener membresías activas: {str(e)}"}), 500
