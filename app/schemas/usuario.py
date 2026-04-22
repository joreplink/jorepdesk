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

    @field_validator("rol")
    @classmethod
    def rol_valido(cls, v: str) -> str:
        if v not in ("admin", "agente"):
            raise ValueError("El rol debe ser 'admin' o 'agente'.")
        return v

    @field_validator("nombre", "apellido")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Este campo no puede estar vacío.")
        return v


class UsuarioCreate(UsuarioBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_seguro(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Carlos",
                "apellido": "Mendez",
                "email": "carlos@helpdesk.com",
                "password": "Password123!",
                "rol": "agente",
                "cargo": "Tecnico de Soporte",
                "telefono": "555-1234",
            }
        }
    }


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    cargo: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("nombre", "apellido")
    @classmethod
    def no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Este campo no puede estar vacío.")
        return v


class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nuevo: str

    @field_validator("password_nuevo")
    @classmethod
    def password_seguro(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contrasena debe tener al menos 8 caracteres.")
        return v


class UsuarioOut(UsuarioBase):
    """Schema de respuesta — nunca expone password_hash."""
    id: str
    activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


class UsuarioResumen(BaseModel):
    """Schema minimo para referencias dentro de otros schemas."""
    id: str
    nombre: str
    apellido: str
    email: EmailStr
    rol: str
    cargo: Optional[str] = None

    model_config = {"from_attributes": True}
