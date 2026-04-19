from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Recurso no encontrado — 404."""
    def __init__(self, resource: str = "Recurso"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} no encontrado.",
        )


class UnauthorizedException(HTTPException):
    """No autenticado — 401."""
    def __init__(self, detail: str = "No autenticado. Inicia sesión."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(HTTPException):
    """Sin permisos suficientes — 403."""
    def __init__(self, detail: str = "No tienes permisos para esta acción."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class ConflictException(HTTPException):
    """Conflicto con el estado actual — 409."""
    def __init__(self, detail: str = "Conflicto con el estado actual del recurso."):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class BadRequestException(HTTPException):
    """Petición mal formada — 400."""
    def __init__(self, detail: str = "Petición inválida."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class UnprocessableException(HTTPException):
    """Error de validación de negocio — 422."""
    def __init__(self, detail: str = "No se puede procesar la solicitud."):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )
