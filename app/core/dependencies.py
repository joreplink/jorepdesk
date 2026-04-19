from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.db.session import get_db

# El tokenUrl apunta al endpoint de login que crearemos en la Fase 3
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Dependencia base: extrae y valida el JWT del header Authorization.
    Retorna el objeto Usuario activo del token.

    Uso:
        @router.get("/endpoint")
        def mi_endpoint(current_user = Depends(get_current_user)):
            ...
    """
    # Importación local para evitar circular imports con los modelos
    from app.models.usuario import Usuario

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
    """
    Dependencia que exige rol 'admin'.
    Lanza 403 si el usuario autenticado no es administrador.

    Uso:
        @router.post("/tickets", dependencies=[Depends(require_admin)])
        def crear_ticket(...):
            ...

        # O para acceder al usuario dentro del endpoint:
        @router.post("/tickets")
        def crear_ticket(current_user = Depends(require_admin)):
            ...
    """
    if current_user.rol != "admin":
        raise ForbiddenException("Se requiere rol de administrador.")
    return current_user


def require_agente(current_user=Depends(get_current_user)):
    """
    Dependencia que exige rol 'agente'.
    Lanza 403 si el usuario autenticado no es agente.
    """
    if current_user.rol != "agente":
        raise ForbiddenException("Se requiere rol de agente.")
    return current_user


def require_admin_or_agente(current_user=Depends(get_current_user)):
    """
    Dependencia que permite acceso a ambos roles.
    Útil para endpoints compartidos como GET /tickets/:id
    """
    if current_user.rol not in ("admin", "agente"):
        raise ForbiddenException("Acceso no autorizado.")
    return current_user
