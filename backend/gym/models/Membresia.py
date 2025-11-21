# archivo: gym/models/Membresia.py

from gym.extensions import db

class Membresia(db.Model):
    __tablename__ = "Membresias"
    
    # --- COLUMNAS ---
    id_membresia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    duracion_dias = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    
    # --- RELACIONES ---
    # CORRECCIÓN: Relación bidireccional explícita con el modelo Cliente.
    # Esto se sincroniza con la propiedad 'membresia' en la clase Cliente.
    clientes = db.relationship('Cliente', back_populates='membresia')

    def __repr__(self):
        return f"<Membresia {self.id_membresia} - {self.nombre}>"
    
    def to_dict(self):
        """Serializa el objeto Membresia a un diccionario."""
        return {
            'id_membresia': self.id_membresia,
            'nombre': self.nombre,
            'duracion_dias': self.duracion_dias,
            'precio': self.precio
        } # <-- CORRECCIÓN: Se eliminó el signo '+' extra de aquí.