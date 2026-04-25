from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models.ticket import Ticket
from app.models.ticket_agente import TicketAgente
from app.models.historial_estado import HistorialEstado
from app.models.usuario import Usuario


class TicketRepository:

    def __init__(self, db: Session):
        self.db = db

    def _base_query(self):
        """Query base con todos los joins necesarios para evitar N+1."""
        return (
            self.db.query(Ticket)
            .options(
                joinedload(Ticket.creado_por),
                joinedload(Ticket.tipo_servicio),
                joinedload(Ticket.area),
                joinedload(Ticket.asignaciones).joinedload(TicketAgente.agente),
                joinedload(Ticket.historial_estados).joinedload(
                    HistorialEstado.cambiado_por
                ),
            )
        )

    def get_by_id(self, ticket_id: str) -> Ticket | None:
        return self._base_query().filter(Ticket.id == ticket_id).first()

    def get_all(
        self,
        estado: str | None = None,
        prioridad: str | None = None,
        area_id: str | None = None,
        tipo_servicio_id: str | None = None,
    ) -> list[Ticket]:
        query = self._base_query()
        if estado:
            query = query.filter(Ticket.estado == estado)
        if prioridad:
            query = query.filter(Ticket.prioridad == prioridad)
        if area_id:
            query = query.filter(Ticket.area_id == area_id)
        if tipo_servicio_id:
            query = query.filter(Ticket.tipo_servicio_id == tipo_servicio_id)
        return query.order_by(Ticket.creado_en.desc()).all()

    def get_by_agente(self, agente_id: str) -> list[Ticket]:
        """Retorna tickets con asignacion activa para un agente."""
        return (
            self._base_query()
            .join(TicketAgente, and_(
                TicketAgente.ticket_id == Ticket.id,
                TicketAgente.agente_id == agente_id,
                TicketAgente.activo == True,
            ))
            .order_by(Ticket.creado_en.desc())
            .all()
        )

    def get_asignacion_activa(self, ticket_id: str, agente_id: str) -> TicketAgente | None:
        return (
            self.db.query(TicketAgente)
            .filter(
                TicketAgente.ticket_id == ticket_id,
                TicketAgente.agente_id == agente_id,
                TicketAgente.activo == True,
            )
            .first()
        )

    def get_asignaciones_activas(self, ticket_id: str) -> list[TicketAgente]:
        return (
            self.db.query(TicketAgente)
            .filter(
                TicketAgente.ticket_id == ticket_id,
                TicketAgente.activo == True,
            )
            .all()
        )

    def create(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.flush()
        self.db.refresh(ticket)
        return self.get_by_id(ticket.id)

    def update(self, ticket: Ticket) -> Ticket:
        self.db.flush()
        return self.get_by_id(ticket.id)

    def add_asignacion(self, asignacion: TicketAgente) -> TicketAgente:
        self.db.add(asignacion)
        self.db.flush()
        self.db.refresh(asignacion)
        return asignacion

    def siguiente_numero(self) -> str:
        """Genera el siguiente numero correlativo TKT-00001."""
        from sqlalchemy import func
        result = self.db.query(func.max(Ticket.numero)).scalar()
        if not result:
            return "TKT-00001"
        try:
            n = int(result.split("-")[1]) + 1
        except (IndexError, ValueError):
            n = 1
        return f"TKT-{n:05d}"
