from sqlalchemy.orm import Session, joinedload
from app.models.evidencia import Evidencia


class EvidenciaRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_ticket(self, ticket_id: str) -> list[Evidencia]:
        return (
            self.db.query(Evidencia)
            .options(joinedload(Evidencia.subido_por))
            .filter(Evidencia.ticket_id == ticket_id)
            .order_by(Evidencia.subido_en.desc())
            .all()
        )

    def create(self, evidencia: Evidencia) -> Evidencia:
        self.db.add(evidencia)
        self.db.flush()
        self.db.refresh(evidencia)
        return (
            self.db.query(Evidencia)
            .options(joinedload(Evidencia.subido_por))
            .filter(Evidencia.id == evidencia.id)
            .first()
        )
