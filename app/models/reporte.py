import uuid
from sqlalchemy import Date, DateTime, ForeignKey, Enum as SAEnum, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR

from app.db.base import Base


class Reporte(Base):
    __tablename__ = "reportes"

    __table_args__ = (
        CheckConstraint("fecha_inicio <= fecha_fin", name="chk_reportes_fechas"),
    )

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    generado_por_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("usuarios.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    tipo: Mapped[str] = mapped_column(
        SAEnum("por_tipo_servicio", "por_area", "por_agente", name="tipo_reporte"),
        nullable=False, index=True,
    )
    # UUID del área / agente / tipo_servicio según el tipo del reporte
    filtro_id: Mapped[str | None] = mapped_column(CHAR(36), nullable=True, index=True)
    fecha_inicio: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    fecha_fin: Mapped[Date] = mapped_column(Date, nullable=False)
    generado_en: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )

    # ── Relaciones ───────────────────────────────────────────────────────────
    generado_por: Mapped["Usuario"] = relationship(
        "Usuario", back_populates="reportes"
    )

    def __repr__(self) -> str:
        return f"<Reporte {self.tipo} {self.fecha_inicio}→{self.fecha_fin}>"
