import uuid
import os
from werkzeug.utils import secure_filename
from flask import current_app

def save_upload(file, upload_type="comprobantes"):
    """
    Guarda un archivo subido de forma segura
    Args:
        file: Objeto de archivo de Flask
        upload_type: Tipo de upload ('comprobantes', 'fotos', etc.)
    Returns:
        str: Ruta relativa del archivo guardado
    """
    if not file or not file.filename:
        raise ValueError("No se proporcionó archivo válido")
    
    # Validar extensión
    allowed_extensions = {
        'comprobantes': {'pdf', 'jpg', 'jpeg', 'png'},
        'fotos': {'jpg', 'jpeg', 'png'}
    }
    
    if '.' not in file.filename:
        raise ValueError("Archivo sin extensión")
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions.get(upload_type, set()):
        raise ValueError(f"Extensión {ext} no permitida para {upload_type}")
    
    # Generar nombre único
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Crear directorio si no existe
    rel_dir = f"gym/uploads/{upload_type}"
    abs_dir = os.path.join(os.getcwd(), rel_dir)
    os.makedirs(abs_dir, exist_ok=True)
    
    # Ruta completa del archivo
    file_path = os.path.join(rel_dir, secure_filename(unique_filename))
    abs_path = os.path.join(os.getcwd(), file_path)
    
    # Guardar archivo
    file.save(abs_path)
    
    # Retornar ruta relativa para guardar en BD
    return file_path

def validate_file_size(file, max_size_mb=5):
    """
    Valida el tamaño del archivo
    Args:
        file: Objeto de archivo
        max_size_mb: Tamaño máximo en MB
    """
    if file:
        # Ir al final del archivo para obtener el tamaño
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)  # Volver al inicio
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if size > max_size_bytes:
            raise ValueError(f"Archivo muy grande. Máximo permitido: {max_size_mb}MB")
    
    return True