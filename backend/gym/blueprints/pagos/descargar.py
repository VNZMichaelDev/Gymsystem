from flask import Blueprint, send_from_directory, abort, jsonify, current_app
from flask_jwt_extended import jwt_required
from gym.models.Pago import Pago
from gym.extensions import db
import os
import mimetypes

descargar_comprobante_bp = Blueprint("descargar_comprobante", __name__)


def _resolve_comprobante_path(comprobante_rel, upload_folder):
    """Resuelve la ruta absoluta del comprobante probando varias ubicaciones.
    Devuelve la ruta absoluta si existe, o None si no se encuentra.
    """
    if not comprobante_rel:
        return None

    # 1) Si es ruta absoluta y existe
    if os.path.isabs(comprobante_rel) and os.path.exists(comprobante_rel):
        return os.path.abspath(comprobante_rel)

    # 2) Intentar como relativo a upload_folder
    candidate = os.path.join(upload_folder, comprobante_rel)
    if os.path.exists(candidate):
        return os.path.abspath(candidate)

    # 3) Intentar como relativo al cwd (la función save_upload guarda relativo a cwd)
    candidate2 = os.path.join(os.getcwd(), comprobante_rel)
    if os.path.exists(candidate2):
        return os.path.abspath(candidate2)

    # 4) Intentar usar solo el basename dentro de la carpeta 'comprobantes' del upload_folder
    base = os.path.basename(comprobante_rel)
    candidate3 = os.path.join(upload_folder, 'comprobantes', base)
    if os.path.exists(candidate3):
        return os.path.abspath(candidate3)

    return None

@descargar_comprobante_bp.get("/<int:id_pago>/comprobante")
@jwt_required()
def descargar_comprobante(id_pago):
    """
    Endpoint protegido para descargar comprobantes de pago
    Solo usuarios autenticados pueden acceder
    """
    try:
        # Buscar el pago
        pago = Pago.query.get(id_pago)
        if not pago:
            return jsonify({"error": "Pago no encontrado"}), 404
        
        # Verificar que tenga comprobante
        if not pago.comprobante:
            return jsonify({"error": "Este pago no tiene comprobante"}), 404
        
        # Construir ruta completa del archivo intentando varias resoluciones
        upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(os.getcwd(), 'gym', 'uploads'))
        abs_path = _resolve_comprobante_path(pago.comprobante, upload_folder)

        if not abs_path:
            return jsonify({"error": "Archivo de comprobante no encontrado"}), 404

        # Verificar que el archivo está dentro del directorio permitido (seguridad)
        upload_folder_abs = os.path.abspath(upload_folder)
        if not abs_path.startswith(upload_folder_abs):
            # Permitir rutas relativas almacenadas que resuelvan dentro del uploads
            if 'gym{}uploads'.format(os.sep) not in abs_path.replace('\\', os.sep):
                return jsonify({"error": "Acceso denegado"}), 403

        # Obtener directorio y nombre del archivo
        directory, filename = os.path.split(abs_path)
        
        # Determinar el tipo MIME
        mimetype, _ = mimetypes.guess_type(filename)
        if not mimetype:
            mimetype = 'application/octet-stream'
        
        # Servir el archivo
        return send_from_directory(
            directory, 
            filename, 
            as_attachment=False,  # False = mostrar en navegador, True = forzar descarga
            mimetype=mimetype
        )
        
    except Exception as e:
        return jsonify({"error": f"Error al descargar comprobante: {str(e)}"}), 500

