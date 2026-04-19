from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración central de la aplicación.
    Lee variables desde el archivo .env automáticamente.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Aplicación ──────────────────────────────────────
    app_name: str = "HelpDesk API"
    app_version: str = "1.0.0"
    app_env: str = "development"

    # ── Base de datos ───────────────────────────────────
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "helpdesk"
    db_user: str = "root"
    db_password: str = ""

    # ── JWT ─────────────────────────────────────────────
    secret_key: str = "cambia_esta_clave"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # ── CORS ────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173"

    # ── Archivos ────────────────────────────────────────
    media_dir: str = "./media"
    max_file_size_mb: int = 10
    allowed_mime_types: str = "image/jpeg,image/png,image/gif,image/webp,application/pdf"

    # ── Propiedades calculadas ───────────────────────────

    @property
    def database_url(self) -> str:
        """URL de conexión para SQLAlchemy."""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?charset=utf8mb4"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        """Convierte el string de orígenes CORS a lista."""
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def allowed_mime_types_list(self) -> list[str]:
        """Convierte el string de MIME types a lista."""
        return [m.strip() for m in self.allowed_mime_types.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        """Tamaño máximo de archivo en bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Retorna la instancia de Settings cacheada.
    Usar como dependencia en FastAPI:
        settings = Depends(get_settings)
    O directamente:
        from app.core.config import get_settings
        settings = get_settings()
    """
    return Settings()
