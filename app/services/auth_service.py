from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import UnauthorizedException
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import LoginRequest, TokenResponse, RefreshResponse
from app.schemas.usuario import UsuarioOut


class AuthService:

    def __init__(self, db: Session):
        self.db = db
        self.usuario_repo = UsuarioRepository(db)

    def login(self, data: LoginRequest) -> TokenResponse:
        """
        Valida credenciales y retorna access + refresh token.
        Lanza 401 si el email no existe, la contraseña es incorrecta
        o el usuario está inactivo.
        """
        usuario = self.usuario_repo.get_by_email(data.email)

        # Mensaje genérico intencional — no revela si el email existe o no
        if not usuario:
            raise UnauthorizedException("Credenciales incorrectas.")

        if not verify_password(data.password, usuario.password_hash):
            raise UnauthorizedException("Credenciales incorrectas.")

        if not usuario.activo:
            raise UnauthorizedException("Usuario inactivo. Contacta al administrador.")

        # Claims extra que se incluyen en el token para no tener que
        # consultar la DB en cada request
        extra_claims = {"rol": usuario.rol, "email": usuario.email}

        access_token  = create_access_token(usuario.id, extra_claims)
        refresh_token = create_refresh_token(usuario.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UsuarioOut.model_validate(usuario),
        )

    def refresh(self, refresh_token: str) -> RefreshResponse:
        """
        Valida el refresh token y emite un nuevo access token.
        Lanza 401 si el refresh token es inválido o el usuario ya no existe.
        """
        payload = decode_token(refresh_token, expected_type="refresh")
        user_id = payload.get("sub")

        usuario = self.usuario_repo.get_by_id(user_id)

        if not usuario or not usuario.activo:
            raise UnauthorizedException("Token inválido.")

        extra_claims = {"rol": usuario.rol, "email": usuario.email}
        new_access_token = create_access_token(usuario.id, extra_claims)

        return RefreshResponse(access_token=new_access_token)
