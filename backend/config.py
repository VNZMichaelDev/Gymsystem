# Application configuration
import os
from dotenv import load_dotenv
from datetime import timedelta

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class Config:
    # Clave secreta para sesiones y protección de formularios
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-muy-segura")

    # Configuración de la base de datos
    # En Render/Railway, DATABASE_URL se proporciona automáticamente para PostgreSQL
    # Para desarrollo local, usa SQLite
    db_url = os.getenv("DATABASE_URL", "sqlite:///gym.db")
    
    # Convertir postgresql:// a postgresql+psycopg2:// para SQLAlchemy
    if db_url and db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Deshabilitar el seguimiento de modificaciones (para ahorrar recursos)

    # Configuración de JWT para la autenticación
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-string-super-seguro-para-getfit-2025")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Los tokens expiran en 24 horas
    JWT_ALGORITHM = 'HS256'
    # Asegurar lectura por header Authorization: Bearer <token>
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Configuración para la subida de archivos
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'gym', 'uploads')
    ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,pdf").split(","))  # Extensiones permitidas
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # Tamaño máximo de archivo (16MB por defecto)

    # ...
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    # si viene con comas, conviértelo en lista
    if isinstance(CORS_ORIGINS, str) and "," in CORS_ORIGINS:
        CORS_ORIGINS = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
