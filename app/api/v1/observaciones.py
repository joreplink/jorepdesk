from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import require_agente, require_admin_or_agente
from app.schemas.observacion import ObservacionCreate, ObservacionOut
from app.services.observacion_service import ObservacionService

router = APIRouter()


@router.get(
    "/tickets/{ticket_id}/observaciones",
    response_model=list[ObservacionOut],
    summary="Listar observaciones del ticket",
    description="Admin ve todas. Agente solo si está asignado al ticket.",
)
def listar_observaciones(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_agente),
):
    return ObservacionService(db).get_by_ticket(ticket_id, current_user)


@router.post(
    "/tickets/{ticket_id}/observaciones",
    response_model=ObservacionOut,
    status_code=201,
    summary="Agregar observación al ticket",
    description="Solo agentes asignados al ticket. No se puede agregar en tickets cerrados.",
)
def crear_observacion(
    ticket_id: str,
    data: ObservacionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_agente),
):
    return ObservacionService(db).crear(ticket_id, data, current_user)
