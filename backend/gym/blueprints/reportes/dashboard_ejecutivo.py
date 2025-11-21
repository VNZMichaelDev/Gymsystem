from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Cliente import Cliente
from gym.models.Pago import Pago
from gym.models.Membresia import Membresia
from gym.models.Asistencia import Asistencia
from gym.extensions import db
from sqlalchemy import func, and_
from datetime import datetime, timedelta

dashboard_ejecutivo_bp = Blueprint("dashboard_ejecutivo", __name__)

@dashboard_ejecutivo_bp.get("/dashboard_ejecutivo")
@jwt_required()
def dashboard_ejecutivo():
    """
    Dashboard ejecutivo con KPIs principales del gimnasio:
    - Métricas financieras
    - Métricas de clientes
    - Métricas operacionales
    - Tendencias y comparativas
    """
    try:
        # Parámetros para comparativas
        mes_actual = datetime.now().replace(day=1)
        mes_anterior = (mes_actual - timedelta(days=1)).replace(day=1)
        inicio_año = datetime.now().replace(month=1, day=1)
        
        # Fechas en formato string
        mes_actual_str = mes_actual.strftime("%Y-%m-%d")
        mes_anterior_str = mes_anterior.strftime("%Y-%m-%d")
        fin_mes_anterior_str = (mes_actual - timedelta(days=1)).strftime("%Y-%m-%d")
        inicio_año_str = inicio_año.strftime("%Y-%m-%d")
        hoy = datetime.now().strftime("%Y-%m-%d")
        
        # === MÉTRICAS FINANCIERAS ===
        
        # Ingresos mes actual
        # Sumar los montos realmente pagados (monto_pagado) para ingresos
        ingresos_mes_actual = db.session.query(
            func.sum(Pago.monto_pagado)
        ).filter(
            and_(
                Pago.fecha_pago >= mes_actual_str,
                Pago.estado == "Confirmado"
            )
        ).scalar() or 0
        
        # Ingresos mes anterior
        ingresos_mes_anterior = db.session.query(
            func.sum(Pago.monto_pagado)
        ).filter(
            and_(
                Pago.fecha_pago >= mes_anterior_str,
                Pago.fecha_pago <= fin_mes_anterior_str,
                Pago.estado == "Confirmado"
            )
        ).scalar() or 0
        
        # Ingresos año actual
        ingresos_año = db.session.query(
            func.sum(Pago.monto_pagado)
        ).filter(
            and_(
                Pago.fecha_pago >= inicio_año_str,
                Pago.estado == "Confirmado"
            )
        ).scalar() or 0
        
        # Pagos pendientes
        # Sumar los montos pendientes sobre el campo correcto (monto_pendiente)
        pagos_pendientes = db.session.query(
            func.sum(Pago.monto_pendiente),
            func.count(Pago.id_pago)
        ).filter(Pago.estado == "Pendiente").first()

        monto_pendiente = pagos_pendientes[0] or 0
        cantidad_pendiente = pagos_pendientes[1] or 0
        
        # === MÉTRICAS DE CLIENTES ===
        
        # Total clientes activos
        total_clientes = db.session.query(func.count(Cliente.id_cliente)).scalar() or 0
        
        # Clientes nuevos mes actual
        clientes_nuevos_mes = db.session.query(
            func.count(Cliente.id_cliente)
        ).filter(Cliente.fecha_registro >= mes_actual_str).scalar() or 0
        
        # Clientes nuevos mes anterior
        clientes_nuevos_mes_anterior = db.session.query(
            func.count(Cliente.id_cliente)
        ).filter(
            and_(
                Cliente.fecha_registro >= mes_anterior_str,
                Cliente.fecha_registro <= fin_mes_anterior_str
            )
        ).scalar() or 0
        
        # Distribución por membresías
        distribucion_membresias = db.session.query(
            Membresia.nombre,
            Membresia.precio,
            func.count(Cliente.id_cliente).label('cantidad_clientes')
        ).join(Cliente, Membresia.id_membresia == Cliente.id_membresia)\
         .group_by(Membresia.id_membresia)\
         .order_by(func.count(Cliente.id_cliente).desc()).all()
        
        # === MÉTRICAS OPERACIONALES ===
        
        # Asistencias mes actual
        asistencias_mes = db.session.query(
            func.count(Asistencia.id_asistencia)
        ).filter(Asistencia.fecha >= mes_actual_str).scalar() or 0
        
        # Asistencias mes anterior
        asistencias_mes_anterior = db.session.query(
            func.count(Asistencia.id_asistencia)
        ).filter(
            and_(
                Asistencia.fecha >= mes_anterior_str,
                Asistencia.fecha <= fin_mes_anterior_str
            )
        ).scalar() or 0
        
        # Promedio asistencias por día (últimos 30 días)
        fecha_30_dias = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        asistencias_30_dias = db.session.query(
            func.count(Asistencia.id_asistencia)
        ).filter(Asistencia.fecha >= fecha_30_dias).scalar() or 0
        
        promedio_asistencias_dia = round(asistencias_30_dias / 30, 1)
        
        # Clientes activos (con asistencia en últimos 7 días)
        fecha_7_dias = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        clientes_activos_semana = db.session.query(
            func.count(func.distinct(Asistencia.id_cliente))
        ).filter(Asistencia.fecha >= fecha_7_dias).scalar() or 0
        
        # === CÁLCULOS DE VARIACIONES ===
        
        def calcular_variacion(actual, anterior):
            if anterior == 0:
                return 100 if actual > 0 else 0
            return round(((actual - anterior) / anterior) * 100, 1)
        
        variacion_ingresos = calcular_variacion(ingresos_mes_actual, ingresos_mes_anterior)
        variacion_clientes = calcular_variacion(clientes_nuevos_mes, clientes_nuevos_mes_anterior)
        variacion_asistencias = calcular_variacion(asistencias_mes, asistencias_mes_anterior)
        
        # === MÉTRICAS DERIVADAS ===
        
        # Ingreso promedio por cliente
        ingreso_promedio_cliente = round(ingresos_año / total_clientes, 2) if total_clientes > 0 else 0
        
        # Tasa de retención (clientes activos vs total)
        tasa_retencion = round((clientes_activos_semana / total_clientes) * 100, 1) if total_clientes > 0 else 0
        
        # Frecuencia promedio de uso
        frecuencia_uso = round(asistencias_30_dias / total_clientes, 1) if total_clientes > 0 else 0
        
        return jsonify({
            "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodo_actual": mes_actual.strftime("%B %Y"),
            
            "metricas_financieras": {
                "ingresos_mes_actual": round(float(ingresos_mes_actual), 2),
                "ingresos_mes_anterior": round(float(ingresos_mes_anterior), 2),
                "variacion_ingresos_porcentaje": variacion_ingresos,
                "ingresos_año_actual": round(float(ingresos_año), 2),
                "pagos_pendientes": {
                    "monto": round(float(monto_pendiente), 2),
                    "cantidad": cantidad_pendiente
                },
                "ingreso_promedio_por_cliente_anual": ingreso_promedio_cliente
            },
            
            "metricas_clientes": {
                "total_clientes_activos": total_clientes,
                "clientes_nuevos_mes_actual": clientes_nuevos_mes,
                "clientes_nuevos_mes_anterior": clientes_nuevos_mes_anterior,
                "variacion_clientes_nuevos_porcentaje": variacion_clientes,
                "clientes_activos_ultima_semana": clientes_activos_semana,
                "tasa_retencion_porcentaje": tasa_retencion,
                "distribucion_por_membresias": [{
                    "tipo_membresia": nombre,
                    "precio": float(precio),
                    "cantidad_clientes": cantidad,
                    "porcentaje": round((cantidad / total_clientes) * 100, 1) if total_clientes > 0 else 0
                } for nombre, precio, cantidad in distribucion_membresias]
            },
            
            "metricas_operacionales": {
                "asistencias_mes_actual": asistencias_mes,
                "asistencias_mes_anterior": asistencias_mes_anterior,
                "variacion_asistencias_porcentaje": variacion_asistencias,
                "promedio_asistencias_por_dia": promedio_asistencias_dia,
                "frecuencia_uso_promedio_por_cliente": frecuencia_uso
            },
            
            "kpis_principales": {
                "revenue_growth": f"{variacion_ingresos:+.1f}%",
                "customer_acquisition": f"{variacion_clientes:+.1f}%",
                "retention_rate": f"{tasa_retencion}%",
                "facility_usage": f"{promedio_asistencias_dia} asistencias/día"
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Error al generar dashboard ejecutivo: {str(e)}"}), 500