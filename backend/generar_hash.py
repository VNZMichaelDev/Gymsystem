# generar_hash.py
from werkzeug.security import generate_password_hash

# Escribe aquí la contraseña que quieres usar para tu usuario admin
contrasena_en_texto_plano = "admin123"

# Generamos el hash
hash_generado = generate_password_hash(contrasena_en_texto_plano)

print("\nCopia este hash y pégalo en tu base de datos:")
print("==============================================")
print(hash_generado)
print("==============================================\n")