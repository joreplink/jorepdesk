from pydantic import BaseModel, EmailStr
from app.schemas.usuario import UsuarioOut


class LoginRequest(BaseModel):
    """Body del POST /auth/login."""
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "admin@helpdesk.com",
                "password": "password123",
            }
        }
    }


class TokenResponse(BaseModel):
    """Respuesta del login exitoso."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UsuarioOut


class RefreshRequest(BaseModel):
    """Body del POST /auth/refresh."""
    refresh_token: str


class RefreshResponse(BaseModel):
    """Respuesta del refresh exitoso."""
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    """Respuesta del GET /auth/me — datos del usuario autenticado."""
    user: UsuarioOut