@descargar_comprobante_bp.get("/<int:id_pago>/comprobante/download")
@jwt_required()
def forzar_descarga_comprobante(id_pago):
    """
    Fuerza la descarga del comprobante (no lo muestra en el navegador)
    """
    try:
        pago = Pago.query.get(id_pago)
        if not pago:
            return jsonify({"error": "Pago no encontrado"}), 404

        if not pago.comprobante:
            return jsonify({"error": "Este pago no tiene comprobante"}), 404

        upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(os.getcwd(), 'gym', 'uploads'))
        abs_path = _resolve_comprobante_path(pago.comprobante, upload_folder)

        if not abs_path:
            return jsonify({"error": "Archivo de comprobante no encontrado"}), 404

        upload_folder_abs = os.path.abspath(upload_folder)
        if not abs_path.startswith(upload_folder_abs):
            if 'gym{}uploads'.format(os.sep) not in abs_path.replace('\\', os.sep):
                return jsonify({"error": "Acceso denegado"}), 403

        directory, filename = os.path.split(abs_path)

        # Generar nombre de descarga más descriptivo
        base_name, ext = os.path.splitext(filename)
        download_name = f"comprobante_pago_{id_pago}_{pago.fecha_pago}{ext}"

        return send_from_directory(
            directory,
            filename,
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        return jsonify({"error": f"Error al descargar comprobante: {str(e)}"}), 500

@descargar_comprobante_bp.get("/<int:id_pago>/comprobante/info")
@jwt_required()
def info_comprobante(id_pago):
    """
    Obtiene información del comprobante sin descargarlo
    """
    try:
        pago = Pago.query.get(id_pago)
        if not pago:
            return jsonify({"error": "Pago no encontrado"}), 404
        
        if not pago.comprobante:
            return jsonify({
                "id_pago": id_pago,
                "tiene_comprobante": False,
                "mensaje": "Este pago no tiene comprobante"
            })
        
        upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(os.getcwd(), 'gym', 'uploads'))
        abs_path = _resolve_comprobante_path(pago.comprobante, upload_folder)

        file_exists = os.path.exists(abs_path) if abs_path else False
        file_size = os.path.getsize(abs_path) if file_exists else 0
        
        # Determinar tipo de archivo
        _, ext = os.path.splitext(pago.comprobante)
        file_type = "Imagen" if ext.lower() in ['.jpg', '.jpeg', '.png', '.gif'] else "Documento" if ext.lower() == '.pdf' else "Archivo"
        
        return jsonify({
            "id_pago": id_pago,
            "tiene_comprobante": True,
            "archivo": os.path.basename(pago.comprobante),
            "ruta_relativa": pago.comprobante,
            "tipo_archivo": file_type,
            "extension": ext,
            "existe": file_exists,
            "tamaño_bytes": file_size,
            "tamaño_mb": round(file_size / (1024*1024), 2) if file_size > 0 else 0,
            "fecha_pago": pago.fecha_pago,
            "url_visualizar": f"/api/pagos/{id_pago}/comprobante",
            "url_descargar": f"/api/pagos/{id_pago}/comprobante/download"
        })
        
    except Exception as e:
        return jsonify({"error": f"Error al obtener información: {str(e)}"}), 500

@descargar_comprobante_bp.delete("/<int:id_pago>/comprobante")
@jwt_required()
def eliminar_comprobante(id_pago):
    """
    Elimina el comprobante de un pago (solo el archivo, mantiene el registro del pago)
    """
    try:
        pago = Pago.query.get(id_pago)
        if not pago:
            return jsonify({"error": "Pago no encontrado"}), 404

        if not pago.comprobante:
            return jsonify({"error": "Este pago no tiene comprobante"}), 404

        upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(os.getcwd(), 'gym', 'uploads'))
        abs_path = _resolve_comprobante_path(pago.comprobante, upload_folder)

        # Eliminar archivo físico si existe
        if abs_path and os.path.exists(abs_path):
            upload_folder_abs = os.path.abspath(upload_folder)
            if abs_path.startswith(upload_folder_abs):
                os.remove(abs_path)

        # Limpiar referencia en la base de datos
        pago.comprobante = None
        db.session.commit()

        return jsonify({
            "message": "Comprobante eliminado exitosamente",
            "pago": pago.to_dict()
        })

    except Exception as e:
        return jsonify({"error": f"Error al obtener información: {str(e)}"}), 500