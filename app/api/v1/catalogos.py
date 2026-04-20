from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.schemas.catalogo import (
    TipoServicioCreate, TipoServicioUpdate, TipoServicioOut,
    AreaCreate, AreaUpdate, AreaOut,
)
from app.services.catalogo_service import TipoServicioService, AreaService

router = APIRouter()


# ══════════════════════════════════════════════════════
#  TIPO SERVICIO
# ══════════════════════════════════════════════════════

@router.get(
    "/tipo-servicios",
    response_model=list[TipoServicioOut],
    summary="Listar tipos de servicio",
)
def listar_tipo_servicios(
    solo_activos: bool = Query(False, description="Si es true, retorna solo los activos"),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return TipoServicioService(db).get_all(solo_activos=solo_activos)


@router.get(
    "/tipo-servicios/{tipo_id}",
    response_model=TipoServicioOut,
    summary="Obtener tipo de servicio por ID",
)
def obtener_tipo_servicio(
    tipo_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return TipoServicioService(db).get_by_id(tipo_id)


@router.post(
    "/tipo-servicios",
    response_model=TipoServicioOut,
    status_code=201,
    summary="Crear tipo de servicio",
)
def crear_tipo_servicio(
    data: TipoServicioCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return TipoServicioService(db).create(data)


@router.put(
    "/tipo-servicios/{tipo_id}",
    response_model=TipoServicioOut,
    summary="Actualizar tipo de servicio",
)
def actualizar_tipo_servicio(
    tipo_id: str,
    data: TipoServicioUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return TipoServicioService(db).update(tipo_id, data)


@router.delete(
    "/tipo-servicios/{tipo_id}",
    summary="Eliminar tipo de servicio",
    description="Elimina lógicamente (desactiva) el tipo de servicio. "
                "No se puede eliminar si tiene tickets asociados.",
)
def eliminar_tipo_servicio(
    tipo_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return TipoServicioService(db).delete(tipo_id)


# ══════════════════════════════════════════════════════
#  AREAS
# ══════════════════════════════════════════════════════

@router.get(
    "/areas",
    response_model=list[AreaOut],
    summary="Listar áreas",
)
def listar_areas(
    solo_activos: bool = Query(False, description="Si es true, retorna solo las activas"),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return AreaService(db).get_all(solo_activos=solo_activos)


@router.get(
    "/areas/{area_id}",
    response_model=AreaOut,
    summary="Obtener área por ID",
)
def obtener_area(
    area_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return AreaService(db).get_by_id(area_id)


@router.post(
    "/areas",
    response_model=AreaOut,
    status_code=201,
    summary="Crear área",
)
def crear_area(
    data: AreaCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return AreaService(db).create(data)


@router.put(
    "/areas/{area_id}",
    response_model=AreaOut,
    summary="Actualizar área",
)
def actualizar_area(
    area_id: str,
    data: AreaUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return AreaService(db).update(area_id, data)


@router.delete(
    "/areas/{area_id}",
    summary="Eliminar área",
    description="Elimina lógicamente (desactiva) el área. "
                "No se puede eliminar si tiene tickets asociados.",
)
def eliminar_area(
    area_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return AreaService(db).delete(area_id)
