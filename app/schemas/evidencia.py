from pydantic import BaseModel
from datetime import datetime
from app.schemas.usuario import UsuarioResumen


class EvidenciaOut(BaseModel):
    id: str
    nombre_archivo: str
    tipo_archivo: str
    ruta: str
    tamano_bytes: int
    subido_en: datetime
    subido_por: UsuarioResumen

    model_config = {"from_attributes": True}

    @property
    def tamano_legible(self) -> str:
        if self.tamano_bytes < 1024:
            return f"{self.tamano_bytes} B"
        elif self.tamano_bytes < 1024 * 1024:
            return f"{self.tamano_bytes / 1024:.1f} KB"
        return f"{self.tamano_bytes / (1024 * 1024):.1f} MB"
