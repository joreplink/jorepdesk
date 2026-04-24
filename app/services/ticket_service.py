import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.ticket_agente import TicketAgente
from app.models.historial_estado import HistorialEstado
from app.models.usuario import Usuario
from app.repositories.ticket_repository import TicketRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.catalogo_repository import TipoServicioRepository, AreaRepository
from app.schemas.ticket import (
    TicketCreate, TicketAsignarRequest, TicketCambiarEstadoRequest,
    TicketOut, TicketDetail, AgenteSummary, HistorialEstadoOut, TRANSICIONES,
)
from app.schemas.usuario import UsuarioResumen
from app.schemas.catalogo import TipoServicioOut, AreaOut
from app.core.exceptions import (
    NotFoundException, BadRequestException,
    ForbiddenException, ConflictException,
)


def _ticket_to_out(ticket: Ticket) -> TicketOut:
    """Convierte un modelo Ticket a TicketOut manejando relaciones."""
    agentes = [
        AgenteSummary(
            id=a.agente.id,
            nombre=a.agente.nombre,
            apellido=a.agente.apellido,
            cargo=a.agente.cargo,
        )
        for a in ticket.asignaciones if a.activo
    ]
    return TicketOut(
        id=ticket.id,
        numero=ticket.numero,
        titulo=ticket.titulo,
        estado=ticket.estado,
        prioridad=ticket.prioridad,
        nombre_reportante=ticket.nombre_reportante,
        telefono_reportante=ticket.telefono_reportante,
        tipo_servicio=TipoServicioOut.model_validate(ticket.tipo_servicio),
        area=AreaOut.model_validate(ticket.area),
        creado_por=UsuarioResumen.model_validate(ticket.creado_por),
        creado_en=ticket.creado_en,
        actualizado_en=ticket.actualizado_en,
        cerrado_en=ticket.cerrado_en,
        agentes=agentes,
    )


def _ticket_to_detail(ticket: Ticket) -> TicketDetail:
    """Convierte un modelo Ticket a TicketDetail incluyendo historial."""
    base = _ticket_to_out(ticket)
    historial = [
        HistorialEstadoOut(
            id=h.id,
            estado_anterior=h.estado_anterior,
            estado_nuevo=h.estado_nuevo,
            cambiado_en=h.cambiado_en,
            cambiado_por=UsuarioResumen.model_validate(h.cambiado_por),
        )
        for h in ticket.historial_estados
    ]
    return TicketDetail(**base.model_dump(), historial_estados=historial)


