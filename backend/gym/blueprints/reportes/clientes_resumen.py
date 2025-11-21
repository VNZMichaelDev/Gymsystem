from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Cliente import Cliente
from gym.models.Membresia import Membresia
from gym.extensions import db
from sqlalchemy import func
from datetime import date, timedelta

clientes_resumen_bp = Blueprint('clientes_resumen', __name__)


@clientes_resumen_bp.get('/clientes_resumen')
@jwt_required()
def clientes_resumen():
    """Devuelve un resumen con counts: total, vip, basica y registrados_ultimo_mes."""
    # Fechas para el último mes
    today = date.today()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)

    start_last = first_day_last_month.strftime('%Y-%m-%d')
    start_this = first_day_this_month.strftime('%Y-%m-%d')

    # Total de clientes
    total = db.session.query(func.count(Cliente.id_cliente)).scalar() or 0

    # Clientes con membresía cuyo nombre contiene 'VIP' (case-insensitive)
    vip_count = db.session.query(func.count(Cliente.id_cliente))\
        .join(Membresia, Cliente.id_membresia == Membresia.id_membresia)\
        .filter(func.lower(Membresia.nombre).like('%vip%'))\
        .scalar() or 0

    # Clientes con membresía cuyo nombre contiene 'básica' o 'basica' (case-insensitive)
    basica_count = db.session.query(func.count(Cliente.id_cliente))\
        .join(Membresia, Cliente.id_membresia == Membresia.id_membresia)\
        .filter(func.lower(Membresia.nombre).like('%basica%'))\
        .scalar() or 0

    # Clientes registrados en el último mes (entre start_last y start_this)
    registrados_ultimo_mes = db.session.query(func.count(Cliente.id_cliente))\
        .filter(Cliente.fecha_registro >= start_last, Cliente.fecha_registro < start_this)\
        .scalar() or 0

    return jsonify({
        'total': int(total),
        'vip': int(vip_count),
        'basica': int(basica_count),
        'registrados_ultimo_mes': int(registrados_ultimo_mes),
        'period': { 'start_last_month': start_last, 'start_this_month': start_this }
    })
