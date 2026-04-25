import uuid
import os
import shutil
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.evidencia import Evidencia
from app.models.usuario import Usuario
from app.repositories.evidencia_repository import EvidenciaRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.evidencia import EvidenciaOut
from app.schemas.usuario import UsuarioResumen
from app.core.config import get_settings
from app.core.exceptions import (
    NotFoundException, ForbiddenException,
    BadRequestException, UnprocessableException,
)

settings = get_settings()


class EvidenciaService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = EvidenciaRepository(db)
        self.ticket_repo = TicketRepository(db)

    def get_by_ticket(self, ticket_id: str, current_user: Usuario) -> list[EvidenciaOut]:
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket")

        if current_user.rol == "agente":
            asignacion = self.ticket_repo.get_asignacion_activa(ticket_id, current_user.id)
            if not asignacion:
                raise ForbiddenException("No estás asignado a este ticket.")

        evidencias = self.repo.get_by_ticket(ticket_id)
        return [self._to_out(e) for e in evidencias]

    async def subir(
        self, ticket_id: str, archivo: UploadFile, agente: Usuario
    ) -> EvidenciaOut:
        # Valida que el ticket exista y no esté cerrado
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket")

        if ticket.estado == "cerrado":
            raise BadRequestException(
                "No se pueden subir evidencias a un ticket cerrado."
            )

        # Verifica que el agente esté asignado
        asignacion = self.ticket_repo.get_asignacion_activa(ticket_id, agente.id)
        if not asignacion:
            raise ForbiddenException("No estás asignado a este ticket.")

        # Valida tipo de archivo
        if archivo.content_type not in settings.allowed_mime_types_list:
            raise UnprocessableException(
                f"Tipo de archivo no permitido: {archivo.content_type}. "
                f"Permitidos: {', '.join(settings.allowed_mime_types_list)}"
            )

        # Lee el contenido para validar tamaño
        contenido = await archivo.read()
        tamano = len(contenido)

        if tamano > settings.max_file_size_bytes:
            raise UnprocessableException(
                f"El archivo supera el tamaño máximo permitido "
                f"({settings.max_file_size_mb} MB)."
            )

        if tamano == 0:
            raise BadRequestException("El archivo está vacío.")

        # Guarda el archivo en disco organizado por ticket
        carpeta = os.path.join(settings.media_dir, "tickets", ticket_id)
        os.makedirs(carpeta, exist_ok=True)

        # Nombre único para evitar colisiones
        extension = os.path.splitext(archivo.filename or "archivo")[1]
        nombre_unico = f"{uuid.uuid4()}{extension}"
        ruta_completa = os.path.join(carpeta, nombre_unico)
        ruta_relativa = os.path.join("tickets", ticket_id, nombre_unico)

        with open(ruta_completa, "wb") as f:
            f.write(contenido)

        # Persiste en base de datos
        evidencia = Evidencia(
            id=str(uuid.uuid4()),
            ticket_id=ticket_id,
            subido_por_id=agente.id,
            nombre_archivo=archivo.filename or nombre_unico,
            tipo_archivo=archivo.content_type,
            ruta=ruta_relativa,
            tamano_bytes=tamano,
        )
        evidencia = self.repo.create(evidencia)
        return self._to_out(evidencia)

    def _to_out(self, evidencia: Evidencia) -> EvidenciaOut:
        return EvidenciaOut(
            id=evidencia.id,
            nombre_archivo=evidencia.nombre_archivo,
            tipo_archivo=evidencia.tipo_archivo,
            ruta=evidencia.ruta,
            tamano_bytes=evidencia.tamano_bytes,
            subido_en=evidencia.subido_en,
            subido_por=UsuarioResumen.model_validate(evidencia.subido_por),
        )
