# Importa todos los modelos para que SQLAlchemy y Alembic
# los registren en Base.metadata automáticamente.
# El orden importa: tablas sin FK primero.

from app.models.usuario import Usuario
from app.models.tipo_servicio import TipoServicio
from app.models.area import Area
from app.models.ticket import Ticket
from app.models.ticket_agente import TicketAgente
from app.models.observacion import Observacion
from app.models.evidencia import Evidencia
from app.models.historial_estado import HistorialEstado
from app.models.reporte import Reporte

__all__ = [
    "Usuario",
    "TipoServicio",
    "Area",
    "Ticket",
    "TicketAgente",
    "Observacion",
    "Evidencia",
    "HistorialEstado",
    "Reporte",
]
