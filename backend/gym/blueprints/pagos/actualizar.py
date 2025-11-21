from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Pago import Pago
from gym.models.Cliente import Cliente
from gym.models.Membresia import Membresia
from gym.extensions import db
from gym.utils.file_upload import save_upload
from datetime import datetime

actualizar_bp = Blueprint("actualizar_pago", __name__)

@actualizar_bp.put("/<int:id_pago>")
@jwt_required()
def actualizar_pago(id_pago):
    """Actualiza un pago existente"""
    try:
        pago = Pago.query.get(id_pago)
        if not pago:
            return jsonify({"error": "Pago no encontrado"}), 404

        # Obtener datos de la petición
        if request.is_json:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Cuerpo JSON vacío o inválido"}), 400
            
            monto_pagado = data.get("monto_pagado")
            estado = data.get("estado")
            comprobante_file = None
        else:  # form-data
            monto_pagado = request.form.get("monto_pagado", type=float)
            estado = request.form.get("estado")
            comprobante_file = request.files.get('comprobante') if 'comprobante' in request.files else None

        # Validaciones
        if monto_pagado is not None:
            if monto_pagado <= 0:
                return jsonify({"error": "El monto debe ser mayor a 0"}), 400

            # Validar que el nuevo monto no exceda el total de la membresía
            cliente = Cliente.query.get(pago.id_cliente)
            if cliente and cliente.id_membresia:
                membresia = Membresia.query.get(cliente.id_membresia)
                if membresia:
                    # Calcular total pagado por otros pagos del mismo cliente
                    otros_pagos = Pago.query.filter(
                        Pago.id_cliente == pago.id_cliente,
                        Pago.id_pago != id_pago
                    ).all()
                    
                    total_otros_pagos = sum(p.monto_pagado for p in otros_pagos)
                    
                    if (total_otros_pagos + monto_pagado) > membresia.precio:
                        return jsonify({
                            "error": f"El monto total no puede exceder el precio de la membresía (S/ {membresia.precio:.2f})"
                        }), 400

        # Actualizar campos
        campos_actualizados = []
        
        if monto_pagado is not None and monto_pagado != pago.monto_pagado:
            pago.monto_pagado = monto_pagado
            
            # Recalcular monto pendiente
            cliente = Cliente.query.get(pago.id_cliente)
            if cliente and cliente.id_membresia:
                membresia = Membresia.query.get(cliente.id_membresia)
                if membresia:
                    todos_los_pagos = Pago.query.filter_by(id_cliente=pago.id_cliente).all()
                    total_pagado = sum(p.monto_pagado for p in todos_los_pagos)
                    pago.monto_pendiente = membresia.precio - total_pagado
            
            campos_actualizados.append("monto_pagado")

        if estado and estado != pago.estado:
            if estado in ['Pendiente', 'Pagado', 'Vencido']:
                pago.estado = estado
                campos_actualizados.append("estado")
            else:
                return jsonify({"error": "Estado inválido. Debe ser: Pendiente, Pagado o Vencido"}), 400

        # Manejar subida de nuevo comprobante
        if comprobante_file and comprobante_file.filename:
            try:
                comprobante_filename = save_upload(comprobante_file, 'comprobantes')
                pago.comprobante = comprobante_filename
                campos_actualizados.append("comprobante")
            except Exception as e:
                return jsonify({"error": f"Error al subir comprobante: {str(e)}"}), 400

        if not campos_actualizados:
            return jsonify({"message": "No se realizaron cambios"}), 200

        # Guardar cambios
        db.session.commit()

        return jsonify({
            "message": f"Pago actualizado exitosamente. Campos modificados: {', '.join(campos_actualizados)}",
            "pago": pago.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar pago: {str(e)}"}), 500


@actualizar_bp.patch("/<int:id_pago>/estado")
@jwt_required()
def actualizar_estado_pago(id_pago):
    """Actualiza solo el estado de un pago"""
    try:
        pago = Pago.query.get(id_pago)
        if not pago:
            return jsonify({"error": "Pago no encontrado"}), 404

        data = request.get_json()
        if not data or 'estado' not in data:
            return jsonify({"error": "Se requiere el campo 'estado'"}), 400

        nuevo_estado = data['estado']
        if nuevo_estado not in ['Pendiente', 'Pagado', 'Vencido']:
            return jsonify({"error": "Estado inválido. Debe ser: Pendiente, Pagado o Vencido"}), 400

        estado_anterior = pago.estado
        pago.estado = nuevo_estado
        
        db.session.commit()

        return jsonify({
            "message": f"Estado del pago actualizado de '{estado_anterior}' a '{nuevo_estado}'",
            "pago": pago.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar estado del pago: {str(e)}"}), 500