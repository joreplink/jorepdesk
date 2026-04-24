from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from app.schemas.usuario import UsuarioResumen
from app.schemas.catalogo import TipoServicioOut, AreaOut


# ── Enums como constantes ─────────────────────────────────────────────────────
ESTADOS_VALIDOS    = ("abierto", "en_proceso", "cerrado")
PRIORIDADES_VALIDAS = ("baja", "media", "alta", "critica")

# Transiciones permitidas de estado
TRANSICIONES = {
    "abierto":    ["en_proceso"],
    "en_proceso": ["cerrado"],
    "cerrado":    [],           # estado final — no se puede cambiar
}


# ── Request schemas ───────────────────────────────────────────────────────────

class TicketCreate(BaseModel):
    titulo: str
    descripcion: str
    prioridad: str = "media"
    nombre_reportante: str
    telefono_reportante: Optional[str] = None
    tipo_servicio_id: str
    area_id: str

    @field_validator("titulo")
    @classmethod
    def titulo_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El título no puede estar vacío.")
        if len(v) > 200:
            raise ValueError("El título no puede superar 200 caracteres.")
        return v

    @field_validator("descripcion")
    @classmethod
    def descripcion_valida(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("La descripción no puede estar vacía.")
        return v

    @field_validator("nombre_reportante")
    @classmethod
    def nombre_reportante_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre del reportante no puede estar vacío.")
        return v

    @field_validator("prioridad")
    @classmethod
    def prioridad_valida(cls, v: str) -> str:
        if v not in PRIORIDADES_VALIDAS:
            raise ValueError(f"Prioridad inválida. Opciones: {PRIORIDADES_VALIDAS}")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "titulo": "Computadora no enciende",
                "descripcion": "El equipo del usuario no enciende desde esta mañana.",
                "prioridad": "alta",
                "nombre_reportante": "María García",
                "telefono_reportante": "555-9876",
                "tipo_servicio_id": "<uuid-tipo-servicio>",
                "area_id": "<uuid-area>",
            }
        }
    }


class TicketAsignarRequest(BaseModel):
    agente_ids: list[str]

    @field_validator("agente_ids")
    @classmethod
    def al_menos_uno(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Debes asignar al menos un agente.")
        if len(set(v)) != len(v):
            raise ValueError("No puedes asignar el mismo agente dos veces.")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {"agente_ids": ["<uuid-agente-1>", "<uuid-agente-2>"]}
        }
    }


class TicketCambiarEstadoRequest(BaseModel):
    estado: str

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v: str) -> str:
        if v not in ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido. Opciones: {ESTADOS_VALIDOS}")
        return v

    model_config = {
        "json_schema_extra": {"example": {"estado": "en_proceso"}}
    }


# ── Response schemas ──────────────────────────────────────────────────────────

class AgenteSummary(BaseModel):
    id: str
    nombre: str
    apellido: str
    cargo: Optional[str] = None

    model_config = {"from_attributes": True}


class HistorialEstadoOut(BaseModel):
    id: str
    estado_anterior: str
    estado_nuevo: str
    cambiado_en: datetime
    cambiado_por: UsuarioResumen

    model_config = {"from_attributes": True}


class TicketOut(BaseModel):
    """Schema resumido — para listados."""
    id: str
    numero: str
    titulo: str
    estado: str
    prioridad: str
    nombre_reportante: str
    telefono_reportante: Optional[str] = None
    tipo_servicio: TipoServicioOut
    area: AreaOut
    creado_por: UsuarioResumen
    creado_en: datetime
    actualizado_en: datetime
    cerrado_en: Optional[datetime] = None
    agentes: list[AgenteSummary] = []

    model_config = {"from_attributes": True}


class TicketDetail(TicketOut):
    """Schema detallado — incluye historial de estados."""
    historial_estados: list[HistorialEstadoOut] = []

    model_config = {"from_attributes": True}
