from gym.extensions import db
from datetime import datetime

class Asistencia(db.Model):
    __tablename__ = "Asistencia"  # Corregido: sin "s" al final
    id_asistencia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("Clientes.id_cliente"), nullable=False, index=True)
    fecha = db.Column(db.String(32), nullable=False, default=lambda: datetime.now().strftime("%Y-%m-%d"))  # Fecha modificable solo al crear
    hora_entrada = db.Column(db.String(8), nullable=False, default=lambda: datetime.now().strftime("%H:%M"))
    hora_salida = db.Column(db.String(8), nullable=True)

    # Comentado para evitar imports circulares
    # cliente = db.relationship("Cliente", backref="asistencias")

    def __repr__(self):
        return f"<Asistencia {self.id_asistencia} - Cliente {self.id_cliente}>"
    
    def actualizar_fecha(self, nueva_fecha):
        """Método para actualizar la fecha de asistencia"""
        self.fecha = nueva_fecha
    
    def marcar_salida(self, hora_salida=None):
        """Método para marcar la hora de salida"""
        if hora_salida is None:
            hora_salida = datetime.now().strftime("%H:%M")
        self.hora_salida = hora_salida

    def to_dict(self):
        return {
            "id_asistencia": self.id_asistencia,
            "id_cliente": self.id_cliente,
            "fecha": self.fecha,
            "hora_entrada": self.hora_entrada,
            "hora_salida": self.hora_salida
        }
