import uuid
from sqlalchemy.orm import Session

from app.models.tipo_servicio import TipoServicio
from app.models.area import Area
from app.repositories.catalogo_repository import TipoServicioRepository, AreaRepository
from app.schemas.catalogo import (
    TipoServicioCreate, TipoServicioUpdate, TipoServicioOut,
    AreaCreate, AreaUpdate, AreaOut,
)
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException


# ══════════════════════════════════════════════════════
#  TIPO SERVICIO SERVICE
# ══════════════════════════════════════════════════════

class TipoServicioService:

    def __init__(self, db: Session):
        self.repo = TipoServicioRepository(db)

    def get_all(self, solo_activos: bool = False) -> list[TipoServicioOut]:
        tipos = self.repo.get_all(solo_activos=solo_activos)
        return [TipoServicioOut.model_validate(t) for t in tipos]

    def get_by_id(self, tipo_id: str) -> TipoServicioOut:
        tipo = self.repo.get_by_id(tipo_id)
        if not tipo:
            raise NotFoundException("Tipo de servicio")
        return TipoServicioOut.model_validate(tipo)

    def create(self, data: TipoServicioCreate) -> TipoServicioOut:
        # Verifica nombre único
        if self.repo.get_by_nombre(data.nombre):
            raise ConflictException(
                f"Ya existe un tipo de servicio con el nombre '{data.nombre}'."
            )
        tipo = TipoServicio(
            id=str(uuid.uuid4()),
            nombre=data.nombre.strip(),
            descripcion=data.descripcion,
            activo=True,
        )
        tipo = self.repo.create(tipo)
        return TipoServicioOut.model_validate(tipo)

    def update(self, tipo_id: str, data: TipoServicioUpdate) -> TipoServicioOut:
        tipo = self.repo.get_by_id(tipo_id)
        if not tipo:
            raise NotFoundException("Tipo de servicio")

        # Verifica nombre único si se está cambiando
        if data.nombre is not None:
            if self.repo.get_by_nombre(data.nombre, exclude_id=tipo_id):
                raise ConflictException(
                    f"Ya existe un tipo de servicio con el nombre '{data.nombre}'."
                )
            tipo.nombre = data.nombre.strip()

        if data.descripcion is not None:
            tipo.descripcion = data.descripcion

        if data.activo is not None:
            tipo.activo = data.activo

        tipo = self.repo.update(tipo)
        return TipoServicioOut.model_validate(tipo)

    def delete(self, tipo_id: str) -> dict:
        tipo = self.repo.get_by_id(tipo_id)
        if not tipo:
            raise NotFoundException("Tipo de servicio")

        # No elimina si tiene tickets — desactiva en su lugar
        if self.repo.tiene_tickets(tipo_id):
            raise BadRequestException(
                "No se puede eliminar un tipo de servicio con tickets asociados. "
                "Desactívalo en su lugar."
            )
        tipo.activo = False
        self.repo.update(tipo)
        return {"message": "Tipo de servicio eliminado correctamente."}


# ══════════════════════════════════════════════════════
#  AREA SERVICE
# ══════════════════════════════════════════════════════

class AreaService:

    def __init__(self, db: Session):
        self.repo = AreaRepository(db)

    def get_all(self, solo_activos: bool = False) -> list[AreaOut]:
        areas = self.repo.get_all(solo_activos=solo_activos)
        return [AreaOut.model_validate(a) for a in areas]

    def get_by_id(self, area_id: str) -> AreaOut:
        area = self.repo.get_by_id(area_id)
        if not area:
            raise NotFoundException("Área")
        return AreaOut.model_validate(area)

    def create(self, data: AreaCreate) -> AreaOut:
        if self.repo.get_by_nombre(data.nombre):
            raise ConflictException(
                f"Ya existe un área con el nombre '{data.nombre}'."
            )
        area = Area(
            id=str(uuid.uuid4()),
            nombre=data.nombre.strip(),
            descripcion=data.descripcion,
            ubicacion=data.ubicacion,
            activo=True,
        )
        area = self.repo.create(area)
        return AreaOut.model_validate(area)

    def update(self, area_id: str, data: AreaUpdate) -> AreaOut:
        area = self.repo.get_by_id(area_id)
        if not area:
            raise NotFoundException("Área")

        if data.nombre is not None:
            if self.repo.get_by_nombre(data.nombre, exclude_id=area_id):
                raise ConflictException(
                    f"Ya existe un área con el nombre '{data.nombre}'."
                )
            area.nombre = data.nombre.strip()

        if data.descripcion is not None:
            area.descripcion = data.descripcion

        if data.ubicacion is not None:
            area.ubicacion = data.ubicacion

        if data.activo is not None:
            area.activo = data.activo

        area = self.repo.update(area)
        return AreaOut.model_validate(area)

    def delete(self, area_id: str) -> dict:
        area = self.repo.get_by_id(area_id)
        if not area:
            raise NotFoundException("Área")

        if self.repo.tiene_tickets(area_id):
            raise BadRequestException(
                "No se puede eliminar un área con tickets asociados. "
                "Desactívala en su lugar."
            )
        area.activo = False
        self.repo.update(area)
        return {"message": "Área eliminada correctamente."}
