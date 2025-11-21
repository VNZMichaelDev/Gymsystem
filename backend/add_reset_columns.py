import sqlite3

def add_reset_columns():
    # Conectar a tu base de datos
    conn = sqlite3.connect('bd/base_Datos.db')  # Ajusta la ruta según tu DB
    cursor = conn.cursor()
    
    try:
        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(Usuarios);")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        
        print("Columnas existentes:", existing_columns)
        
        # Agregar columnas para reset de contraseña si no existen
        if 'reset_token' not in existing_columns:
            cursor.execute("ALTER TABLE Usuarios ADD COLUMN reset_token TEXT;")
            print("✓ Columna reset_token agregada")
        
        if 'reset_token_expires' not in existing_columns:
            cursor.execute("ALTER TABLE Usuarios ADD COLUMN reset_token_expires TEXT;")
            print("✓ Columna reset_token_expires agregada")
        
        conn.commit()
        print("✓ Tabla actualizada exitosamente")
        
        # Mostrar estructura final
        cursor.execute("PRAGMA table_info(Usuarios);")
        columns = cursor.fetchall()
        print("\nEstructura final de la tabla:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_reset_columns()