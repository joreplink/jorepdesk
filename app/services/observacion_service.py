import uuid
from sqlalchemy.orm import Session

from app.models.observacion import Observacion
from app.models.usuario import Usuario
from app.repositories.observacion_repository import ObservacionRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.observacion import ObservacionCreate, ObservacionOut
from app.schemas.usuario import UsuarioResumen
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException


class ObservacionService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = ObservacionRepository(db)
        self.ticket_repo = TicketRepository(db)

    def get_by_ticket(self, ticket_id: str, current_user: Usuario) -> list[ObservacionOut]:
        # Verifica que el ticket exista
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket")

        # Si es agente, verifica que esté asignado
        if current_user.rol == "agente":
            asignacion = self.ticket_repo.get_asignacion_activa(ticket_id, current_user.id)
            if not asignacion:
                raise ForbiddenException("No estás asignado a este ticket.")

        observaciones = self.repo.get_by_ticket(ticket_id)
        return [
            ObservacionOut(
                id=o.id,
                contenido=o.contenido,
                creado_en=o.creado_en,
                agente=UsuarioResumen.model_validate(o.agente),
            )
            for o in observaciones
        ]

    def crear(
        self, ticket_id: str, data: ObservacionCreate, agente: Usuario
    ) -> ObservacionOut:
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket")

        if ticket.estado == "cerrado":
            raise BadRequestException(
                "No se pueden agregar observaciones a un ticket cerrado."
            )

        # Verifica que el agente esté asignado activamente
        asignacion = self.ticket_repo.get_asignacion_activa(ticket_id, agente.id)
        if not asignacion:
            raise ForbiddenException("No estás asignado a este ticket.")

        observacion = Observacion(
            id=str(uuid.uuid4()),
            ticket_id=ticket_id,
            agente_id=agente.id,
            contenido=data.contenido.strip(),
        )
        observacion = self.repo.create(observacion)
        return ObservacionOut(
            id=observacion.id,
            contenido=observacion.contenido,
            creado_en=observacion.creado_en,
            agente=UsuarioResumen.model_validate(observacion.agente),
        )
