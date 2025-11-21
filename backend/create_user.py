#!/usr/bin/env python
"""
Script para crear un nuevo usuario en la base de datos.
Uso: python create_user.py <email> <password>
Ejemplo: python create_user.py admin@gym.local admin123
"""
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash
from app import create_app, db
from gym.models.Usuario import Usuario

def create_user(email, password):
    """Crea un nuevo usuario en la base de datos."""
    app = create_app()
    
    with app.app_context():
        # Verificar si el usuario ya existe
        existing_user = Usuario.query.filter_by(email=email).first()
        if existing_user:
            print(f"❌ El usuario {email} ya existe")
            return False
        
        # Crear nuevo usuario
        user = Usuario(email=email)
        user.set_password(password)
        user.fecha_creacion = datetime.utcnow()
        
        try:
            db.session.add(user)
            db.session.commit()
            print(f"✅ Usuario creado exitosamente:")
            print(f"   Email: {email}")
            print(f"   Contraseña: {password}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear usuario: {e}")
            return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python create_user.py <email> <password>")
        print("Ejemplo: python create_user.py admin@gym.local admin123")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    success = create_user(email, password)
    sys.exit(0 if success else 1)
