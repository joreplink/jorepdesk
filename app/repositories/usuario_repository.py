from sqlalchemy.orm import Session
from app.models.usuario import Usuario


class UsuarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, usuario_id: str) -> Usuario | None:
        return self.db.get(Usuario, usuario_id)

    def get_by_email(self, email: str) -> Usuario | None:
        return (
            self.db.query(Usuario)
            .filter(Usuario.email == email.lower().strip())
            .first()
        )

    def get_all(self, solo_activos: bool = True) -> list[Usuario]:
        query = self.db.query(Usuario)
        if solo_activos:
            query = query.filter(Usuario.activo == True)
        return query.order_by(Usuario.nombre).all()

    def get_agentes(self, solo_activos: bool = True) -> list[Usuario]:
        query = self.db.query(Usuario).filter(Usuario.rol == "agente")
        if solo_activos:
            query = query.filter(Usuario.activo == True)
        return query.order_by(Usuario.nombre).all()

    def create(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.flush()   # obtiene el id sin hacer commit
        self.db.refresh(usuario)
        return usuario

    def update(self, usuario: Usuario) -> Usuario:
        self.db.flush()
        self.db.refresh(usuario)
        return usuario

    def email_exists(self, email: str, exclude_id: str | None = None) -> bool:
        query = self.db.query(Usuario).filter(
            Usuario.email == email.lower().strip()
        )
        if exclude_id:
            query = query.filter(Usuario.id != exclude_id)
        return query.first() is not None
