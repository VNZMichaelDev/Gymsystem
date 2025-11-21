# Flask application entry point
from flask import Flask, app, jsonify
from config import Config
from gym.extensions import db, migrate, jwt, init_cors
from gym.blueprints.auth.views import auth_bp  # Importa el blueprint de autenticación
from gym.blueprints.clientes.crear import clientes_bp  # Importa el blueprint de clientes
from gym.blueprints.clientes.views import listar_bp as listar_clientes_bp # Importa el blueprint de listar clientes
from gym.blueprints.clientes.actualizar import actualizar_bp as actualizar_clientes_bp # Importa el blueprint de actualizar clientes
from gym.blueprints.clientes.eliminar import eliminar_bp as eliminar_clientes_bp # Importa el blueprint de eliminar clientes
from gym.blueprints.pagos.crear import pagos_bp # Importa el blueprint de  crear pagos
from gym.blueprints.pagos.listar import listar_bp as listar_pagos_bp # Importa el blueprint de listar pagos
from gym.blueprints.pagos.actualizar import actualizar_bp as actualizar_pagos_bp # Importa el blueprint de actualizar pagos
from gym.blueprints.pagos.eliminar import eliminar_bp as eliminar_pagos_bp # Importa el blueprint de eliminar pagos
from gym.blueprints.pagos.descargar import descargar_comprobante_bp # Importa el blueprint de descarga segura
#membresias 
from gym.blueprints.membresias.crear import membresias_bp as crear_membresia_bp
from gym.blueprints.membresias.listar import listar_bp as listar_membresias_bp
from gym.blueprints.membresias.actualizar import actualizar_bp as actualizar_membresia_bp
from gym.blueprints.membresias.eliminar import eliminar_bp as eliminar_membresia_bp

# Asistencias
from gym.blueprints.asistencia.crear import asistencias_bp as crear_asistencia_bp
from gym.blueprints.asistencia.listar import listar_bp as listar_asistencias_bp
from gym.blueprints.asistencia.actualizar import actualizar_bp as actualizar_asistencia_bp
from gym.blueprints.asistencia.eliminar import eliminar_bp as eliminar_asistencia_bp

# Reportes
from gym.blueprints.reportes.asistencias_por_cliente import asistencias_por_cliente_bp
from gym.blueprints.reportes.clientes_nuevos_por_mes import clientes_nuevos_por_mes_bp
from gym.blueprints.reportes.ingresos_por_membresia import ingresos_por_membresia_bp
from gym.blueprints.reportes.membresias_activas import membresias_activas_bp
from gym.blueprints.reportes.pagos_pendientes import pagos_pendientes_bp
from gym.blueprints.reportes.pagos_por_mes import pagos_por_mes_bp
from gym.blueprints.reportes.retencion_clientes import retencion_clientes_bp
from gym.blueprints.reportes.rentabilidad_clientes import rentabilidad_clientes_bp
from gym.blueprints.reportes.horarios_pico import horarios_pico_bp
from gym.blueprints.reportes.dashboard_ejecutivo import dashboard_ejecutivo_bp
from gym.blueprints.reportes.membresias_por_vencer import membresias_por_vencer_bp
from gym.blueprints.reportes.clientes_resumen import clientes_resumen_bp
from gym.blueprints.reportes.pagos_resumen import pagos_resumen_bp
from gym.blueprints.reportes.membresias_resumen import membresias_resumen_bp
from gym.blueprints.reportes.asistencias_resumen import asistencias_resumen_bp
from gym.blueprints.reportes.asistencias_por_periodo import asistencias_por_periodo_bp
from gym.blueprints.reportes.membresias_por_precio import membresias_por_precio_bp


