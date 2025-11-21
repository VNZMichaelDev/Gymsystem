from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Cliente import Cliente
from gym.models.Asistencia import Asistencia
from gym.extensions import db
from sqlalchemy import func, and_, case
from datetime import datetime, timedelta

retencion_clientes_bp = Blueprint("retencion_clientes", __name__)

@retencion_clientes_bp.get("/retencion_clientes")
@jwt_required()
def retencion_clientes():
    """
    Analiza la retención de clientes basándose en su última asistencia
    Categoriza clientes como: Activos, En Riesgo, Inactivos
    """
    try:
        # Parámetros para definir categorías (días sin asistir)
        dias_activo = int(request.args.get('dias_activo', 7))  # Últimos 7 días = activo
        dias_riesgo = int(request.args.get('dias_riesgo', 30))  # 7-30 días = en riesgo
        
        fecha_limite_activo = (datetime.now() - timedelta(days=dias_activo)).strftime("%Y-%m-%d")
        fecha_limite_riesgo = (datetime.now() - timedelta(days=dias_riesgo)).strftime("%Y-%m-%d")
        
        # Subconsulta para obtener la última asistencia de cada cliente
        ultima_asistencia = db.session.query(
            Asistencia.id_cliente,
            func.max(Asistencia.fecha).label('ultima_fecha')
        ).group_by(Asistencia.id_cliente).subquery()
        
        # Query principal sin categorización automática (la haremos en Python)
        clientes_retencion = db.session.query(
            Cliente.id_cliente,
            Cliente.nombre,
            Cliente.apellido_paterno,
            Cliente.apellido_materno,
            Cliente.fecha_registro,
            ultima_asistencia.c.ultima_fecha
        ).outerjoin(ultima_asistencia, Cliente.id_cliente == ultima_asistencia.c.id_cliente)\
         .order_by(Cliente.fecha_registro.desc()).all()
        
        # Procesar resultados y categorizar en Python
        resultados = []
        contadores = {"Activo": 0, "En Riesgo": 0, "Inactivo": 0}
        
        for cliente in clientes_retencion:
            id_cliente, nombre, apellido_paterno, apellido_materno, fecha_registro, ultima_fecha = cliente
            
            # Determinar estado de retención
            if ultima_fecha is None:
                estado_retencion = "Inactivo"
                dias_sin_asistir = "Nunca asistió"
            elif ultima_fecha >= fecha_limite_activo:
                estado_retencion = "Activo"
                dias_sin_asistir = (datetime.now() - datetime.strptime(ultima_fecha, "%Y-%m-%d")).days
            elif ultima_fecha >= fecha_limite_riesgo:
                estado_retencion = "En Riesgo"
                dias_sin_asistir = (datetime.now() - datetime.strptime(ultima_fecha, "%Y-%m-%d")).days
            else:
                estado_retencion = "Inactivo"
                dias_sin_asistir = (datetime.now() - datetime.strptime(ultima_fecha, "%Y-%m-%d")).days
            
            contadores[estado_retencion] += 1
            
            resultados.append({
                "id_cliente": id_cliente,
                "nombre_completo": f"{nombre} {apellido_paterno} {apellido_materno}",
                "fecha_registro": fecha_registro,
                "ultima_asistencia": ultima_fecha,
                "estado_retencion": estado_retencion,
                "dias_sin_asistir": dias_sin_asistir
            })
        
        # Estadísticas generales
        total_clientes = len(resultados)
        
        return jsonify({
            "resumen": {
                "total_clientes": total_clientes,
                "activos": contadores["Activo"],
                "en_riesgo": contadores["En Riesgo"],
                "inactivos": contadores["Inactivo"],
                "tasa_retencion": round((contadores["Activo"] / total_clientes) * 100, 2) if total_clientes > 0 else 0,
                "tasa_riesgo": round((contadores["En Riesgo"] / total_clientes) * 100, 2) if total_clientes > 0 else 0
            },
            "parametros": {
                "dias_activo": dias_activo,
                "dias_riesgo": dias_riesgo,
                "fecha_limite_activo": fecha_limite_activo,
                "fecha_limite_riesgo": fecha_limite_riesgo
            },
            "clientes": resultados
        })
        
    except Exception as e:
        return jsonify({"error": f"Error al analizar retención de clientes: {str(e)}"}), 500