from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from app.core.config import get_settings
from app.db.session import check_db_connection

settings = get_settings()


# ── Lifespan (startup / shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Eventos de ciclo de vida de la aplicación.
    Código antes del yield: se ejecuta al iniciar.
    Código después del yield: se ejecuta al cerrar.
    """
    # Startup
    print(f"\n{'='*50}")
    print(f"  {settings.app_name} v{settings.app_version}")
    print(f"  Entorno: {settings.app_env}")
    print(f"{'='*50}")

    if check_db_connection():
        print("  ✓ Conexión a base de datos: OK")
    else:
        print("  ✗ Conexión a base de datos: FALLÓ")
        print("  Verifica las variables DB_* en tu archivo .env")

    # Crea el directorio de media si no existe
    os.makedirs(settings.media_dir, exist_ok=True)
    print(f"  ✓ Directorio de archivos: {settings.media_dir}")
    print(f"{'='*50}\n")

    yield

    # Shutdown
    print("\nAplicación cerrada.")


# ── Instancia FastAPI ─────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## HelpDesk API

Sistema de gestión de tickets para soporte técnico.

### Roles
- **Administrador**: Crea tickets, asigna agentes, gestiona catálogos y genera reportes.
- **Agente**: Ve sus tickets asignados, cambia estados y agrega observaciones/evidencias.

### Autenticación
Todos los endpoints (excepto `/auth/login`) requieren un JWT en el header:
```
Authorization: Bearer <token>
```
    """,
    lifespan=lifespan,
    # Deshabilita docs en producción
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)


# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Manejo global de excepciones ─────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Captura cualquier excepción no manejada y retorna un 500 limpio."""
    if settings.is_development:
        # En desarrollo muestra el error completo
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error interno: {str(exc)}"},
        )
    # En producción no expone detalles del error
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor."},
    )


# ── Archivos estáticos (evidencias) ──────────────────────────────────────────
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")


# ── Routers ──────────────────────────────────────────────────────────────────
from app.api.v1 import auth
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

from app.api.v1 import catalogos
app.include_router(catalogos.router, prefix="/api/v1", tags=["Catálogos"])
from app.api.v1 import usuarios
app.include_router(usuarios.router, prefix="/api/v1", tags=["Usuarios"])
from app.api.v1 import tickets
app.include_router(tickets.router, prefix="/api/v1", tags=["Tickets"])
from app.api.v1 import observaciones, evidencias
app.include_router(observaciones.router, prefix="/api/v1", tags=["Observaciones"])
app.include_router(evidencias.router, prefix="/api/v1", tags=["Evidencias"])
from app.api.v1 import reportes
app.include_router(reportes.router, prefix="/api/v1", tags=["Reportes"])


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["Sistema"])
def health_check():
    """Verifica que la API esté corriendo. Útil para monitoreo."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
    }
