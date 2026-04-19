from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional


class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    rol: str
    cargo: Optional[str] = None
    telefono: Optional[str] = None


class UsuarioOut(UsuarioBase):
    """Schema de respuesta — nunca expone password_hash."""
    id: str
    activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"


class UsuarioResumen(BaseModel):
    """Schema mínimo para referencias en otros schemas (ej: dentro de un Ticket)."""
    id: str
    nombre: str
    apellido: str
    email: EmailStr
    rol: str
    cargo: Optional[str] = None

    model_config = {"from_attributes": True}
