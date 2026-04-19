import uuid
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR, BIGINT

from app.db.base import Base


class Evidencia(Base):
    __tablename__ = "evidencias"

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    ticket_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("tickets.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    subido_por_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("usuarios.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_archivo: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ruta: Mapped[str] = mapped_column(Text, nullable=False)
    tamano_bytes: Mapped[int] = mapped_column(BIGINT, nullable=False)
    subido_en: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # ── Relaciones ───────────────────────────────────────────────────────────
    ticket: Mapped["Ticket"] = relationship(
        "Ticket", back_populates="evidencias"
    )
    subido_por: Mapped["Usuario"] = relationship(
        "Usuario", back_populates="evidencias"
    )

    def __repr__(self) -> str:
        return f"<Evidencia {self.nombre_archivo} ticket={self.ticket_id}>"

    @property
    def tamano_legible(self) -> str:
        """Retorna el tamaño del archivo en formato legible (KB, MB)."""
        if self.tamano_bytes < 1024:
            return f"{self.tamano_bytes} B"
        elif self.tamano_bytes < 1024 * 1024:
            return f"{self.tamano_bytes / 1024:.1f} KB"
        return f"{self.tamano_bytes / (1024 * 1024):.1f} MB"
