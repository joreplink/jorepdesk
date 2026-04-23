# HelpDesk API

Sistema de gestión de tickets para soporte técnico.  
**Stack**: FastAPI · SQLAlchemy 2.0 · MySQL 8 · Alembic · Pydantic v2 · JWT

---

## Requisitos

- Python 3.11+
- MySQL 8.0+ o MariaDB 10.6+

---

## Instalación

### 1. Clonar y crear entorno virtual

```bash
git clone <repo>
cd helpdesk-api

python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tus credenciales de base de datos y JWT
```

### 4. Crear la base de datos en MySQL

```sql
CREATE DATABASE helpdesk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'helpdesk_user'@'localhost' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON helpdesk.* TO 'helpdesk_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Ejecutar migraciones

```bash
alembic upgrade head
```

### 6. Iniciar el servidor

```bash
uvicorn app.main:app --reload
```

La API estará disponible en: http://localhost:8000  
Documentación Swagger: http://localhost:8000/docs

---

## Estructura del proyecto

```
helpdesk-api/
├── app/
│   ├── main.py              # Entry point FastAPI
│   ├── api/v1/              # Routers (endpoints)
│   ├── core/
│   │   ├── config.py        # Settings desde .env
│   │   ├── security.py      # JWT + hashing
│   │   ├── dependencies.py  # Dependencias FastAPI (guards)
│   │   └── exceptions.py    # Excepciones HTTP personalizadas
│   ├── db/
│   │   ├── base.py          # Base declarativa SQLAlchemy
│   │   └── session.py       # Engine + SessionLocal + get_db
│   ├── models/              # Modelos ORM (SQLAlchemy)
│   ├── schemas/             # DTOs request/response (Pydantic)
│   ├── services/            # Lógica de negocio
│   └── repositories/        # Acceso a datos
├── alembic/                 # Migraciones de base de datos
├── media/                   # Archivos de evidencia subidos
├── tests/
├── .env.example
├── alembic.ini
└── requirements.txt
```

---

## Comandos útiles

```bash
# Crear nueva migración (después de modificar modelos)
alembic revision --autogenerate -m "descripcion del cambio"

# Aplicar migraciones pendientes
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial de migraciones
alembic history

# Correr tests
pytest tests/ -v

# Health check
curl http://localhost:8000/health
```

---

## Fases de desarrollo

- [ ] **Fase 1** — Configuración base (config, DB, seguridad, estructura)
- [ ] **Fase 2** — Modelos ORM + primera migración Alembic
- [ ] **Fase 3** — Autenticación JWT (login, refresh, guards)
- [ ] **Fase 4** — Catálogos (TipoServicio, Area)
- [x] **Fase 5** — Usuarios / Agentes
- [ ] **Fase 6** — Tickets (crear, asignar, reasignar, cambiar estado)
- [ ] **Fase 7** — Observaciones y Evidencias
- [ ] **Fase 8** — Reportes y exportación
