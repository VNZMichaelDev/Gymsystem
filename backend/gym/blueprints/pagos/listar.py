from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Pago import Pago
from gym.models.Cliente import Cliente
from gym.models.Membresia import Membresia
from sqlalchemy import or_

listar_bp = Blueprint("listar_pagos", __name__)

@listar_bp.get("/")
@jwt_required()
def listar_pagos():
    """
    Listar pagos con paginación y búsqueda
    Parámetros:
    - page: Número de página (default: 1)
    - size: Tamaño de página (default: 10, max: 100)
    - search: Término de búsqueda en nombre del cliente o documento
    - cliente_id: Filtrar por ID del cliente específico
    """
    try:
        # Parámetros de paginación
        page = max(int(request.args.get("page", 1)), 1)
        size = min(max(int(request.args.get("size", 10)), 1), 100)
        search = request.args.get("search", "").strip()
        cliente_id = request.args.get("cliente_id", "").strip()
        offset = request.args.get("offset", 0)
        
        # Convertir offset a int si se proporciona
        try:
            offset = int(offset)
        except (ValueError, TypeError):
            offset = 0
        
        # Query base con LEFT JOIN para incluir información de cliente y membresía
        query = Pago.query.join(Cliente, Pago.id_cliente == Cliente.id_cliente)\
                          .outerjoin(Membresia, Pago.id_membresia == Membresia.id_membresia)
        
        # Aplicar filtro por cliente específico
        if cliente_id:
            try:
                cliente_id = int(cliente_id)
                query = query.filter(Pago.id_cliente == cliente_id)
            except ValueError:
                pass  # Ignorar si no es un número válido
        
        # Aplicar filtro de búsqueda
        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    Cliente.nombre.ilike(like),
                    Cliente.apellido_paterno.ilike(like),
                    Cliente.apellido_materno.ilike(like),
                    Cliente.numero_documento.ilike(like),
                    Membresia.nombre.ilike(like)
                )
            )
        
        # Ordenar por fecha de pago (más recientes primero)
        query = query.order_by(Pago.fecha_pago.desc())
        
        # Aplicar paginación usando offset/limit si se proporciona offset
        if offset > 0:
            pagos = query.offset(offset).limit(size).all()
            total = query.count()
        else:
            # Usar paginación tradicional
            paginated = query.paginate(
                page=page, 
                per_page=size, 
                error_out=False
            )
            pagos = paginated.items
            total = paginated.total
        
        # Convertir a diccionarios
        pagos_data = []
        for pago in pagos:
            pago_dict = pago.to_dict()
            pagos_data.append(pago_dict)
        
        return jsonify({
            "data": pagos_data,
            "pagination": {
                "page": page if offset == 0 else None,
                "size": size,
                "total": total,
                "offset": offset if offset > 0 else None
            },
            "search": search if search else None,
            "cliente_id": cliente_id if cliente_id else None
        })
        
    except ValueError:
        return jsonify({"error": "Parámetros page y size deben ser números enteros"}), 400
    except Exception as e:
        return jsonify({"error": f"Error al listar pagos: {str(e)}"}), 500

@listar_bp.get("/<int:id_pago>")
@jwt_required()
def obtener_pago(id_pago):
    """Obtener un pago específico por ID"""
    try:
        pago = Pago.query.get(id_pago)
        if not pago:
            return jsonify({"error": "Pago no encontrado"}), 404
        
        return jsonify(pago.to_dict())
    except Exception as e:
        return jsonify({"error": f"Error al obtener pago: {str(e)}"}), 500