import uuid
from sqlalchemy import String, Boolean, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR

from app.db.base import Base


class TipoServicio(Base):
    __tablename__ = "tipo_servicios"

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    creado_en: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relaciones ───────────────────────────────────────────────────────────
    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket", back_populates="tipo_servicio"
    )

    def __repr__(self) -> str:
        return f"<TipoServicio {self.nombre}>"
