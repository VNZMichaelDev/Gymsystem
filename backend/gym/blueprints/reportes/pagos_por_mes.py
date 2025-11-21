from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Pago import Pago
from gym.extensions import db
from sqlalchemy import func

pagos_por_mes_bp = Blueprint("pagos_por_mes", __name__)

@pagos_por_mes_bp.get("/pagos_por_mes")
@jwt_required()
def pagos_por_mes():
    # Agrupar por mes y calcular el total de pagos confirmados
    try:
        # Crear alias para la columna mes
        mes_column = func.strftime('%Y-%m', Pago.fecha_pago).label('mes')
        
        # Primero intentamos con filtro por estado
        pagos = db.session.query(
            mes_column,
            func.sum(Pago.monto).label('total_pagos'),
            func.count(Pago.id_pago).label('cantidad_pagos')
        ).filter(Pago.estado == "Confirmado")\
         .group_by(mes_column)\
         .order_by(mes_column).all()

        return jsonify([{
            'mes': mes, 
            'total_pagos': float(total_pagos) if total_pagos else 0,
            'cantidad_pagos': cantidad_pagos
        } for mes, total_pagos, cantidad_pagos in pagos])
    
    except Exception as e:
        # Si falla con el estado, intentamos sin filtro de estado
        try:
            mes_column = func.strftime('%Y-%m', Pago.fecha_pago).label('mes')
            
            pagos = db.session.query(
                mes_column,
                func.sum(Pago.monto).label('total_pagos'),
                func.count(Pago.id_pago).label('cantidad_pagos')
            ).group_by(mes_column)\
             .order_by(mes_column).all()

            return jsonify({
                "mensaje": "Mostrando todos los pagos (confirmados y pendientes)",
                "datos": [{
                    'mes': mes, 
                    'total_pagos': float(total_pagos) if total_pagos else 0,
                    'cantidad_pagos': cantidad_pagos
                } for mes, total_pagos, cantidad_pagos in pagos]
            })
        except Exception as e2:
            return jsonify({"error": f"Error al obtener pagos por mes: {str(e2)}"}), 500
