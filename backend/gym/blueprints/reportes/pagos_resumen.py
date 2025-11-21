from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from gym.extensions import db
from gym.models.Pago import Pago
from gym.models.Cliente import Cliente
from sqlalchemy import func

pagos_resumen_bp = Blueprint('pagos_resumen', __name__)


@pagos_resumen_bp.get('/pagos_resumen')
@jwt_required()
def pagos_resumen():
    """Devuelve KPIs para el módulo Pagos:
    - pagos_realizados: cantidad de registros de pago con monto_pagado>0
    - membresias_usadas: cantidad de membresias distintas registradas en pagos
    - clientes_que_pagaron: cantidad de clientes con al menos un pago
    - clientes_sin_pagos: total clientes sin ningún pago
    - clientes_con_deuda: cantidad de clientes con monto_pendiente > 0 (en al menos un pago)
    - total_monto_pagado: suma de monto_pagado
    - total_deuda: suma de monto_pendiente
    """

    pagos_realizados = db.session.query(func.count(Pago.id_pago)).filter(Pago.monto_pagado > 0).scalar() or 0

    membresias_usadas = db.session.query(func.count(func.distinct(Pago.id_membresia))).scalar() or 0

    clientes_que_pagaron = db.session.query(func.count(func.distinct(Pago.id_cliente))).scalar() or 0

    total_clientes = db.session.query(func.count(Cliente.id_cliente)).scalar() or 0
    clientes_sin_pagos = max(0, (total_clientes - clientes_que_pagaron))

    clientes_con_deuda = db.session.query(func.count(func.distinct(Pago.id_cliente))).filter(Pago.monto_pendiente > 0).scalar() or 0

    total_monto_pagado = db.session.query(func.coalesce(func.sum(Pago.monto_pagado), 0)).scalar() or 0.0
    total_deuda = db.session.query(func.coalesce(func.sum(Pago.monto_pendiente), 0)).scalar() or 0.0

    return jsonify({
        'pagos_realizados': int(pagos_realizados),
        'membresias_usadas': int(membresias_usadas),
        'clientes_que_pagaron': int(clientes_que_pagaron),
        'clientes_sin_pagos': int(clientes_sin_pagos),
        'clientes_con_deuda': int(clientes_con_deuda),
        'total_monto_pagado': float(total_monto_pagado),
        'total_deuda': float(total_deuda)
    })
