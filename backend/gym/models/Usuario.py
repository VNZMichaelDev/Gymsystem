# gym/models/usuario.py

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from gym.extensions import db

class Usuario(db.Model):
    __tablename__ = 'Usuarios'

    # --- CORRECCIÓN ---
    # Se mapean las columnas para que coincidan EXACTAMENTE
    # con la estructura de tu tabla 'Usuarios' en el archivo .sql
    # Se eliminaron los campos 'rol', 'nombre_completo' y 'nombre_usuario'
    # que no existen en la base de datos.

    id = db.Column('id_usuario', db.Integer, primary_key=True)
    email = db.Column('correo', db.String(120), unique=True, nullable=False)
    password = db.Column('contrasena_hash', db.String(255), nullable=False)
    fecha_creacion = db.Column('fecha_creacion', db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Columnas para reset de contraseña
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password_to_set):
        """Genera el hash de la contraseña usando werkzeug."""
        self.password = generate_password_hash(password_to_set)

    def check_password(self, password_to_check):
        """Verifica la contraseña contra el hash usando werkzeug."""
        return check_password_hash(self.password, password_to_check)

    def __repr__(self):
        return f'<Usuario {self.email}>'
    
    def to_dict(self):
        # --- CORRECCIÓN ---
        # Se eliminaron los campos que no existen del diccionario de retorno.
        return {
            'id': self.id,
            'email': self.email,
            'fecha_creacion': self.fecha_creacion.isoformat()
        }