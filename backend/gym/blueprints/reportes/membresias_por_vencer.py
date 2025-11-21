from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Pago import Pago
from gym.models.Cliente import Cliente
from gym.models.Membresia import Membresia
from gym.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import or_

membresias_por_vencer_bp = Blueprint('membresias_por_vencer', __name__)


@membresias_por_vencer_bp.get('/membresias_por_vencer')
@jwt_required()
def membresias_por_vencer():
    """Devuelve una lista mínima de clientes con la próxima fecha_fin de membresía
    y el monto pendiente, para los que vencen en los próximos `days` días.
    Query params:
      - days (int) default 7
    Response: { data: [ { id_cliente, cliente_nombre, fecha_fin, monto_pendiente, id_pago, membresia_nombre } ] }
    """
    try:
        days = int(request.args.get('days', 7))
        if days < 1: days = 7

        today = datetime.now().date()
        max_date = today + timedelta(days=days)
        today_str = today.strftime('%Y-%m-%d')
        max_str = max_date.strftime('%Y-%m-%d')

        # Obtener pagos cuya fecha_fin_membresia o fecha_fin esté en el rango
        pagos = Pago.query.filter(
            Pago.fecha_fin_membresia >= today_str,
            Pago.fecha_fin_membresia <= max_str
        ).all()

        # Agrupar por cliente, quedándonos con la fecha_fin más cercana
        by_client = {}
        for p in pagos:
            cliente = Cliente.query.get(p.id_cliente)
            membresia = Membresia.query.get(p.id_membresia) if p.id_membresia else None
            fecha_fin = p.fecha_fin_membresia
            if not fecha_fin:
                continue
            key = p.id_cliente
            entry = {
                'id_cliente': p.id_cliente,
                'cliente_nombre': cliente.nombre_completo if cliente else '',
                'fecha_fin': fecha_fin,
                'monto_pendiente': float(p.monto_pendiente or 0),
                'id_pago': p.id_pago,
                'membresia_nombre': membresia.nombre if membresia else None
            }
            # Mantener la fecha_fin más temprana
            if key not in by_client:
                by_client[key] = entry
            else:
                if entry['fecha_fin'] < by_client[key]['fecha_fin']:
                    by_client[key] = entry

        data = list(by_client.values())
        # Ordenar por fecha_fin asc
        data.sort(key=lambda x: x['fecha_fin'])

        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'error': f'Error al calcular membresías por vencer: {str(e)}'}), 500
