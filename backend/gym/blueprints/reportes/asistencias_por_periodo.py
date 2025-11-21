from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Asistencia import Asistencia
from gym.extensions import db
from sqlalchemy import func
from datetime import datetime

asistencias_por_periodo_bp = Blueprint('asistencias_por_periodo', __name__)


@asistencias_por_periodo_bp.get('/asistencias_por_periodo')
@jwt_required()
def asistencias_por_periodo():
    """Devuelve conteo de asistencias agrupado por fecha dentro de un rango.
    Query params: fecha_inicio (YYYY-MM-DD), fecha_fin (YYYY-MM-DD)
    Si faltan, se usan los últimos 4 meses por defecto.
    """
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')

        if not fecha_inicio or not fecha_fin:
            hoy = datetime.now()
            # primer día del mes hace 3 meses
            m = hoy.month - 3
            y = hoy.year
            while m <= 0:
                m += 12
                y -= 1
            inicio_mes = datetime(year=y, month=m, day=1)
            fecha_inicio = fecha_inicio or inicio_mes.strftime('%Y-%m-%d')
            fecha_fin = fecha_fin or hoy.strftime('%Y-%m-%d')

        # Query: agrupar por fecha
        rows = (
            db.session.query(
                Asistencia.fecha,
                func.count(Asistencia.id_asistencia).label('cantidad')
            )
            .filter(Asistencia.fecha >= fecha_inicio, Asistencia.fecha <= fecha_fin)
            .group_by(Asistencia.fecha)
            .order_by(Asistencia.fecha.asc())
            .all()
        )

        result = [{'fecha': r[0], 'cantidad': int(r[1])} for r in rows]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
