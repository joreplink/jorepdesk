import uuid
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioOut, CambiarPasswordRequest
from app.core.security import hash_password, verify_password
from app.core.exceptions import (
    NotFoundException, ConflictException,
    BadRequestException, ForbiddenException,
)


class UsuarioService:

    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)

    def get_all(self, rol: str | None = None, solo_activos: bool = False) -> list[UsuarioOut]:
        if rol == "agente":
            usuarios = self.repo.get_agentes(solo_activos=solo_activos)
        else:
            usuarios = self.repo.get_all(solo_activos=solo_activos)
            if rol:
                usuarios = [u for u in usuarios if u.rol == rol]
        return [UsuarioOut.model_validate(u) for u in usuarios]

    def get_by_id(self, usuario_id: str) -> UsuarioOut:
        usuario = self.repo.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundException("Usuario")
        return UsuarioOut.model_validate(usuario)

    def create(self, data: UsuarioCreate) -> UsuarioOut:
        # Email único
        if self.repo.email_exists(data.email):
            raise ConflictException(
                f"Ya existe un usuario con el email '{data.email}'."
            )
        usuario = Usuario(
            id=str(uuid.uuid4()),
            nombre=data.nombre.strip(),
            apellido=data.apellido.strip(),
            email=data.email.lower().strip(),
            password_hash=hash_password(data.password),
            rol=data.rol,
            cargo=data.cargo,
            telefono=data.telefono,
            activo=True,
        )
        usuario = self.repo.create(usuario)
        return UsuarioOut.model_validate(usuario)

    def update(self, usuario_id: str, data: UsuarioUpdate) -> UsuarioOut:
        usuario = self.repo.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundException("Usuario")

        if data.nombre is not None:
            usuario.nombre = data.nombre.strip()
        if data.apellido is not None:
            usuario.apellido = data.apellido.strip()
        if data.cargo is not None:
            usuario.cargo = data.cargo
        if data.telefono is not None:
            usuario.telefono = data.telefono
        if data.activo is not None:
            usuario.activo = data.activo

        usuario = self.repo.update(usuario)
        return UsuarioOut.model_validate(usuario)

    def cambiar_password(
        self,
        usuario_id: str,
        data: CambiarPasswordRequest,
        current_user_id: str,
    ) -> dict:
        # Solo el propio usuario puede cambiar su contraseña
        if usuario_id != current_user_id:
            raise ForbiddenException(
                "Solo puedes cambiar tu propia contraseña."
            )
        usuario = self.repo.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundException("Usuario")

        if not verify_password(data.password_actual, usuario.password_hash):
            raise BadRequestException("La contraseña actual es incorrecta.")

        if data.password_actual == data.password_nuevo:
            raise BadRequestException(
                "La contraseña nueva debe ser diferente a la actual."
            )
        usuario.password_hash = hash_password(data.password_nuevo)
        self.repo.update(usuario)
        return {"message": "Contraseña actualizada correctamente."}

    def desactivar(self, usuario_id: str, current_user_id: str) -> dict:
        if usuario_id == current_user_id:
            raise BadRequestException("No puedes desactivar tu propia cuenta.")

        usuario = self.repo.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundException("Usuario")

        usuario.activo = False
        self.repo.update(usuario)
        return {"message": f"Usuario {usuario.email} desactivado correctamente."}
