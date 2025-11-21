# Flask extensions configuration (db, migrate, jwt, cors)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def init_cors(app):
    """Inicializar CORS con configuración permisiva para desarrollo"""
    CORS(app, 
         origins=["*"],  # Permitir todos los orígenes (para desarrollo)
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"],
         supports_credentials=True
    )
