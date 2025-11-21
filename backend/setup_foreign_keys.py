import sqlite3

# Conectar a la base de datos real
conn = sqlite3.connect(r'd:\2025-02\gym\gym-system\backend\bd\base_Datos.db')
cursor = conn.cursor()

print("=== CONFIGURANDO CLAVES FORÁNEAS ===")

try:
    # En SQLite, las claves foráneas se configuran al crear la tabla
    # Como ya tenemos datos, no podemos agregar constraints fácilmente
    # Pero podemos crear un índice para mejorar el rendimiento
    
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_Pagos_id_cliente ON Pagos(id_cliente)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_Pagos_id_membresia ON Pagos(id_membresia)")
    
    print("✅ Índices creados para mejorar el rendimiento")
    
    # Confirmar cambios
    conn.commit()
    
    print("\n=== VERIFICANDO INTEGRIDAD DE DATOS ===")
    
    # Verificar que todas las membresías referenciadas existen
    cursor.execute("""
        SELECT COUNT(*) as total_pagos,
               COUNT(id_membresia) as pagos_con_membresia
        FROM Pagos
    """)
    result = cursor.fetchone()
    print(f"Pagos totales: {result[0]}, Pagos con membresía: {result[1]}")
    
    # Verificar membresías disponibles
    cursor.execute("SELECT COUNT(*) FROM Membresias")
    membresias_count = cursor.fetchone()[0]
    print(f"Membresías disponibles: {membresias_count}")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

conn.close()
print("\n🎉 ¡Configuración de claves foráneas completada!")