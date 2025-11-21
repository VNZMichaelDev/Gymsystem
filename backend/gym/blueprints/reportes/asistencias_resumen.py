from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Asistencia import Asistencia
from gym.extensions import db
from sqlalchemy import func
from datetime import datetime

asistencias_resumen_bp = Blueprint('asistencias_resumen', __name__)


@asistencias_resumen_bp.get('/asistencias_resumen')
@jwt_required()
def asistencias_resumen():
    """
    Retorna resumen de asistencias:
    - asistencias_hoy: cantidad de asistencias en la fecha actual
    - promedio_horas: promedio de duración por asistencia (horas)
    - dia_mas_registros: { fecha, cantidad }
    - dia_menos_registros: { fecha, cantidad }
    """
    try:
        hoy = datetime.now().strftime('%Y-%m-%d')

        asistencias_hoy = Asistencia.query.filter(Asistencia.fecha == hoy).count() or 0

        # Calcular promedio de duración en minutos para registros con hora_salida
        registros = Asistencia.query.filter(Asistencia.hora_salida.isnot(None)).all()
        total_minutes = 0
        count_with_duration = 0
        for r in registros:
            try:
                h_in = datetime.strptime(r.hora_entrada, '%H:%M')
                h_out = datetime.strptime(r.hora_salida, '%H:%M')
                # si la salida es anterior a la entrada asumimos que pasó a otro día -> ignorar o ajustar
                delta = (h_out - h_in).total_seconds() / 60.0
                if delta < 0:
                    # ajustar sumando 24h
                    delta += 24*60
                total_minutes += delta
                count_with_duration += 1
            except Exception:
                continue

        promedio_horas = (total_minutes / count_with_duration / 60.0) if count_with_duration else 0.0

        # Día con más y menos registros (group by fecha)
        counts = db.session.query(
            Asistencia.fecha,
            func.count(Asistencia.id_asistencia).label('cantidad')
        ).group_by(Asistencia.fecha).order_by(func.count(Asistencia.id_asistencia).desc()).all()

        dia_mas = {'fecha': counts[0][0], 'cantidad': int(counts[0][1])} if counts else None
        dia_menos = {'fecha': counts[-1][0], 'cantidad': int(counts[-1][1])} if counts else None

        return jsonify({
            'asistencias_hoy': int(asistencias_hoy),
            'promedio_horas': round(promedio_horas, 2),
            'dia_mas_registros': dia_mas,
            'dia_menos_registros': dia_menos
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
