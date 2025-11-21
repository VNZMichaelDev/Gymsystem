# gym/auth/views.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from gym.models import Usuario  # Asegúrate que la importación del modelo sea correcta
from gym.extensions import db

# --- CORRECCIÓN ---
# Se eliminó la importación de 'bcrypt' ya que no se utilizará.
# El modelo ya maneja la verificación de contraseñas.

auth_bp = Blueprint("auth", __name__)

# Ruta para login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Faltan el correo y la contraseña"}), 400

    email = data.get("email").strip().lower()
    password = data.get("password")

    # Buscar usuario en la base de datos por su email (mapeado a la columna 'correo')
    user = Usuario.query.filter_by(email=email).first()

    # --- CORRECCIÓN ---
    # 1. Se comprueba si el usuario existe.
    # 2. Se usa el método 'check_password' del modelo, que utiliza 'werkzeug'.
    #    Esto resuelve la inconsistencia de hashing.
    if user is None or not user.check_password(password):
        return jsonify({"message": "Credenciales inválidas"}), 401

    # --- CORRECCIÓN ---
    # Se cambió 'user.id_usuario' por 'user.id' para que coincida con el
    # nombre del atributo en el modelo.
    # La identidad del token ahora es el ID del usuario.
    access_token = create_access_token(
        identity=str(user.id),  # PyJWT requiere que 'sub' sea string
        expires_delta=timedelta(hours=8)
    )
    
    return jsonify(access_token=access_token)


# Ruta de perfil para verificar el token
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    # Obtener la identidad del usuario a partir del token JWT (que guardamos como user.id)
    current_user_id = get_jwt_identity()
    # Convertir a int para consultas SQLAlchemy
    try:
        uid = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({"message": "Token inválido", "error": "Invalid subject type"}), 401
    user = Usuario.query.get(uid)

    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # --- CORRECCIÓN ---
    # Se usa el método to_dict() del modelo para devolver la información
    # del usuario de forma consistente y segura.
    return jsonify(user.to_dict())

# Alias simple para validación del token desde clientes (Postman/Frontend)
@auth_bp.route("/validate", methods=["GET", "POST"])
@jwt_required()
def validate():
    # Si llega aquí, el token es válido
    current_user_id = get_jwt_identity()
    return jsonify({"valid": True, "user_id": current_user_id}), 200
# ... (tus rutas de login y profile) ...

@auth_bp.route("/usuarios", methods=["GET"])
@jwt_required()
def get_usuarios():
    """
    Devuelve una lista de todos los usuarios.
    (Opcional: podrías restringir esto solo a roles de 'admin')
    """
    try:
        usuarios = Usuario.query.all()
        # Usamos el to_dict() que ya tenías en tu modelo Usuario
        return jsonify([user.to_dict() for user in usuarios]), 200
    except Exception as e:
        return jsonify({"message": f"Error al obtener usuarios: {str(e)}"}), 500