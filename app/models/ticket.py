import uuid
from sqlalchemy import String, Text, Boolean, Enum as SAEnum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    numero: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(
        SAEnum("abierto", "en_proceso", "cerrado", name="estado_ticket"),
        nullable=False,
        default="abierto",
        index=True,
    )
    prioridad: Mapped[str] = mapped_column(
        SAEnum("baja", "media", "alta", "critica", name="prioridad_ticket"),
        nullable=False,
        default="media",
        index=True,
    )
    nombre_reportante: Mapped[str] = mapped_column(String(150), nullable=False)
    telefono_reportante: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ── Foreign Keys ─────────────────────────────────────────────────────────
    creado_por_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("usuarios.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    tipo_servicio_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("tipo_servicios.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    area_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("areas.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    # ── Timestamps ───────────────────────────────────────────────────────────
    creado_en: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )
    actualizado_en: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    cerrado_en: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True, index=True)

    # ── Relaciones ───────────────────────────────────────────────────────────
    creado_por: Mapped["Usuario"] = relationship(
        "Usuario", back_populates="tickets_creados", foreign_keys=[creado_por_id]
    )
    tipo_servicio: Mapped["TipoServicio"] = relationship(
        "TipoServicio", back_populates="tickets"
    )
    area: Mapped["Area"] = relationship(
        "Area", back_populates="tickets"
    )
    asignaciones: Mapped[list["TicketAgente"]] = relationship(
        "TicketAgente", back_populates="ticket", cascade="all, delete-orphan"
    )
    observaciones: Mapped[list["Observacion"]] = relationship(
        "Observacion", back_populates="ticket", cascade="all, delete-orphan",
        order_by="Observacion.creado_en"
    )
    evidencias: Mapped[list["Evidencia"]] = relationship(
        "Evidencia", back_populates="ticket", cascade="all, delete-orphan"
    )
    historial_estados: Mapped[list["HistorialEstado"]] = relationship(
        "HistorialEstado", back_populates="ticket", cascade="all, delete-orphan",
        order_by="HistorialEstado.cambiado_en"
    )

    def __repr__(self) -> str:
        return f"<Ticket {self.numero} [{self.estado}]>"

    @property
    def agentes_activos(self) -> list:
        """Retorna solo las asignaciones activas del ticket."""
        return [a for a in self.asignaciones if a.activo]

    @property
    def is_cerrado(self) -> bool:
        return self.estado == "cerrado"
