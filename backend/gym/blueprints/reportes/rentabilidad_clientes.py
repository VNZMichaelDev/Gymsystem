from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Cliente import Cliente
from gym.models.Pago import Pago
from gym.models.Membresia import Membresia
from gym.models.Asistencia import Asistencia
from gym.extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta

rentabilidad_clientes_bp = Blueprint("rentabilidad_clientes", __name__)

@rentabilidad_clientes_bp.get("/rentabilidad_clientes")
@jwt_required()
def rentabilidad_clientes():
    """
    Analiza la rentabilidad de los clientes basándose en:
    - Total pagado vs frecuencia de uso
    - Valor promedio por visita
    - ROI por cliente
    """
    try:
        # Parámetros opcionales
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        limite = int(request.args.get('limite', 50))
        
        # Query base para pagos por cliente
        query_pagos = db.session.query(
            Cliente.id_cliente,
            Cliente.nombre,
            Cliente.apellido_paterno,
            Cliente.apellido_materno,
            Cliente.fecha_registro,
            Membresia.nombre.label('tipo_membresia'),
            Membresia.precio.label('precio_membresia'),
            func.sum(Pago.monto).label('total_pagado'),
            func.count(Pago.id_pago).label('total_pagos')
        ).join(Pago, Cliente.id_cliente == Pago.id_cliente)\
         .join(Membresia, Cliente.id_membresia == Membresia.id_membresia)\
         .filter(Pago.estado == "Confirmado")
        
        # Aplicar filtros de fecha
        if fecha_inicio:
            query_pagos = query_pagos.filter(Pago.fecha_pago >= fecha_inicio)
        if fecha_fin:
            query_pagos = query_pagos.filter(Pago.fecha_pago <= fecha_fin)
        
        pagos_por_cliente = query_pagos.group_by(Cliente.id_cliente).subquery()
        
        # Query para asistencias por cliente
        query_asistencias = db.session.query(
            Asistencia.id_cliente,
            func.count(Asistencia.id_asistencia).label('total_asistencias')
        )
        
        # Aplicar filtros de fecha para asistencias
        if fecha_inicio:
            query_asistencias = query_asistencias.filter(Asistencia.fecha >= fecha_inicio)
        if fecha_fin:
            query_asistencias = query_asistencias.filter(Asistencia.fecha <= fecha_fin)
        
        asistencias_por_cliente = query_asistencias.group_by(Asistencia.id_cliente).subquery()
        
        # Query final combinando pagos y asistencias
        rentabilidad = db.session.query(
            pagos_por_cliente.c.id_cliente,
            pagos_por_cliente.c.nombre,
            pagos_por_cliente.c.apellido_paterno,
            pagos_por_cliente.c.apellido_materno,
            pagos_por_cliente.c.fecha_registro,
            pagos_por_cliente.c.tipo_membresia,
            pagos_por_cliente.c.precio_membresia,
            pagos_por_cliente.c.total_pagado,
            pagos_por_cliente.c.total_pagos,
            func.coalesce(asistencias_por_cliente.c.total_asistencias, 0).label('total_asistencias')
        ).outerjoin(
            asistencias_por_cliente, 
            pagos_por_cliente.c.id_cliente == asistencias_por_cliente.c.id_cliente
        ).order_by(pagos_por_cliente.c.total_pagado.desc()).limit(limite).all()
        
        # Calcular métricas de rentabilidad
        resultados = []
        for r in rentabilidad:
            total_asistencias = r.total_asistencias or 1  # Evitar división por cero
            valor_por_visita = float(r.total_pagado) / total_asistencias
            
            # Calcular días desde registro
            fecha_registro = datetime.strptime(r.fecha_registro, "%Y-%m-%d")
            dias_miembro = (datetime.now() - fecha_registro).days or 1
            valor_mensual = (float(r.total_pagado) / dias_miembro) * 30
            
            resultados.append({
                "id_cliente": r.id_cliente,
                "nombre_completo": f"{r.nombre} {r.apellido_paterno} {r.apellido_materno}",
                "tipo_membresia": r.tipo_membresia,
                "precio_membresia": float(r.precio_membresia),
                "fecha_registro": r.fecha_registro,
                "total_pagado": float(r.total_pagado),
                "total_pagos": r.total_pagos,
                "total_asistencias": r.total_asistencias,
                "valor_por_visita": round(valor_por_visita, 2),
                "valor_mensual_promedio": round(valor_mensual, 2),
                "dias_como_miembro": dias_miembro,
                "frecuencia_uso": round(r.total_asistencias / (dias_miembro / 30), 2) if dias_miembro > 0 else 0
            })
        
        # Estadísticas generales
        if resultados:
            total_ingresos = sum(r["total_pagado"] for r in resultados)
            promedio_valor_visita = sum(r["valor_por_visita"] for r in resultados) / len(resultados)
            promedio_asistencias = sum(r["total_asistencias"] for r in resultados) / len(resultados)
        else:
            total_ingresos = promedio_valor_visita = promedio_asistencias = 0
        
        return jsonify({
            "resumen": {
                "total_clientes_analizados": len(resultados),
                "total_ingresos": round(total_ingresos, 2),
                "promedio_valor_por_visita": round(promedio_valor_visita, 2),
                "promedio_asistencias_por_cliente": round(promedio_asistencias, 2)
            },
            "clientes": resultados
        })
        
    except Exception as e:
        return jsonify({"error": f"Error al analizar rentabilidad: {str(e)}"}), 500