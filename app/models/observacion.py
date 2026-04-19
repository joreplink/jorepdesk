import uuid
from sqlalchemy import Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR

from app.db.base import Base


class Observacion(Base):
    __tablename__ = "observaciones"

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
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    creado_en: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )

    # ── Relaciones ───────────────────────────────────────────────────────────
    ticket: Mapped["Ticket"] = relationship(
        "Ticket", back_populates="observaciones"
    )
    agente: Mapped["Usuario"] = relationship(
        "Usuario", back_populates="observaciones"
    )

    def __repr__(self) -> str:
        return f"<Observacion ticket={self.ticket_id} agente={self.agente_id}>"
