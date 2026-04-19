"""
Script para crear el usuario administrador inicial.

Uso:
    python seed_admin.py

Ejecutar UNA sola vez después de aplicar las migraciones.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.models.usuario import Usuario
from app.core.security import hash_password
import uuid


def crear_admin():
    db = SessionLocal()
    try:
        # Verifica si ya existe
        existe = db.query(Usuario).filter(Usuario.rol == "admin").first()
        if existe:
            print(f"✓ Ya existe un admin: {existe.email}")
            return

        admin = Usuario(
            id=str(uuid.uuid4()),
            nombre="Administrador",
            apellido="HelpDesk",
            email="admin@helpdesk.com",
            password_hash=hash_password("Admin123!"),
            rol="admin",
            activo=True,
        )
        db.add(admin)
        db.commit()

        print("✓ Usuario admin creado exitosamente")
        print(f"  Email   : admin@helpdesk.com")
        print(f"  Password: Admin123!")
        print(f"\n  ⚠️  Cambia la contraseña después del primer login.")

    except Exception as e:
        db.rollback()
        print(f"✗ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    crear_admin()
