# Reportes blueprint
from .asistencias_por_cliente import asistencias_por_cliente_bp
from .asistencias_por_periodo import asistencias_por_periodo_bp
from .clientes_nuevos_por_mes import clientes_nuevos_por_mes_bp
from .ingresos_por_membresia import ingresos_por_membresia_bp
from .membresias_activas import membresias_activas_bp
from .pagos_pendientes import pagos_pendientes_bp
from .pagos_por_mes import pagos_por_mes_bp
from .retencion_clientes import retencion_clientes_bp
from .rentabilidad_clientes import rentabilidad_clientes_bp
from .horarios_pico import horarios_pico_bp
from .dashboard_ejecutivo import dashboard_ejecutivo_bp
from .membresias_por_vencer import membresias_por_vencer_bp
from .clientes_resumen import clientes_resumen_bp
from .pagos_resumen import pagos_resumen_bp
from .membresias_resumen import membresias_resumen_bp
from .asistencias_resumen import asistencias_resumen_bp

__all__ = [
    'asistencias_por_cliente_bp',
    'asistencias_por_periodo_bp',
    'clientes_nuevos_por_mes_bp', 
    'ingresos_por_membresia_bp',
    'membresias_activas_bp',
    'pagos_pendientes_bp',
    'pagos_por_mes_bp',
    'retencion_clientes_bp',
    'rentabilidad_clientes_bp',
    'horarios_pico_bp',
    'dashboard_ejecutivo_bp'
    , 'membresias_por_vencer_bp'
    , 'clientes_resumen_bp'
    , 'pagos_resumen_bp'
    , 'membresias_resumen_bp'
    , 'asistencias_resumen_bp'
]