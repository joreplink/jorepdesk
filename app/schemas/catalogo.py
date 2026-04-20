from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


# ══════════════════════════════════════════════════════
#  TIPO SERVICIO
# ══════════════════════════════════════════════════════

class TipoServicioBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío.")
        if len(v) > 100:
            raise ValueError("El nombre no puede superar 100 caracteres.")
        return v


class TipoServicioCreate(TipoServicioBase):
    pass

    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Soporte de Hardware",
                "descripcion": "Fallas en equipos físicos: computadoras, impresoras, etc.",
            }
        }
    }


class TipoServicioUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("El nombre no puede estar vacío.")
        return v


class TipoServicioOut(TipoServicioBase):
    id: str
    activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════
#  AREA
# ══════════════════════════════════════════════════════

class AreaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío.")
        if len(v) > 100:
            raise ValueError("El nombre no puede superar 100 caracteres.")
        return v


class AreaCreate(AreaBase):
    pass

    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Recursos Humanos",
                "descripcion": "Oficina de RRHH piso 3",
                "ubicacion": "Edificio A, Piso 3",
            }
        }
    }


class AreaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("El nombre no puede estar vacío.")
        return v


class AreaOut(AreaBase):
    id: str
    activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}
