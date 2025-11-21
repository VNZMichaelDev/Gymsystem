import sqlite3

# Ruta del archivo SQL (asegúrate de que la ruta sea correcta)
sql_file = './bd/db_getfit.sql'  # Ruta al archivo SQL

# Conectar a la base de datos SQLite
conn = sqlite3.connect('./bd/base_Datos.db')  # Si la base de datos no existe, SQLite la creará automáticamente
cursor = conn.cursor()

# Leer el archivo SQL
with open(sql_file, 'r') as f:
    sql_script = f.read()

# Ejecutar el script SQL
try:
    cursor.executescript(sql_script)  # Ejecuta el script completo
    conn.commit()
    print("Base de datos creada con éxito")
except Exception as e:
    print(f"Error al ejecutar el script SQL: {e}")
finally:
    conn.close()
