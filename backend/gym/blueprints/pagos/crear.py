from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from gym.models.Pago import Pago
from gym.models.Cliente import Cliente
from gym.models.Membresia import Membresia
from gym.extensions import db
from gym.utils.file_upload import save_upload
from datetime import datetime

pagos_bp = Blueprint("pagos", __name__)

@pagos_bp.post("/")
@jwt_required()
def crear_pago():
    """Registra un nuevo pago. Acepta JSON y multipart/form-data."""
    try:
        # Detectar el tipo de contenido y extraer datos
        if request.is_json:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Cuerpo JSON vacío o inválido"}), 400
            id_cliente = data.get("id_cliente")
            monto_pagado = data.get("monto_pagado")
            comprobante_file = None
        else:  # Asumir form-data
            id_cliente = request.form.get("id_cliente", type=int)
            monto_pagado = request.form.get("monto_pagado", type=float)
            comprobante_file = request.files.get('comprobante') if 'comprobante' in request.files else None

        # Validaciones básicas
        if not id_cliente or monto_pagado is None:
            return jsonify({"error": "Faltan id_cliente y monto_pagado"}), 400

        if monto_pagado <= 0:
            return jsonify({"error": "El monto debe ser mayor a 0"}), 400

        # Verificar que el cliente existe
        cliente = Cliente.query.get(id_cliente)
        if not cliente:
            return jsonify({"error": "Cliente no encontrado"}), 404

        # Verificar que el cliente tiene una membresía asignada
        if not cliente.id_membresia:
            return jsonify({"error": "El cliente no tiene una membresía asignada"}), 400

        membresia = Membresia.query.get(cliente.id_membresia)
        if not membresia:
            return jsonify({"error": "Membresía no encontrada"}), 404

        # Obtener información actual de pagos del cliente
        pagos_existentes = Pago.query.filter_by(id_cliente=id_cliente).all()
        
        # Calcular montos actuales
        total_pagado_anteriormente = sum(p.monto_pagado for p in pagos_existentes)
        monto_total = membresia.precio
        monto_pendiente_actual = monto_total - total_pagado_anteriormente

        # Validar que no se pague más de lo que debe
        if monto_pagado > monto_pendiente_actual:
            return jsonify({
                "error": f"El monto a pagar (S/ {monto_pagado:.2f}) no puede ser mayor al pendiente (S/ {monto_pendiente_actual:.2f})"
            }), 400

        # Calcular nuevo monto pendiente
        nuevo_monto_pendiente = monto_pendiente_actual - monto_pagado
        
        # Determinar estado
        estado = "Pagado" if nuevo_monto_pendiente <= 0 else "Pendiente"

        # Calcular fechas de membresía (si es el primer pago)
        if not pagos_existentes:
            # Primer pago - calcular fechas desde hoy
            fechas = Pago.calcular_fechas_membresia(membresia.duracion_dias)
            fecha_inicio_membresia = fechas["fecha_inicio"]
            fecha_fin_membresia = fechas["fecha_fin"]
        else:
            # Usar las fechas del primer pago
            primer_pago = pagos_existentes[0]
            fecha_inicio_membresia = primer_pago.fecha_inicio_membresia
            fecha_fin_membresia = primer_pago.fecha_fin_membresia

        # Manejar subida de comprobante
        comprobante_filename = None
        if comprobante_file and comprobante_file.filename:
            try:
                comprobante_filename = save_upload(comprobante_file, 'comprobantes')
            except Exception as e:
                return jsonify({"error": f"Error al subir comprobante: {str(e)}"}), 400

        # Crear el nuevo pago
        nuevo_pago = Pago(
            id_cliente=id_cliente,
            id_membresia=cliente.id_membresia,
            fecha_pago=datetime.now().strftime("%Y-%m-%d"),
            fecha_inicio_membresia=fecha_inicio_membresia,
            fecha_fin_membresia=fecha_fin_membresia,
            monto_total=monto_total,
            monto_pagado=monto_pagado,
            monto_pendiente=nuevo_monto_pendiente,
            comprobante=comprobante_filename,
            estado=estado
        )

        # Guardar en la base de datos
        db.session.add(nuevo_pago)
        db.session.commit()

        return jsonify({
            "message": "Pago registrado exitosamente",
            "pago": nuevo_pago.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al crear pago: {str(e)}"}), 500


@pagos_bp.get("/cliente/<int:id_cliente>/info")
@jwt_required()
def obtener_info_pago_cliente(id_cliente):
    """Obtiene información de pagos y deuda de un cliente específico."""
    try:
        # Verificar que el cliente existe
        cliente = Cliente.query.get(id_cliente)
        if not cliente:
            return jsonify({"error": "Cliente no encontrado"}), 404

        # Verificar que el cliente tiene membresía
        if not cliente.id_membresia:
            return jsonify({"error": "El cliente no tiene una membresía asignada"}), 400

        membresia = Membresia.query.get(cliente.id_membresia)
        if not membresia:
            return jsonify({"error": "Membresía no encontrada"}), 404

        # Obtener todos los pagos del cliente
        pagos = Pago.query.filter_by(id_cliente=id_cliente).all()

        # Calcular información de pagos
        total_pagado = sum(p.monto_pagado for p in pagos)
        monto_total = membresia.precio
        monto_pendiente = monto_total - total_pagado

        # Calcular fechas de membresía
        if pagos:
            # Usar fechas del primer pago
            primer_pago = pagos[0]
            fecha_inicio = primer_pago.fecha_inicio_membresia
            fecha_fin = primer_pago.fecha_fin_membresia
        else:
            # Calcular fechas desde hoy si no hay pagos
            fechas = Pago.calcular_fechas_membresia(membresia.duracion_dias)
            fecha_inicio = fechas["fecha_inicio"]
            fecha_fin = fechas["fecha_fin"]

        # Calcular días restantes
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
            dias_restantes = max(0, (fecha_fin_obj - datetime.now()).days)
        except:
            dias_restantes = 0

        return jsonify({
            "cliente": {
                "id_cliente": cliente.id_cliente,
                "nombre_completo": cliente.nombre_completo,
                "numero_documento": cliente.numero_documento
            },
            "membresia": {
                "id_membresia": membresia.id_membresia,
                "nombre": membresia.nombre,
                "precio": membresia.precio,
                "duracion_dias": membresia.duracion_dias
            },
            "pago_info": {
                "monto_total": monto_total,
                "total_pagado": total_pagado,
                "monto_pendiente": monto_pendiente,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "dias_restantes": dias_restantes,
                "cantidad_pagos": len(pagos)
            }
        })

    except Exception as e:
        return jsonify({"error": f"Error al obtener información: {str(e)}"}), 500