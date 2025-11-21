# archivo: gym/models/Cliente.py

from gym.extensions import db
from datetime import datetime
from sqlalchemy import CheckConstraint
# Se importa el modelo Membresia para que la relación funcione correctamente
from gym.models.Membresia import Membresia

class Cliente(db.Model):
    __tablename__ = "Clientes"
    
    # --- COLUMNAS ---
    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_documento = db.Column(db.String(10), nullable=False)
    numero_documento = db.Column(db.String(32), nullable=False, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido_paterno = db.Column(db.String(100), nullable=False)
    apellido_materno = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(255))
    telefono = db.Column(db.String(50))
    fecha_registro = db.Column(db.String(32), nullable=False, default=lambda: datetime.now().strftime("%Y-%m-%d"))
    id_membresia = db.Column(db.Integer, db.ForeignKey("Membresias.id_membresia"))

    # --- CONSTRAINTS ---
    __table_args__ = (
        CheckConstraint("tipo_documento IN ('DNI', 'CE', 'RUC')", name='check_tipo_documento'),
        CheckConstraint("length(trim(nombre)) > 0", name='check_nombre_not_empty'),
        CheckConstraint("length(trim(apellido_paterno)) > 0", name='check_apellido_paterno_not_empty'),
    )

    # --- RELACIONES ---
    # CORRECCIÓN: Usamos back_populates para una relación bidireccional explícita sin conflictos.
    membresia = db.relationship('Membresia', back_populates='clientes')
    
    # Estas relaciones usan backref, lo cual está bien si los modelos Pago y Asistencia no definen la relación inversa.
    pagos = db.relationship('Pago', backref='cliente', lazy=True)
    asistencias = db.relationship('Asistencia', backref='cliente', lazy=True)

    def __repr__(self):
        return f"<Cliente {self.id_cliente} - {self.nombre} {self.apellido_paterno}>"

    @property
    def nombre_completo(self):
        """Propiedad que devuelve el nombre completo del cliente."""
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}".strip()

    def to_dict(self, include_membresia=True):
        """
        Serializa el objeto Cliente a un diccionario.
        Es eficiente porque usa la relación 'membresia' ya cargada.
        """
        result = {
            "id_cliente": self.id_cliente,
            "tipo_documento": self.tipo_documento,
            "numero_documento": self.numero_documento,
            "nombre": self.nombre,
            "apellido_paterno": self.apellido_paterno,
            "apellido_materno": self.apellido_materno,
            "nombre_completo": self.nombre_completo,
            "correo": self.correo,
            "telefono": self.telefono,
            "fecha_registro": self.fecha_registro,
            "id_membresia": self.id_membresia
        }
        
        # CORRECCIÓN: Usa la relación en lugar de hacer una nueva consulta a la BD.
        if include_membresia and self.membresia:
            result["nombre_membresia"] = self.membresia.nombre
            result["membresia"] = self.membresia.to_dict()
        else:
            result["nombre_membresia"] = None
            result["membresia"] = None
            
        return result
    
    # --- MÉTODOS ESTÁTICOS DE VALIDACIÓN ---
    @staticmethod
    def validate_tipo_documento(tipo):
        """Valida que el tipo de documento sea válido."""
        valid_types = ["DNI", "CE", "RUC"]
        return tipo in valid_types
    
    @staticmethod
    def validate_numero_documento(tipo, numero):
        """Valida el formato del número de documento según el tipo."""
        if not numero or not numero.strip():
            return False, "Número de documento requerido"
        
        numero = numero.strip()
        
        if tipo == "DNI" and (not numero.isdigit() or len(numero) != 8):
            return False, "DNI debe tener exactamente 8 dígitos"
        elif tipo == "CE" and (len(numero) < 4 or len(numero) > 12):
            return False, "CE debe tener entre 4 y 12 caracteres"
        elif tipo == "RUC" and (not numero.isdigit() or len(numero) != 11):
            return False, "RUC debe tener exactamente 11 dígitos"
        
        return True, "Válido"