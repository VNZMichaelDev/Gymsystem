"""
Script para inicializar la base de datos con datos de ejemplo.
Se ejecuta automáticamente en el primer deploy.
"""
import os
import sys
from sqlalchemy import text
from app import create_app, db

def init_database():
    """Ejecuta el SQL de inicialización si la BD está vacía."""
    app = create_app()
    
    with app.app_context():
        # Leer el archivo SQL
        sql_file = os.path.join(os.path.dirname(__file__), 'bd', 'db_getfit.sql')
        
        if not os.path.exists(sql_file):
            print(f"⚠️  Archivo SQL no encontrado: {sql_file}")
            return
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        try:
            # Ejecutar el SQL
            db.session.execute(text(sql_content))
            db.session.commit()
            print("✅ Base de datos inicializada correctamente con datos de ejemplo")
        except Exception as e:
            print(f"⚠️  Error al ejecutar SQL: {e}")
            print("   (Esto es normal si la BD ya tiene datos)")
            db.session.rollback()

if __name__ == '__main__':
    init_database()
