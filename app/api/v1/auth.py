from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    RefreshResponse,
    MeResponse,
)
from app.schemas.usuario import UsuarioOut
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Autentica al usuario con email y contraseña. Retorna access token, refresh token y datos del usuario.",
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(data)


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Renovar access token",
    description="Usa el refresh token para obtener un nuevo access token sin volver a hacer login.",
)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return AuthService(db).refresh(data.refresh_token)


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Datos del usuario autenticado",
    description="Retorna la información del usuario que está haciendo la petición.",
)
def me(current_user=Depends(get_current_user)):
    return MeResponse(user=UsuarioOut.model_validate(current_user))