class TicketService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = TicketRepository(db)
        self.usuario_repo = UsuarioRepository(db)
        self.tipo_repo = TipoServicioRepository(db)
        self.area_repo = AreaRepository(db)

    # ── Listados ──────────────────────────────────────────────────────────────

    def get_all(
        self,
        estado: str | None = None,
        prioridad: str | None = None,
        area_id: str | None = None,
        tipo_servicio_id: str | None = None,
    ) -> list[TicketOut]:
        tickets = self.repo.get_all(estado, prioridad, area_id, tipo_servicio_id)
        return [_ticket_to_out(t) for t in tickets]

    def get_by_id(self, ticket_id: str) -> TicketDetail:
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket")
        return _ticket_to_detail(ticket)

    def get_mis_tickets(self, agente_id: str) -> list[TicketOut]:
        tickets = self.repo.get_by_agente(agente_id)
        return [_ticket_to_out(t) for t in tickets]

    # ── Crear ─────────────────────────────────────────────────────────────────

    def crear(self, data: TicketCreate, admin_id: str) -> TicketDetail:
        # Valida que los catálogos existan y estén activos
        tipo = self.tipo_repo.get_by_id(data.tipo_servicio_id)
        if not tipo or not tipo.activo:
            raise NotFoundException("Tipo de servicio")

        area = self.area_repo.get_by_id(data.area_id)
        if not area or not area.activo:
            raise NotFoundException("Área")

        numero = self.repo.siguiente_numero()

        ticket = Ticket(
            id=str(uuid.uuid4()),
            numero=numero,
            titulo=data.titulo.strip(),
            descripcion=data.descripcion.strip(),
            estado="abierto",
            prioridad=data.prioridad,
            nombre_reportante=data.nombre_reportante.strip(),
            telefono_reportante=data.telefono_reportante,
            creado_por_id=admin_id,
            tipo_servicio_id=data.tipo_servicio_id,
            area_id=data.area_id,
        )
        ticket = self.repo.create(ticket)
        return _ticket_to_detail(ticket)

    # ── Asignación ────────────────────────────────────────────────────────────

    def asignar(
        self, ticket_id: str, data: TicketAsignarRequest, admin_id: str
    ) -> TicketDetail:
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket")

        if ticket.estado == "cerrado":
            raise BadRequestException(
                "No se puede asignar agentes a un ticket cerrado."
            )

        # Valida que todos los agente_ids existan y sean agentes activos
        for agente_id in data.agente_ids:
            agente = self.usuario_repo.get_by_id(agente_id)
            if not agente:
                raise NotFoundException(f"Agente {agente_id}")
            if agente.rol != "agente":
                raise BadRequestException(
                    f"El usuario {agente.email} no tiene rol de agente."
                )
            if not agente.activo:
                raise BadRequestException(
                    f"El agente {agente.email} está inactivo."
                )
            # Evita duplicar asignación activa
            existe = self.repo.get_asignacion_activa(ticket_id, agente_id)
            if existe:
                raise ConflictException(
                    f"El agente {agente.email} ya está asignado a este ticket."
                )

        # Crea las asignaciones
        for agente_id in data.agente_ids:
            asignacion = TicketAgente(
                id=str(uuid.uuid4()),
                ticket_id=ticket_id,
                agente_id=agente_id,
                asignado_por_id=admin_id,
                activo=True,
            )
            self.repo.add_asignacion(asignacion)

        return _ticket_to_detail(self.repo.get_by_id(ticket_id))

    def reasignar(
        self, ticket_id: str, data: TicketAsignarRequest, admin_id: str
    ) -> TicketDetail:
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket")

        if ticket.estado == "cerrado":
            raise BadRequestException(
                "No se puede reasignar un ticket cerrado."
            )

        # Valida nuevos agentes
        for agente_id in data.agente_ids:
            agente = self.usuario_repo.get_by_id(agente_id)
            if not agente:
                raise NotFoundException(f"Agente {agente_id}")
            if agente.rol != "agente":
                raise BadRequestException(
                    f"El usuario {agente.email} no tiene rol de agente."
                )
            if not agente.activo:
                raise BadRequestException(
                    f"El agente {agente.email} está inactivo."
                )

        # Desactiva asignaciones anteriores
        asignaciones_activas = self.repo.get_asignaciones_activas(ticket_id)
        for asig in asignaciones_activas:
            asig.activo = False
        self.db.flush()

        # Crea nuevas asignaciones
        for agente_id in data.agente_ids:
            asignacion = TicketAgente(
                id=str(uuid.uuid4()),
                ticket_id=ticket_id,
                agente_id=agente_id,
                asignado_por_id=admin_id,
                activo=True,
            )
            self.repo.add_asignacion(asignacion)

        return _ticket_to_detail(self.repo.get_by_id(ticket_id))

    # ── Cambiar estado ────────────────────────────────────────────────────────

    def cambiar_estado(
        self,
        ticket_id: str,
        data: TicketCambiarEstadoRequest,
        agente: Usuario,
    ) -> TicketDetail:
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket")

        # Verifica que el agente esté asignado activamente
        asignacion = self.repo.get_asignacion_activa(ticket_id, agente.id)
        if not asignacion:
            raise ForbiddenException(
                "No estás asignado a este ticket."
            )

        # Valida transición de estado
        transiciones_permitidas = TRANSICIONES.get(ticket.estado, [])
        if data.estado not in transiciones_permitidas:
            raise BadRequestException(
                f"No puedes cambiar de '{ticket.estado}' a '{data.estado}'. "
                f"Transiciones permitidas: {transiciones_permitidas or 'ninguna (ticket cerrado)'}."
            )

        # Registra historial
        historial = HistorialEstado(
            id=str(uuid.uuid4()),
            ticket_id=ticket_id,
            cambiado_por_id=agente.id,
            estado_anterior=ticket.estado,
            estado_nuevo=data.estado,
        )
        self.db.add(historial)

        # Actualiza estado
        ticket.estado = data.estado
        if data.estado == "cerrado":
            ticket.cerrado_en = datetime.now(timezone.utc)

        return _ticket_to_detail(self.repo.update(ticket))
