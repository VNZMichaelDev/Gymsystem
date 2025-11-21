"""
Script para polar la base de datos con datos iniciales
Ejecutar: python seed_data.py
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from gym.extensions import db
from gym.models.Usuario import Usuario
from gym.models.Membresia import Membresia
from gym.models.Cliente import Cliente
from gym.models.Pago import Pago
from gym.models.Asistencia import Asistencia
from datetime import datetime, timedelta
import random
app = create_app()

def create_admin_user():
    """Crea un usuario administrador si no existe."""
    with app.app_context():
        # Check if admin user exists
        admin = Usuario.query.filter_by(email="admin@gym.com").first()
        if not admin:
            print("👤 Creando usuario administrador...")
            admin = Usuario(
                nombre_usuario="admin",
                email="admin@gym.com",
                rol="admin",
                nombre_completo="Administrador del Sistema"
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario administrador creado con éxito.")
        else:
            print("ℹ️  El usuario administrador ya existe.")

def create_memberships():
    """Crear membresías base"""
    memberships_data = [
        {"nombre": "Básica", "duracion_dias": 30, "precio": 50.0},
        {"nombre": "Premium", "duracion_dias": 30, "precio": 80.0},
        {"nombre": "VIP", "duracion_dias": 30, "precio": 120.0},
        {"nombre": "Anual Básica", "duracion_dias": 365, "precio": 500.0},
        {"nombre": "Anual Premium", "duracion_dias": 365, "precio": 800.0}
    ]
    
    for mem_data in memberships_data:
        existing = Membresia.query.filter_by(nombre=mem_data["nombre"]).first()
        if not existing:
            membresia = Membresia(**mem_data)
            db.session.add(membresia)
            print(f"✅ Membresía '{mem_data['nombre']}' creada")
        else:
            print(f"ℹ️  Membresía '{mem_data['nombre']}' ya existe")

def create_sample_clients():
    """Crear clientes de ejemplo"""
    if Cliente.query.count() >= 10:
        print("ℹ️  Ya existen suficientes clientes de ejemplo")
        return
    
    memberships = Membresia.query.all()
    if not memberships:
        print("❌ No hay membresías disponibles. Crear primero las membresías.")
        return
    
    clients_data = [
        {"nombre": "Juan", "apellido_paterno": "Pérez", "apellido_materno": "González", "tipo_documento": "DNI", "numero_documento": "12345678", "correo": "juan.perez@email.com", "telefono": "987654321"},
        {"nombre": "María", "apellido_paterno": "García", "apellido_materno": "López", "tipo_documento": "DNI", "numero_documento": "87654321", "correo": "maria.garcia@email.com", "telefono": "123456789"},
        {"nombre": "Carlos", "apellido_paterno": "Rodríguez", "apellido_materno": "Martín", "tipo_documento": "CE", "numero_documento": "CE123456", "correo": "carlos.rodriguez@email.com", "telefono": "456789123"},
        {"nombre": "Ana", "apellido_paterno": "Fernández", "apellido_materno": "Ruiz", "tipo_documento": "DNI", "numero_documento": "11223344", "correo": "ana.fernandez@email.com", "telefono": "789123456"},
        {"nombre": "Luis", "apellido_paterno": "Martínez", "apellido_materno": "Silva", "tipo_documento": "DNI", "numero_documento": "44332211", "correo": "luis.martinez@email.com", "telefono": "321654987"}
    ]
    
    for client_data in clients_data:
        existing = Cliente.query.filter_by(numero_documento=client_data["numero_documento"]).first()
        if not existing:
            # Asignar membresía aleatoria
            client_data["id_membresia"] = random.choice(memberships).id_membresia
            cliente = Cliente(**client_data)
            db.session.add(cliente)
            print(f"✅ Cliente '{client_data['nombre']} {client_data['apellido_paterno']}' creado")

def create_sample_payments():
    """Crear pagos de ejemplo"""
    clientes = Cliente.query.all()
    if not clientes:
        print("❌ No hay clientes disponibles")
        return
    
    if Pago.query.count() >= 5:
        print("ℹ️  Ya existen suficientes pagos de ejemplo")
        return
    
    for cliente in clientes[:3]:  # Solo los primeros 3 clientes
        pago = Pago(
            id_cliente=cliente.id_cliente,
            id_membresia=cliente.id_membresia,  # Añadir esta línea
            monto_pagado=random.uniform(50, 120),
            comprobante="Sin comprobante",
            estado=random.choice(["Pendiente", "Confirmado"])
        )
        db.session.add(pago)
        print(f"✅ Pago para cliente {cliente.nombre} creado")

def create_sample_attendance():
    """Crear asistencias de ejemplo"""
    clientes = Cliente.query.all()
    if not clientes:
        print("❌ No hay clientes disponibles")
        return
    
    if Asistencia.query.count() >= 10:
        print("ℹ️  Ya existen suficientes asistencias de ejemplo")
        return
    
    # Crear asistencias para los últimos 7 días
    for i in range(7):
        fecha = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        # 2-4 asistencias por día
        num_asistencias = random.randint(2, 4)
        
        for _ in range(num_asistencias):
            cliente = random.choice(clientes)
            hora_entrada = f"{random.randint(6, 21):02d}:{random.randint(0, 59):02d}"
            
            asistencia = Asistencia(
                id_cliente=cliente.id_cliente,
                fecha=fecha,
                hora_entrada=hora_entrada
            )
            db.session.add(asistencia)
        
        print(f"✅ {num_asistencias} asistencias creadas para {fecha}")

def main():
    """Función principal para ejecutar todos los seeds"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Iniciando seed de datos...")
        
        try:
            # Crear tablas si no existen
            db.create_all()
            print("✅ Tablas de base de datos verificadas")
            
            # Ejecutar seeds en orden
            create_admin_user()
            create_memberships()
            create_sample_clients()
            create_sample_payments()
            create_sample_attendance()
            
            # Confirmar cambios
            db.session.commit()
            print("\n🎉 Seed completado exitosamente!")
            print("\n📊 Resumen:")
            print(f"   - Usuarios: {Usuario.query.count()}")
            print(f"   - Membresías: {Membresia.query.count()}")
            print(f"   - Clientes: {Cliente.query.count()}")
            print(f"   - Pagos: {Pago.query.count()}")
            print(f"   - Asistencias: {Asistencia.query.count()}")
            print("\n🔑 Credenciales de acceso:")
            print("   Correo: admin@gym.com")
            print("   Password: admin123")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error durante el seed: {str(e)}")
            raise

if __name__ == "__main__":
    main()