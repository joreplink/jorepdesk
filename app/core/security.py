from datetime import datetime, timedelta, timezone
from typing import Any
import warnings

# Silencia el warning de compatibilidad entre passlib y bcrypt 4.x
warnings.filterwarnings("ignore", ".*error reading bcrypt version.*")
warnings.filterwarnings("ignore", ".*trapped.*")

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException

settings = get_settings()

# ── Hashing de contraseñas ───────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Genera el hash bcrypt de una contraseña en texto plano."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con su hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT ──────────────────────────────────────────────────────────────────────
def create_access_token(subject: str | Any, extra_claims: dict = {}) -> str:
    """
    Genera un JWT de acceso.

    Args:
        subject:      Identificador del usuario (UUID como string).
        extra_claims: Claims adicionales (ej: {"rol": "admin"}).

    Returns:
        Token JWT firmado como string.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
        **extra_claims,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str | Any) -> str:
    """
    Genera un JWT de refresco con mayor tiempo de vida.

    Args:
        subject: Identificador del usuario (UUID como string).
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str, expected_type: str = "access") -> dict:
    """
    Decodifica y valida un JWT.

    Args:
        token:         El token JWT a decodificar.
        expected_type: Tipo esperado del token ("access" o "refresh").

    Returns:
        El payload del token como diccionario.

    Raises:
        UnauthorizedException: Si el token es inválido, expirado o del tipo incorrecto.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        if payload.get("type") != expected_type:
            raise UnauthorizedException("Tipo de token inválido.")
        return payload
    except JWTError:
        raise UnauthorizedException("Token inválido o expirado.")
