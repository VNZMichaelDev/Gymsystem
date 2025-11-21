from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Cliente import Cliente
from gym.extensions import db

eliminar_bp = Blueprint("eliminar_cliente", __name__)

@eliminar_bp.delete("/<int:id_cliente>")
@jwt_required()
def eliminar_cliente(id_cliente):
    # Buscar el cliente por ID
    cliente = Cliente.query.get(id_cliente)
    
    # Verificar si el cliente existe
    if not cliente:
        return jsonify({
            "success": False,
            "message": f"El cliente con ID {id_cliente} no existe en el sistema"
        }), 404
    
    # Verificar si se está solicitando confirmación
    confirmar = request.args.get('confirmar', '').lower()
    
    if confirmar != 'true':
        # Mostrar información del cliente y pedir confirmación
        return jsonify({
            "success": False,
            "message": "¿Está seguro que desea eliminar este cliente?",
            "cliente": {
                "id_cliente": cliente.id_cliente,
                "nombre_completo": f"{cliente.nombre} {cliente.apellido_paterno} {cliente.apellido_materno}",
                "numero_documento": cliente.numero_documento,
                "correo": cliente.correo,
                "telefono": cliente.telefono
            },
            "instrucciones": f"Para confirmar la eliminación, haga la petición nuevamente con el parámetro: ?confirmar=true"
        }), 200
    
    try:
        # Eliminar el cliente
        nombre_completo = f"{cliente.nombre} {cliente.apellido_paterno} {cliente.apellido_materno}"
        db.session.delete(cliente)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Cliente '{nombre_completo}' eliminado exitosamente"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al eliminar el cliente: {str(e)}"
        }), 500
