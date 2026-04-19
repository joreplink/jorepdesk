import uuid
from sqlalchemy import Boolean, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR

from app.db.base import Base


class TicketAgente(Base):
    __tablename__ = "ticket_agentes"

    __table_args__ = (
        # Evita duplicar una asignación activa del mismo agente al mismo ticket
        UniqueConstraint("ticket_id", "agente_id", "activo", name="uq_ticket_agente_activo"),
    )

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    ticket_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("tickets.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    agente_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("usuarios.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    asignado_por_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("usuarios.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    asignado_en: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )

    # ── Relaciones ───────────────────────────────────────────────────────────
    ticket: Mapped["Ticket"] = relationship(
        "Ticket", back_populates="asignaciones"
    )
    agente: Mapped["Usuario"] = relationship(
        "Usuario", back_populates="asignaciones", foreign_keys=[agente_id]
    )
    asignado_por: Mapped["Usuario"] = relationship(
        "Usuario", foreign_keys=[asignado_por_id]
    )

    def __repr__(self) -> str:
        return f"<TicketAgente ticket={self.ticket_id} agente={self.agente_id} activo={self.activo}>"
