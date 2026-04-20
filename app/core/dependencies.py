from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.db.session import get_db

# HTTPBearer muestra en Swagger un campo simple para pegar el token
http_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db),
):
    """
    Dependencia base: extrae y valida el JWT del header Authorization.
    Retorna el objeto Usuario activo del token.
    """
    from app.models.usuario import Usuario

    if not credentials:
        raise UnauthorizedException("Token no proporcionado.")

    token = credentials.credentials
    payload = decode_token(token, expected_type="access")
    user_id: str = payload.get("sub")

    if not user_id:
        raise UnauthorizedException("Token sin identificador de usuario.")

    user = db.get(Usuario, user_id)

    if not user:
        raise UnauthorizedException("Usuario no encontrado.")

    if not user.activo:
        raise UnauthorizedException("Usuario inactivo.")

    return user


def require_admin(current_user=Depends(get_current_user)):
    if current_user.rol != "admin":
        raise ForbiddenException("Se requiere rol de administrador.")
    return current_user


def require_agente(current_user=Depends(get_current_user)):
    if current_user.rol != "agente":
        raise ForbiddenException("Se requiere rol de agente.")
    return current_user


def require_admin_or_agente(current_user=Depends(get_current_user)):
    if current_user.rol not in ("admin", "agente"):
        raise ForbiddenException("Acceso no autorizado.")
    return current_user
