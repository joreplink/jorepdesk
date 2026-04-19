import uuid
from sqlalchemy import String, Boolean, Enum as SAEnum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(
        SAEnum("admin", "agente", name="rol_usuario"), nullable=False, index=True
    )
    cargo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    creado_en: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relaciones ───────────────────────────────────────────────────────────
    # Tickets que este admin creó
    tickets_creados: Mapped[list["Ticket"]] = relationship(
        "Ticket", back_populates="creado_por", foreign_keys="Ticket.creado_por_id"
    )
    # Asignaciones como agente
    asignaciones: Mapped[list["TicketAgente"]] = relationship(
        "TicketAgente", back_populates="agente", foreign_keys="TicketAgente.agente_id"
    )
    # Observaciones escritas
    observaciones: Mapped[list["Observacion"]] = relationship(
        "Observacion", back_populates="agente"
    )
    # Evidencias subidas
    evidencias: Mapped[list["Evidencia"]] = relationship(
        "Evidencia", back_populates="subido_por"
    )
    # Cambios de estado registrados
    historial_estados: Mapped[list["HistorialEstado"]] = relationship(
        "HistorialEstado", back_populates="cambiado_por"
    )
    # Reportes generados
    reportes: Mapped[list["Reporte"]] = relationship(
        "Reporte", back_populates="generado_por"
    )

    def __repr__(self) -> str:
        return f"<Usuario {self.email} [{self.rol}]>"

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

    @property
    def is_admin(self) -> bool:
        return self.rol == "admin"

    @property
    def is_agente(self) -> bool:
        return self.rol == "agente"
