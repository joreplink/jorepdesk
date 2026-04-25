from pydantic import BaseModel, field_validator, model_validator
from datetime import date, datetime
from typing import Optional
from app.schemas.usuario import UsuarioResumen


TIPOS_REPORTE = ("por_tipo_servicio", "por_area", "por_agente")


class ReporteParams(BaseModel):
    """Parámetros de consulta para generar un reporte."""
    tipo: str
    filtro_id: Optional[str] = None
    fecha_inicio: date
    fecha_fin: date

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v: str) -> str:
        if v not in TIPOS_REPORTE:
            raise ValueError(f"Tipo inválido. Opciones: {TIPOS_REPORTE}")
        return v

    @model_validator(mode="after")
    def fechas_validas(self) -> "ReporteParams":
        if self.fecha_inicio > self.fecha_fin:
            raise ValueError("fecha_inicio no puede ser posterior a fecha_fin.")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "tipo": "por_area",
                "filtro_id": "<uuid-area>",
                "fecha_inicio": "2026-01-01",
                "fecha_fin": "2026-04-30",
            }
        }
    }


# ── Métricas ──────────────────────────────────────────────────────────────────

class TicketResumenMetrica(BaseModel):
    """Fila de resumen en el reporte."""
    nombre: str               # nombre del área / agente / tipo servicio
    total: int
    abiertos: int
    en_proceso: int
    cerrados: int
    promedio_horas_cierre: Optional[float] = None


class ReporteOut(BaseModel):
    id: str
    tipo: str
    filtro_id: Optional[str] = None
    fecha_inicio: date
    fecha_fin: date
    generado_en: datetime
    generado_por: UsuarioResumen
    metricas: list[TicketResumenMetrica]
    total_tickets: int

    model_config = {"from_attributes": True}
