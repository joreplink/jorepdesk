from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import require_agente, require_admin_or_agente
from app.schemas.evidencia import EvidenciaOut
from app.services.evidencia_service import EvidenciaService

router = APIRouter()


@router.get(
    "/tickets/{ticket_id}/evidencias",
    response_model=list[EvidenciaOut],
    summary="Listar evidencias del ticket",
    description="Admin ve todas. Agente solo si está asignado al ticket.",
)
def listar_evidencias(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_agente),
):
    return EvidenciaService(db).get_by_ticket(ticket_id, current_user)


@router.post(
    "/tickets/{ticket_id}/evidencias",
    response_model=EvidenciaOut,
    status_code=201,
    summary="Subir evidencia al ticket",
    description=(
        "Solo agentes asignados al ticket. "
        "Formatos permitidos: JPG, PNG, GIF, WEBP, PDF. "
        "Tamaño máximo: 10 MB."
    ),
)
async def subir_evidencia(
    ticket_id: str,
    archivo: UploadFile = File(..., description="Archivo de evidencia"),
    db: Session = Depends(get_db),
    current_user=Depends(require_agente),
):
    return await EvidenciaService(db).subir(ticket_id, archivo, current_user)
