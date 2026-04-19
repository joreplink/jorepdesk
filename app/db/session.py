from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import get_settings

settings = get_settings()

# ── Engine ───────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.database_url,
    # Pool de conexiones
    pool_size=10,           # conexiones activas permanentes
    max_overflow=20,        # conexiones extra permitidas bajo carga
    pool_pre_ping=True,     # verifica que la conexión siga viva antes de usarla
    pool_recycle=3600,      # recicla conexiones cada hora (evita timeouts de MySQL)
    echo=settings.is_development,  # loggea SQL en desarrollo
)


# ── Session factory ──────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,   # control manual de transacciones
    autoflush=False,    # no hace flush automático antes de queries
    expire_on_commit=False,  # los objetos no expiran al hacer commit
)


# ── Dependency para FastAPI ──────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    Dependencia de FastAPI que provee una sesión de base de datos
    y garantiza que se cierre al terminar cada request.

    Uso en routers:
        @router.get("/endpoint")
        def mi_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Verifica que la conexión a la base de datos funcione.
    Útil en el startup de la aplicación.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[DB] Error de conexión: {e}")
        return False
