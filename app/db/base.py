from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    Clase base para todos los modelos SQLAlchemy.
    Todos los modelos deben heredar de esta clase.

    Uso:
        from app.db.base import Base

        class MiModelo(Base):
            __tablename__ = "mi_tabla"
            ...
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Genera el nombre de tabla automáticamente en snake_case
        a partir del nombre de la clase.
        Ejemplo: TipoServicio → tipo_servicio
        Se puede sobreescribir en cada modelo.
        """
        import re
        name = cls.__name__
        # Inserta _ antes de mayúsculas y convierte a minúsculas
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower() + "s"
