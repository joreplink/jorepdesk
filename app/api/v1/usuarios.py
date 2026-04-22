from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import require_admin, get_current_user
from app.schemas.usuario import (
    UsuarioCreate, UsuarioUpdate, UsuarioOut, CambiarPasswordRequest,
)
from app.services.usuario_service import UsuarioService

router = APIRouter()


@router.get(
    "/usuarios",
    response_model=list[UsuarioOut],
    summary="Listar usuarios",
)
def listar_usuarios(
    rol: str | None = Query(None, description="Filtrar por rol: admin | agente"),
    solo_activos: bool = Query(False, description="Si es true, retorna solo activos"),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return UsuarioService(db).get_all(rol=rol, solo_activos=solo_activos)


@router.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioOut,
    summary="Obtener usuario por ID",
)
def obtener_usuario(
    usuario_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return UsuarioService(db).get_by_id(usuario_id)


@router.post(
    "/usuarios",
    response_model=UsuarioOut,
    status_code=201,
    summary="Crear usuario",
    description="Crea un nuevo usuario con rol admin o agente.",
)
def crear_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return UsuarioService(db).create(data)


@router.put(
    "/usuarios/{usuario_id}",
    response_model=UsuarioOut,
    summary="Actualizar usuario",
)
def actualizar_usuario(
    usuario_id: str,
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return UsuarioService(db).update(usuario_id, data)


@router.patch(
    "/usuarios/{usuario_id}/password",
    summary="Cambiar contraseña",
    description="Solo el propio usuario puede cambiar su contraseña.",
)
def cambiar_password(
    usuario_id: str,
    data: CambiarPasswordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return UsuarioService(db).cambiar_password(
        usuario_id, data, current_user.id
    )


@router.delete(
    "/usuarios/{usuario_id}",
    summary="Desactivar usuario",
    description="Desactiva el usuario. No se puede desactivar la propia cuenta.",
)
def desactivar_usuario(
    usuario_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return UsuarioService(db).desactivar(usuario_id, current_user.id)
