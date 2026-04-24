from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import require_admin, require_agente, require_admin_or_agente
from app.schemas.ticket import (
    TicketCreate, TicketAsignarRequest, TicketCambiarEstadoRequest,
    TicketOut, TicketDetail,
)
from app.services.ticket_service import TicketService

router = APIRouter()


@router.get(
    "/tickets",
    response_model=list[TicketOut],
    summary="Listar todos los tickets",
    description="Solo administradores. Permite filtrar por estado, prioridad, área y tipo de servicio.",
)
def listar_tickets(
    estado: str | None = Query(None, description="abierto | en_proceso | cerrado"),
    prioridad: str | None = Query(None, description="baja | media | alta | critica"),
    area_id: str | None = Query(None),
    tipo_servicio_id: str | None = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return TicketService(db).get_all(estado, prioridad, area_id, tipo_servicio_id)


@router.get(
    "/tickets/mis-tickets",
    response_model=list[TicketOut],
    summary="Ver mis tickets asignados",
    description="Solo agentes. Retorna los tickets activamente asignados al agente autenticado.",
)
def mis_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(require_agente),
):
    return TicketService(db).get_mis_tickets(current_user.id)


@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketDetail,
    summary="Obtener ticket por ID",
    description="Accesible por admin y agente. Incluye historial de estados.",
)
def obtener_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_agente),
):
    return TicketService(db).get_by_id(ticket_id)


@router.post(
    "/tickets",
    response_model=TicketDetail,
    status_code=201,
    summary="Crear ticket",
    description="Solo administradores.",
)
def crear_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return TicketService(db).crear(data, current_user.id)


@router.post(
    "/tickets/{ticket_id}/asignar",
    response_model=TicketDetail,
    summary="Asignar agentes al ticket",
    description="Solo administradores. Asigna uno o más agentes al ticket.",
)
def asignar_ticket(
    ticket_id: str,
    data: TicketAsignarRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return TicketService(db).asignar(ticket_id, data, current_user.id)


@router.post(
    "/tickets/{ticket_id}/reasignar",
    response_model=TicketDetail,
    summary="Reasignar agentes al ticket",
    description="Solo administradores. Desactiva asignaciones anteriores y crea nuevas.",
)
def reasignar_ticket(
    ticket_id: str,
    data: TicketAsignarRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return TicketService(db).reasignar(ticket_id, data, current_user.id)


@router.patch(
    "/tickets/{ticket_id}/estado",
    response_model=TicketDetail,
    summary="Cambiar estado del ticket",
    description=(
        "Solo agentes asignados al ticket. "
        "Transiciones válidas: abierto → en_proceso → cerrado."
    ),
)
def cambiar_estado(
    ticket_id: str,
    data: TicketCambiarEstadoRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_agente),
):
    return TicketService(db).cambiar_estado(ticket_id, data, current_user)
