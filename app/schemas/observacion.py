from pydantic import BaseModel, field_validator
from datetime import datetime
from app.schemas.usuario import UsuarioResumen


class ObservacionCreate(BaseModel):
    contenido: str

    @field_validator("contenido")
    @classmethod
    def contenido_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El contenido no puede estar vacío.")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "contenido": "Se revisó el equipo. El problema es la fuente de poder. Se procederá a reemplazarla."
            }
        }
    }


class ObservacionOut(BaseModel):
    id: str
    contenido: str
    creado_en: datetime
    agente: UsuarioResumen

    model_config = {"from_attributes": True}
