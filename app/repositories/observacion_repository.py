from sqlalchemy.orm import Session, joinedload
from app.models.observacion import Observacion


class ObservacionRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_ticket(self, ticket_id: str) -> list[Observacion]:
        return (
            self.db.query(Observacion)
            .options(joinedload(Observacion.agente))
            .filter(Observacion.ticket_id == ticket_id)
            .order_by(Observacion.creado_en.asc())
            .all()
        )

    def create(self, observacion: Observacion) -> Observacion:
        self.db.add(observacion)
        self.db.flush()
        self.db.refresh(observacion)
        # Recarga con relaciones
        return (
            self.db.query(Observacion)
            .options(joinedload(Observacion.agente))
            .filter(Observacion.id == observacion.id)
            .first()
        )
