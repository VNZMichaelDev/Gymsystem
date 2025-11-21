# archivo: gym/blueprints/clientes/listar.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Cliente import Cliente
from sqlalchemy import or_
from sqlalchemy.orm import joinedload # <-- 1. Importamos la herramienta correcta

# Creamos el blueprint específico para listar clientes.
# Tu app.py lo importa como 'listar_clientes_bp'.
listar_bp = Blueprint('listar_clientes', __name__)

# Aceptar con y sin la barra final para evitar redirecciones que puedan perder headers
@listar_bp.route('/', methods=['GET'])
@listar_bp.route('', methods=['GET'])
@jwt_required()
def listar_clientes():
    """
    Listar clientes con paginación y búsqueda de forma eficiente.
    Requiere un token JWT válido.
    """
    try:
        # Parámetros de paginación
        page = max(int(request.args.get("page", 1)), 1)
        size = min(max(int(request.args.get("size", 10)), 1), 100)
        search = request.args.get("search", "").strip()
        
        # --- ¡CORRECCIÓN CLAVE! ---
        # 2. Cambiamos la consulta para usar 'joinedload'.
        #    Esto carga los datos de la membresía en la misma consulta
        #    y soluciona el problema de lentitud.
        query = Cliente.query.options(joinedload(Cliente.membresia))
        
        # El resto de tu lógica de búsqueda y paginación está perfecta.
        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    Cliente.nombre.ilike(like),
                    Cliente.apellido_paterno.ilike(like),
                    Cliente.apellido_materno.ilike(like),
                    Cliente.numero_documento.ilike(like),
                    Cliente.correo.ilike(like)
                )
            )
        
        query = query.order_by(Cliente.fecha_registro.desc())
        
        paginated = query.paginate(page=page, per_page=size, error_out=False)
        
        # Esta línea ahora es muy eficiente gracias a los cambios.
        return jsonify({
            "data": [cliente.to_dict(include_membresia=True) for cliente in paginated.items],
            # Campos de paginación en objeto dedicado
            "pagination": {
                "page": page,
                "size": size,
                "total": paginated.total,
                "pages": paginated.pages,
                "has_prev": paginated.has_prev,
                "has_next": paginated.has_next,
                "prev_num": paginated.prev_num,
                "next_num": paginated.next_num
            },
            # Duplicamos algunos campos al tope para compatibilidad con frontends previos
            "total": paginated.total,
            "pages": paginated.pages,
            "page": page,
            "size": size,
            "search": search if search else None
        })
        
    except ValueError:
        return jsonify({"error": "Parámetros page y size deben ser números enteros"}), 400
    except Exception as e:
        return jsonify({"error": f"Error al listar clientes: {str(e)}"}), 500