from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Cliente import Cliente
from gym.models.Membresia import Membresia
from gym.models.Pago import Pago
from gym.extensions import db
from sqlalchemy import func
from datetime import datetime
 

ingresos_por_membresia_bp = Blueprint("ingresos_por_membresia", __name__)

@ingresos_por_membresia_bp.get("/ingresos_por_membresia")
@jwt_required()
def ingresos_por_membresia():
    # Parámetros opcionales para filtrar por fecha
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    # Si no se proporcionan fechas, tomar los últimos 4 meses (incluye mes actual y 3 anteriores)
    if not fecha_inicio and not fecha_fin:
        hoy = datetime.now()
        # calcular fecha_inicio = primer día del mes hace 3 meses (incluye mes actual)
        m = hoy.month - 3
        y = hoy.year
        while m <= 0:
            m += 12
            y -= 1
        inicio_mes = datetime(year=y, month=m, day=1)
        fecha_inicio = inicio_mes.strftime('%Y-%m-%d')
        fecha_fin = hoy.strftime('%Y-%m-%d')
    
    # Query base para obtener ingresos por tipo de membresía
    query = db.session.query(
        Membresia.nombre.label('membresia'),
        Membresia.precio.label('precio_membresia'),
    func.count(Pago.id_pago).label('cantidad_pagos'),
    func.sum(Pago.monto_pagado).label('total_ingresos')
    ).join(Cliente, Pago.id_cliente == Cliente.id_cliente)\
     .join(Membresia, Cliente.id_membresia == Membresia.id_membresia)\
     .filter(Pago.estado == "Confirmado")
    
    # Aplicar filtros de fecha si se proporcionan
    if fecha_inicio:
        query = query.filter(Pago.fecha_pago >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Pago.fecha_pago <= fecha_fin)
    
    # Agrupar y ordenar
    ingresos = query.group_by(Membresia.id_membresia)\
                   .order_by(func.sum(Pago.monto_pagado).desc()).all()

    return jsonify([{
        'membresia': membresia,
        'precio_membresia': float(precio_membresia),
        'cantidad_pagos': cantidad_pagos,
        'total_ingresos': float(total_ingresos) if total_ingresos else 0
    } for membresia, precio_membresia, cantidad_pagos, total_ingresos in ingresos])