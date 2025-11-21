from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from gym.models.Asistencia import Asistencia
from gym.models.Cliente import Cliente
from gym.extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta

asistencias_por_cliente_bp = Blueprint("asistencias_por_cliente", __name__)

@asistencias_por_cliente_bp.get("/asistencias_por_cliente")
@jwt_required()
def asistencias_por_cliente():
    # Parámetros opcionales para filtrar por fecha
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # Query base
    query = db.session.query(
        Cliente.nombre,
        Cliente.apellido_paterno,
        Cliente.apellido_materno,
        Cliente.numero_documento,
        func.count(Asistencia.id_asistencia).label('total_asistencias')
    ).join(Asistencia, Cliente.id_cliente == Asistencia.id_cliente)
    
    # Aplicar filtros de fecha si se proporcionan
    if fecha_inicio:
        query = query.filter(Asistencia.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Asistencia.fecha <= fecha_fin)
    
    # Agrupar y ordenar
    asistencias = query.group_by(Cliente.id_cliente)\
                      .order_by(func.count(Asistencia.id_asistencia).desc()).all()

    return jsonify([{
        'cliente': f"{nombre} {apellido_paterno} {apellido_materno}",
        'numero_documento': numero_documento,
        'total_asistencias': total_asistencias
    } for nombre, apellido_paterno, apellido_materno, numero_documento, total_asistencias in asistencias])