# Importar todos los modelos para que SQLAlchemy los registre
from gym.models.Usuario import Usuario
from gym.models.Membresia import Membresia
from gym.models.Cliente import Cliente
from gym.models.Pago import Pago
from gym.models.Asistencia import Asistencia
def create_app():
    import os
    # Configurar Flask para servir archivos estáticos del frontend
    # Buscar frontend en la ruta relativa correcta
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    
    # Si no existe, usar la carpeta actual como fallback
    if not os.path.exists(frontend_path):
        frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'frontend'))
    
    app = Flask(__name__, static_folder=frontend_path, static_url_path='/')

    # Cargar las configuraciones del archivo config.py
    app.config.from_object(Config)
    # Inicializar las extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)  # Inicializa JWT
    init_cors(app)  # Inicializar CORS
    
    # Crear tablas automáticamente si no existen
    with app.app_context():
        db.create_all()
        
        # Crear usuario admin por defecto si no existe
        admin_email = "admin@gym.local"
        admin_user = Usuario.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = Usuario(email=admin_email)
            admin_user.set_password("admin123")
            db.session.add(admin_user)
            db.session.commit()
            print(f"✅ Usuario admin creado: {admin_email}")
    
    # Handlers de JWT
    @jwt.unauthorized_loader
    def no_token(msg):
        return jsonify({"message": "Token de acceso requerido"}), 401
    
    @jwt.expired_token_loader
    def token_expired(jwt_header, jwt_payload):
        return jsonify({"message": "Token expirado"}), 401
    
    @jwt.invalid_token_loader
    def invalid_token(error):
        # Incluir detalle para facilitar depuración desde Postman/Frontend
        return jsonify({"message": "Token inválido", "error": str(error)}), 401
    
    @jwt.needs_fresh_token_loader
    def needs_fresh(jwt_header, jwt_payload):
        return jsonify({"message": "Se requiere un token 'fresh'"}), 401
    
    @jwt.revoked_token_loader
    def revoked(jwt_header, jwt_payload):
        return jsonify({"message": "Token revocado"}), 401
    
    # Handlers de errores globales
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"message": "Recurso no encontrado"}), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"message": "Solicitud inválida"}), 400
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"message": "Error interno del servidor"}), 500
    
    @app.errorhandler(422)
    def validation_error(error):
        return jsonify({"message": "Error de validación"}), 422
    
    init_cors(app)

    # Registrar los blueprints
    #clientes
    app.register_blueprint(auth_bp, url_prefix="/api/auth")  # Registra el blueprint de auth
    app.register_blueprint(clientes_bp, url_prefix="/api/clientes")  # Registra el blueprint de clientes (crear/obtener)
    app.register_blueprint(listar_clientes_bp, url_prefix="/api/clientes") # Registrar el blueprint de listar clientes
    app.register_blueprint(actualizar_clientes_bp, url_prefix="/api/clientes") # Registrar el blueprint de actualizar clientes
    app.register_blueprint(eliminar_clientes_bp, url_prefix="/api/clientes") # Registrar el blueprint de eliminar clientes
    #pagos
    app.register_blueprint(pagos_bp, url_prefix="/api/pagos") # Registrar el blueprint de crear pagos
    app.register_blueprint(listar_pagos_bp, url_prefix="/api/pagos") # Registrar el blueprint de listar pagos
    app.register_blueprint(actualizar_pagos_bp, url_prefix="/api/pagos") # Registrar el blueprint de actualizar pagos
    app.register_blueprint(eliminar_pagos_bp, url_prefix="/api/pagos") # Registrar el blueprint de eliminar pagos
    app.register_blueprint(descargar_comprobante_bp, url_prefix="/api/pagos") # Registrar el blueprint de descarga segura
    #membresias
    app.register_blueprint(crear_membresia_bp, url_prefix="/api/membresias")
    app.register_blueprint(listar_membresias_bp, url_prefix="/api/membresias")
    app.register_blueprint(actualizar_membresia_bp, url_prefix="/api/membresias")
    app.register_blueprint(eliminar_membresia_bp, url_prefix="/api/membresias")
    
    #asistencias
    app.register_blueprint(crear_asistencia_bp, url_prefix="/api/asistencias")
    app.register_blueprint(listar_asistencias_bp, url_prefix="/api/asistencias")
    app.register_blueprint(actualizar_asistencia_bp, url_prefix="/api/asistencias")
    app.register_blueprint(eliminar_asistencia_bp, url_prefix="/api/asistencias")
    
    # Reportes
    app.register_blueprint(asistencias_por_cliente_bp, url_prefix="/api/reportes")
    app.register_blueprint(clientes_nuevos_por_mes_bp, url_prefix="/api/reportes")
    app.register_blueprint(ingresos_por_membresia_bp, url_prefix="/api/reportes")
    app.register_blueprint(membresias_activas_bp, url_prefix="/api/reportes")
    app.register_blueprint(pagos_pendientes_bp, url_prefix="/api/reportes")
    app.register_blueprint(pagos_por_mes_bp, url_prefix="/api/reportes")
    app.register_blueprint(retencion_clientes_bp, url_prefix="/api/reportes")
    app.register_blueprint(rentabilidad_clientes_bp, url_prefix="/api/reportes")
    app.register_blueprint(horarios_pico_bp, url_prefix="/api/reportes")
    app.register_blueprint(dashboard_ejecutivo_bp, url_prefix="/api/reportes")
    app.register_blueprint(membresias_por_vencer_bp, url_prefix="/api/reportes")
    app.register_blueprint(clientes_resumen_bp, url_prefix="/api/reportes")
    app.register_blueprint(pagos_resumen_bp, url_prefix="/api/reportes")
    app.register_blueprint(membresias_resumen_bp, url_prefix="/api/reportes")
    app.register_blueprint(membresias_por_precio_bp, url_prefix="/api/reportes")
    app.register_blueprint(asistencias_resumen_bp, url_prefix="/api/reportes")
    app.register_blueprint(asistencias_por_periodo_bp, url_prefix="/api/reportes")
    
    @app.get("/api/health")
    def health():
        return {"status": "ok"}
    
    # Servir index.html en la raíz para SPA
    @app.get("/")
    def serve_index():
        import os
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return app.send_static_file('index.html')
        return {"message": "Frontend not found"}, 404

    return app


# Esta parte es la que falta en tu archivo app.py
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)  # Inicia el servidor en el puerto 5000
