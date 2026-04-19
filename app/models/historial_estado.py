import uuid
from sqlalchemy import DateTime, ForeignKey, Enum as SAEnum, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR

from app.db.base import Base


class HistorialEstado(Base):
    __tablename__ = "historial_estados"

    __table_args__ = (
        CheckConstraint(
            "estado_anterior <> estado_nuevo",
            name="chk_historial_estados_distintos",
        ),
    )

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    ticket_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("tickets.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    cambiado_por_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("usuarios.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    estado_anterior: Mapped[str] = mapped_column(
        SAEnum("abierto", "en_proceso", "cerrado", name="estado_ticket_historial_ant"),
        nullable=False,
    )
    estado_nuevo: Mapped[str] = mapped_column(
        SAEnum("abierto", "en_proceso", "cerrado", name="estado_ticket_historial_new"),
        nullable=False, index=True,
    )
    cambiado_en: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )

    # ── Relaciones ───────────────────────────────────────────────────────────
    ticket: Mapped["Ticket"] = relationship(
        "Ticket", back_populates="historial_estados"
    )
    cambiado_por: Mapped["Usuario"] = relationship(
        "Usuario", back_populates="historial_estados"
    )

    def __repr__(self) -> str:
        return f"<HistorialEstado {self.estado_anterior}→{self.estado_nuevo} ticket={self.ticket_id}>"
