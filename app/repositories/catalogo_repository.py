from sqlalchemy.orm import Session
from app.models.tipo_servicio import TipoServicio
from app.models.area import Area


# ══════════════════════════════════════════════════════
#  TIPO SERVICIO REPOSITORY
# ══════════════════════════════════════════════════════

class TipoServicioRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, tipo_id: str) -> TipoServicio | None:
        return self.db.get(TipoServicio, tipo_id)

    def get_all(self, solo_activos: bool = False) -> list[TipoServicio]:
        query = self.db.query(TipoServicio)
        if solo_activos:
            query = query.filter(TipoServicio.activo == True)
        return query.order_by(TipoServicio.nombre).all()

    def get_by_nombre(self, nombre: str, exclude_id: str | None = None) -> TipoServicio | None:
        query = self.db.query(TipoServicio).filter(
            TipoServicio.nombre == nombre.strip()
        )
        if exclude_id:
            query = query.filter(TipoServicio.id != exclude_id)
        return query.first()

    def create(self, tipo: TipoServicio) -> TipoServicio:
        self.db.add(tipo)
        self.db.flush()
        self.db.refresh(tipo)
        return tipo

    def update(self, tipo: TipoServicio) -> TipoServicio:
        self.db.flush()
        self.db.refresh(tipo)
        return tipo

    def tiene_tickets(self, tipo_id: str) -> bool:
        """Verifica si el tipo de servicio tiene tickets asociados."""
        from app.models.ticket import Ticket
        return (
            self.db.query(Ticket)
            .filter(Ticket.tipo_servicio_id == tipo_id)
            .first() is not None
        )


# ══════════════════════════════════════════════════════
#  AREA REPOSITORY
# ══════════════════════════════════════════════════════

class AreaRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, area_id: str) -> Area | None:
        return self.db.get(Area, area_id)

    def get_all(self, solo_activos: bool = False) -> list[Area]:
        query = self.db.query(Area)
        if solo_activos:
            query = query.filter(Area.activo == True)
        return query.order_by(Area.nombre).all()

    def get_by_nombre(self, nombre: str, exclude_id: str | None = None) -> Area | None:
        query = self.db.query(Area).filter(
            Area.nombre == nombre.strip()
        )
        if exclude_id:
            query = query.filter(Area.id != exclude_id)
        return query.first()

    def create(self, area: Area) -> Area:
        self.db.add(area)
        self.db.flush()
        self.db.refresh(area)
        return area

    def update(self, area: Area) -> Area:
        self.db.flush()
        self.db.refresh(area)
        return area

    def tiene_tickets(self, area_id: str) -> bool:
        """Verifica si el área tiene tickets asociados."""
        from app.models.ticket import Ticket
        return (
            self.db.query(Ticket)
            .filter(Ticket.area_id == area_id)
            .first() is not None
        )
