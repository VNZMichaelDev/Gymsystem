from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Asistencia import Asistencia
from gym.models.Cliente import Cliente
from gym.extensions import db
from sqlalchemy import func, extract, case
from datetime import datetime, timedelta

horarios_pico_bp = Blueprint("horarios_pico", __name__)

@horarios_pico_bp.get("/horarios_pico")
@jwt_required()
def horarios_pico():
    """
    Analiza los horarios de mayor afluencia en el gimnasio
    Proporciona insights sobre:
    - Horas pico del día
    - Días de la semana más concurridos
    - Distribución de asistencias por franjas horarias
    """
    try:
        # Parámetros opcionales
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Si no se especifica rango, usar últimos 30 días
        if not fecha_inicio:
            fecha_inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not fecha_fin:
            fecha_fin = datetime.now().strftime("%Y-%m-%d")
        
        # Query base para asistencias en el período
        query_base = db.session.query(Asistencia)\
                               .filter(Asistencia.fecha.between(fecha_inicio, fecha_fin))
        
        # 1. Análisis por horas del día
        asistencias_por_hora = db.session.query(
            func.substr(Asistencia.hora_entrada, 1, 2).label('hora'),
            func.count(Asistencia.id_asistencia).label('total_asistencias')
        ).filter(Asistencia.fecha.between(fecha_inicio, fecha_fin))\
         .group_by(func.substr(Asistencia.hora_entrada, 1, 2))\
         .order_by('hora').all()
        
        # 2. Análisis por días de la semana (0=Domingo, 6=Sábado)
        asistencias_por_dia_semana = db.session.query(
            func.strftime('%w', Asistencia.fecha).label('dia_semana'),
            func.count(Asistencia.id_asistencia).label('total_asistencias')
        ).filter(Asistencia.fecha.between(fecha_inicio, fecha_fin))\
         .group_by(func.strftime('%w', Asistencia.fecha))\
         .order_by('dia_semana').all()
        
        # 3. Análisis por franjas horarias
        franjas_horarias = db.session.query(
            case(
                (func.substr(Asistencia.hora_entrada, 1, 2).between('06', '09'), 'Madrugada (6-9 AM)'),
                (func.substr(Asistencia.hora_entrada, 1, 2).between('10', '12'), 'Mañana (10-12 PM)'),
                (func.substr(Asistencia.hora_entrada, 1, 2).between('13', '17'), 'Tarde (1-5 PM)'),
                (func.substr(Asistencia.hora_entrada, 1, 2).between('18', '21'), 'Noche (6-9 PM)'),
                else_='Otras horas'
            ).label('franja_horaria'),
            func.count(Asistencia.id_asistencia).label('total_asistencias')
        ).filter(Asistencia.fecha.between(fecha_inicio, fecha_fin))\
         .group_by('franja_horaria')\
         .order_by(func.count(Asistencia.id_asistencia).desc()).all()
        
        # 4. Análisis combinado: día de semana + hora
        heatmap_data = db.session.query(
            func.strftime('%w', Asistencia.fecha).label('dia_semana'),
            func.substr(Asistencia.hora_entrada, 1, 2).label('hora'),
            func.count(Asistencia.id_asistencia).label('total_asistencias')
        ).filter(Asistencia.fecha.between(fecha_inicio, fecha_fin))\
         .group_by('dia_semana', 'hora')\
         .order_by('dia_semana', 'hora').all()
        
        # Convertir días numéricos a nombres
        dias_semana = {
            '0': 'Domingo', '1': 'Lunes', '2': 'Martes', 
            '3': 'Miércoles', '4': 'Jueves', '5': 'Viernes', '6': 'Sábado'
        }
        
        # Procesar resultados
        horas_pico = [{
            "hora": f"{hora}:00",
            "total_asistencias": total,
            "porcentaje": round((total / sum(h[1] for h in asistencias_por_hora)) * 100, 2) if asistencias_por_hora else 0
        } for hora, total in asistencias_por_hora]
        
        dias_pico = [{
            "dia_semana": dias_semana.get(dia, f"Día {dia}"),
            "dia_numero": int(dia),
            "total_asistencias": total,
            "porcentaje": round((total / sum(d[1] for d in asistencias_por_dia_semana)) * 100, 2) if asistencias_por_dia_semana else 0
        } for dia, total in asistencias_por_dia_semana]
        
        franjas = [{
            "franja": franja,
            "total_asistencias": total,
            "porcentaje": round((total / sum(f[1] for f in franjas_horarias)) * 100, 2) if franjas_horarias else 0
        } for franja, total in franjas_horarias]
        
        # Crear matriz heatmap
        heatmap = {}
        for dia, hora, total in heatmap_data:
            if dias_semana.get(dia) not in heatmap:
                heatmap[dias_semana.get(dia)] = {}
            heatmap[dias_semana.get(dia)][f"{hora}:00"] = total
        
        # Encontrar picos absolutos
        hora_mas_concurrida = max(asistencias_por_hora, key=lambda x: x[1]) if asistencias_por_hora else None
        dia_mas_concurrido = max(asistencias_por_dia_semana, key=lambda x: x[1]) if asistencias_por_dia_semana else None
        
        return jsonify({
            "periodo_analizado": {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
            },
            "resumen": {
                "hora_pico": f"{hora_mas_concurrida[0]}:00" if hora_mas_concurrida else None,
                "asistencias_hora_pico": hora_mas_concurrida[1] if hora_mas_concurrida else 0,
                "dia_pico": dias_semana.get(dia_mas_concurrido[0]) if dia_mas_concurrido else None,
                "asistencias_dia_pico": dia_mas_concurrido[1] if dia_mas_concurrido else 0,
                "total_asistencias_periodo": sum(h[1] for h in asistencias_por_hora)
            },
            "por_horas": horas_pico,
            "por_dias_semana": dias_pico,
            "por_franjas_horarias": franjas,
            "heatmap_dia_hora": heatmap
        })
        
    except Exception as e:
        return jsonify({"error": f"Error al analizar horarios pico: {str(e)}"}), 500