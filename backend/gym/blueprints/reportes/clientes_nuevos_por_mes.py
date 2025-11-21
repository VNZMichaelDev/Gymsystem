from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Cliente import Cliente
from gym.extensions import db
from sqlalchemy import func
from datetime import datetime

clientes_nuevos_por_mes_bp = Blueprint("clientes_nuevos_por_mes", __name__)


@clientes_nuevos_por_mes_bp.get("/clientes_nuevos_por_mes")
@jwt_required()
def clientes_nuevos_por_mes():
    """Devuelve clientes nuevos agrupados por mes entre fecha_inicio y fecha_fin.

    Parámetros opcionales de query: fecha_inicio (YYYY-MM-DD), fecha_fin (YYYY-MM-DD).
    Si no se proporcionan, se usan los últimos 4 meses (mes actual + 3 anteriores).
    """
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

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
        query = db.session.query(
            func.strftime('%Y-%m', Cliente.fecha_registro).label('mes'),
            func.count(Cliente.id_cliente).label('total_clientes_nuevos')
        )
        if fecha_inicio:
            query = query.filter(Cliente.fecha_registro >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Cliente.fecha_registro <= fecha_fin)

        clientes_nuevos = query.group_by('mes').order_by('mes').all()

        return jsonify([{
            'mes': mes,
            'total_clientes_nuevos': total_clientes_nuevos
        } for mes, total_clientes_nuevos in clientes_nuevos])
    except Exception as e:
        return jsonify({'error': f'Error al obtener clientes nuevos por mes: {str(e)}'}), 500