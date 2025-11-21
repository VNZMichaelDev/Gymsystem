from gym.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import CheckConstraint

class Pago(db.Model):
    __tablename__ = "Pagos"
    id_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("Clientes.id_cliente"), nullable=False, index=True)
    id_membresia = db.Column(db.Integer, db.ForeignKey("Membresias.id_membresia"), nullable=False)
    fecha_pago = db.Column(db.String(32), nullable=False, default=lambda: datetime.now().strftime("%Y-%m-%d"))
    fecha_inicio_membresia = db.Column(db.String(32), nullable=False)
    fecha_fin_membresia = db.Column(db.String(32), nullable=False)
    monto_total = db.Column(db.Float, nullable=False)  # Precio total de la membresía
    monto_pagado = db.Column(db.Float, nullable=False)  # Monto que pagó en esta transacción
    monto_pendiente = db.Column(db.Float, nullable=False, default=0.0)  # Lo que aún debe
    comprobante = db.Column(db.String(255), nullable=True)  # Ruta del archivo de imagen
    estado = db.Column(db.String(20), nullable=False, default="Pendiente")  # Pendiente, Pagado, Vencido
    
    # Constraints
    __table_args__ = (
        CheckConstraint("monto_total > 0", name='check_monto_total_positive'),
        CheckConstraint("monto_pagado > 0", name='check_monto_pagado_positive'),
        CheckConstraint("monto_pendiente >= 0", name='check_monto_pendiente_positive'),
        CheckConstraint("estado IN ('Pendiente', 'Pagado', 'Vencido')", name='check_estado_valid'),
    )

    def __repr__(self):
        return f"<Pago {self.id_pago} - Cliente {self.id_cliente}>"

    def to_dict(self):
        """Devuelve una representación del objeto en formato diccionario."""
        from gym.models.Cliente import Cliente
        from gym.models.Membresia import Membresia

        # Prepara el diccionario base
        result = {
            "id_pago": self.id_pago,
            "id_cliente": self.id_cliente,
            "id_membresia": self.id_membresia,
            "fecha_pago": self.fecha_pago,
            "fecha_inicio_membresia": self.fecha_inicio_membresia,
            "fecha_fin_membresia": self.fecha_fin_membresia,
            "monto_total": self.monto_total,
            "monto_pagado": self.monto_pagado,
            "monto_pendiente": self.monto_pendiente,
            "comprobante": self.comprobante,
            "estado": self.estado
        }

        # Incluir información del cliente
        cliente = Cliente.query.get(self.id_cliente)
        if cliente:
            result["cliente_nombre"] = cliente.nombre_completo
            result["cliente_documento"] = cliente.numero_documento
        
        # Incluir información de la membresía
        if self.id_membresia:
            membresia = Membresia.query.get(self.id_membresia)
            if membresia:
                result["membresia_nombre"] = membresia.nombre

        return result
    
    @staticmethod
    def calcular_fechas_membresia(duracion_dias, fecha_inicio=None):
        """Calcula las fechas de inicio y fin de una membresía."""
        if fecha_inicio is None:
            fecha_inicio = datetime.now()
        elif isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            
        fecha_fin = fecha_inicio + timedelta(days=duracion_dias)
        
        return {
            "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
            "fecha_fin": fecha_fin.strftime("%Y-%m-%d")
        }