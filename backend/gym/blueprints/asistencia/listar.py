from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Asistencia import Asistencia

listar_bp = Blueprint("listar_asistencias", __name__)

@listar_bp.get("/")
@jwt_required()
def listar_asistencias():
    """
    Listar asistencias con ordenamiento por fecha/hora (más recientes primero)
    """
    try:
        # Obtener todas las asistencias ordenadas por fecha y hora
        asistencias = Asistencia.query.order_by(
            Asistencia.fecha.desc(),
            Asistencia.hora_entrada.desc()
        ).all()
        
        # Convertir a diccionario usando el método to_dict()
        resultado = [asistencia.to_dict() for asistencia in asistencias]
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"error": f"Error al listar asistencias: {str(e)}"}), 500
