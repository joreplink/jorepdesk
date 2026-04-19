"""crear tablas iniciales

Revision ID: 001_initial
Revises:
Create Date: 2026-04-18

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ── usuarios ─────────────────────────────────────────────────────────────
    op.create_table(
        "usuarios",
        sa.Column("id", mysql.CHAR(36), primary_key=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("apellido", sa.String(100), nullable=False),
        sa.Column("email", sa.String(150), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "rol",
            sa.Enum("admin", "agente", name="rol_usuario"),
            nullable=False,
        ),
        sa.Column("cargo", sa.String(100), nullable=True),
        sa.Column("telefono", sa.String(20), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("creado_en", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "actualizado_en",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.UniqueConstraint("email", name="uq_usuarios_email"),
    )
    op.create_index("idx_usuarios_email",  "usuarios", ["email"])
    op.create_index("idx_usuarios_rol",    "usuarios", ["rol"])
    op.create_index("idx_usuarios_activo", "usuarios", ["activo"])

    # ── tipo_servicios ────────────────────────────────────────────────────────
    op.create_table(
        "tipo_servicios",
        sa.Column("id", mysql.CHAR(36), primary_key=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("creado_en", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "actualizado_en", sa.DateTime(), nullable=False,
            server_default=sa.func.now(), onupdate=sa.func.now(),
        ),
        sa.UniqueConstraint("nombre", name="uq_tipo_servicios_nombre"),
    )
    op.create_index("idx_tipo_servicios_activo", "tipo_servicios", ["activo"])

    # ── areas ────────────────────────────────────────────────────────────────
    op.create_table(
        "areas",
        sa.Column("id", mysql.CHAR(36), primary_key=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("ubicacion", sa.String(200), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("creado_en", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "actualizado_en", sa.DateTime(), nullable=False,
            server_default=sa.func.now(), onupdate=sa.func.now(),
        ),
        sa.UniqueConstraint("nombre", name="uq_areas_nombre"),
    )
    op.create_index("idx_areas_activo", "areas", ["activo"])

    # ── tickets ───────────────────────────────────────────────────────────────
    op.create_table(
        "tickets",
        sa.Column("id", mysql.CHAR(36), primary_key=True),
        sa.Column("numero", sa.String(20), nullable=False),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column(
            "estado",
            sa.Enum("abierto", "en_proceso", "cerrado", name="estado_ticket"),
            nullable=False, server_default="abierto",
        ),
        sa.Column(
            "prioridad",
            sa.Enum("baja", "media", "alta", "critica", name="prioridad_ticket"),
            nullable=False, server_default="media",
        ),
        sa.Column("nombre_reportante", sa.String(150), nullable=False),
        sa.Column("telefono_reportante", sa.String(20), nullable=True),
        sa.Column("creado_por_id", mysql.CHAR(36), nullable=False),
        sa.Column("tipo_servicio_id", mysql.CHAR(36), nullable=False),
        sa.Column("area_id", mysql.CHAR(36), nullable=False),
        sa.Column("creado_en", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "actualizado_en", sa.DateTime(), nullable=False,
            server_default=sa.func.now(), onupdate=sa.func.now(),
        ),
        sa.Column("cerrado_en", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("numero", name="uq_tickets_numero"),
        sa.ForeignKeyConstraint(
            ["creado_por_id"], ["usuarios.id"],
            name="fk_tickets_creado_por", onupdate="CASCADE", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tipo_servicio_id"], ["tipo_servicios.id"],
            name="fk_tickets_tipo_servicio", onupdate="CASCADE", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["area_id"], ["areas.id"],
            name="fk_tickets_area", onupdate="CASCADE", ondelete="RESTRICT",
        ),
    )
    op.create_index("idx_tickets_numero",        "tickets", ["numero"])
    op.create_index("idx_tickets_estado",        "tickets", ["estado"])
    op.create_index("idx_tickets_prioridad",     "tickets", ["prioridad"])
    op.create_index("idx_tickets_creado_por",    "tickets", ["creado_por_id"])
    op.create_index("idx_tickets_tipo_servicio", "tickets", ["tipo_servicio_id"])
    op.create_index("idx_tickets_area",          "tickets", ["area_id"])
    op.create_index("idx_tickets_creado_en",     "tickets", ["creado_en"])
    op.create_index("idx_tickets_cerrado_en",    "tickets", ["cerrado_en"])
    op.create_index("idx_tickets_estado_area",   "tickets", ["estado", "area_id"])
    op.create_index("idx_tickets_estado_tipo",   "tickets", ["estado", "tipo_servicio_id"])

    # ── ticket_agentes ────────────────────────────────────────────────────────
    op.create_table(
        "ticket_agentes",
        sa.Column("id", mysql.CHAR(36), primary_key=True),
        sa.Column("ticket_id", mysql.CHAR(36), nullable=False),
        sa.Column("agente_id", mysql.CHAR(36), nullable=False),
        sa.Column("asignado_por_id", mysql.CHAR(36), nullable=False),
        sa.Column("asignado_en", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint(
            "ticket_id", "agente_id", "activo", name="uq_ticket_agente_activo"
        ),
        sa.ForeignKeyConstraint(
            ["ticket_id"], ["tickets.id"],
            name="fk_ta_ticket", onupdate="CASCADE", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["agente_id"], ["usuarios.id"],
            name="fk_ta_agente", onupdate="CASCADE", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["asignado_por_id"], ["usuarios.id"],
            name="fk_ta_asignado_por", onupdate="CASCADE", ondelete="RESTRICT",
        ),
    )
    op.create_index("idx_ta_ticket_id",     "ticket_agentes", ["ticket_id"])
    op.create_index("idx_ta_agente_id",     "ticket_agentes", ["agente_id"])
    op.create_index("idx_ta_activo",        "ticket_agentes", ["activo"])
    op.create_index("idx_ta_agente_activo", "ticket_agentes", ["agente_id", "activo"])

    # ── observaciones ─────────────────────────────────────────────────────────
    op.create_table(
        "observaciones",
        sa.Column("id", mysql.CHAR(36), primary_key=True),
        sa.Column("ticket_id", mysql.CHAR(36), nullable=False),
        sa.Column("agente_id", mysql.CHAR(36), nullable=False),
        sa.Column("contenido", sa.Text(), nullable=False),
        sa.Column("creado_en", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["ticket_id"], ["tickets.id"],
            name="fk_obs_ticket", onupdate="CASCADE", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["agente_id"], ["usuarios.id"],
            name="fk_obs_agente", onupdate="CASCADE", ondelete="RESTRICT",
        ),
    )
    op.create_index("idx_obs_ticket_id", "observaciones", ["ticket_id"])
    op.create_index("idx_obs_agente_id", "observaciones", ["agente_id"])
    op.create_index("idx_obs_creado_en", "observaciones", ["creado_en"])

    # ── evidencias ────────────────────────────────────────────────────────────
    op.create_table(
        "evidencias",
        sa.Column("id", mysql.CHAR(36), primary_key=True),
        sa.Column("ticket_id", mysql.CHAR(36), nullable=False),
        sa.Column("subido_por_id", mysql.CHAR(36), nullable=False),
        sa.Column("nombre_archivo", sa.String(255), nullable=False),
        sa.Column("tipo_archivo", sa.String(100), nullable=False),
        sa.Column("ruta", sa.Text(), nullable=False),
        sa.Column("tamano_bytes", mysql.BIGINT(), nullable=False),
        sa.Column("subido_en", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["ticket_id"], ["tickets.id"],
            name="fk_ev_ticket", onupdate="CASCADE", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["subido_por_id"], ["usuarios.id"],
            name="fk_ev_subido_por", onupdate="CASCADE", ondelete="RESTRICT",
        ),
    )
    op.create_index("idx_ev_ticket_id",   "evidencias", ["ticket_id"])
    op.create_index("idx_ev_subido_por",  "evidencias", ["subido_por_id"])
    op.create_index("idx_ev_tipo_archivo","evidencias", ["tipo_archivo"])

    # ── historial_estados ─────────────────────────────────────────────────────
    op.create_table(
        "historial_estados",
        sa.Column("id", mysql.CHAR(36), primary_key=True),
        sa.Column("ticket_id", mysql.CHAR(36), nullable=False),
        sa.Column("cambiado_por_id", mysql.CHAR(36), nullable=False),
        sa.Column(
            "estado_anterior",
            sa.Enum("abierto", "en_proceso", "cerrado", name="estado_ticket_historial_ant"),
            nullable=False,
        ),
        sa.Column(
            "estado_nuevo",
            sa.Enum("abierto", "en_proceso", "cerrado", name="estado_ticket_historial_new"),
            nullable=False,
        ),
        sa.Column("cambiado_en", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "estado_anterior <> estado_nuevo",
            name="chk_historial_estados_distintos",
        ),
        sa.ForeignKeyConstraint(
            ["ticket_id"], ["tickets.id"],
            name="fk_he_ticket", onupdate="CASCADE", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["cambiado_por_id"], ["usuarios.id"],
            name="fk_he_cambiado_por", onupdate="CASCADE", ondelete="RESTRICT",
        ),
    )
    op.create_index("idx_he_ticket_id",    "historial_estados", ["ticket_id"])
    op.create_index("idx_he_cambiado_en",  "historial_estados", ["cambiado_en"])
    op.create_index("idx_he_estado_nuevo", "historial_estados", ["estado_nuevo"])

    # ── reportes ──────────────────────────────────────────────────────────────
    op.create_table(
        "reportes",
        sa.Column("id", mysql.CHAR(36), primary_key=True),
        sa.Column("generado_por_id", mysql.CHAR(36), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum("por_tipo_servicio", "por_area", "por_agente", name="tipo_reporte"),
            nullable=False,
        ),
        sa.Column("filtro_id", mysql.CHAR(36), nullable=True),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_fin", sa.Date(), nullable=False),
        sa.Column("generado_en", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("fecha_inicio <= fecha_fin", name="chk_reportes_fechas"),
        sa.ForeignKeyConstraint(
            ["generado_por_id"], ["usuarios.id"],
            name="fk_rep_generado_por", onupdate="CASCADE", ondelete="RESTRICT",
        ),
    )
    op.create_index("idx_rep_generado_por", "reportes", ["generado_por_id"])
    op.create_index("idx_rep_tipo",         "reportes", ["tipo"])
    op.create_index("idx_rep_filtro_id",    "reportes", ["filtro_id"])
    op.create_index("idx_rep_fecha_inicio", "reportes", ["fecha_inicio"])
    op.create_index("idx_rep_generado_en",  "reportes", ["generado_en"])

    # ── Trigger: auto-número de ticket ────────────────────────────────────────
    op.execute("""
        CREATE TRIGGER trg_tickets_numero
        BEFORE INSERT ON tickets
        FOR EACH ROW
        BEGIN
            DECLARE next_num INT;
            SELECT COALESCE(MAX(CAST(SUBSTRING(numero, 5) AS UNSIGNED)), 0) + 1
              INTO next_num
              FROM tickets;
            SET NEW.numero = CONCAT('TKT-', LPAD(next_num, 5, '0'));
        END
    """)

    # ── Vistas para reportes ──────────────────────────────────────────────────
    op.execute("""
        CREATE VIEW v_tickets_con_agentes AS
        SELECT
            t.id AS ticket_id, t.numero, t.titulo, t.estado, t.prioridad,
            t.creado_en, t.cerrado_en,
            ts.nombre AS tipo_servicio,
            a.nombre  AS area,
            u.id      AS agente_id,
            CONCAT(u.nombre, ' ', u.apellido) AS agente_nombre,
            ta.asignado_en
        FROM tickets t
        JOIN tipo_servicios ts ON t.tipo_servicio_id = ts.id
        JOIN areas a           ON t.area_id = a.id
        LEFT JOIN ticket_agentes ta ON ta.ticket_id = t.id AND ta.activo = 1
        LEFT JOIN usuarios u        ON u.id = ta.agente_id
    """)

    op.execute("""
        CREATE VIEW v_resumen_por_agente AS
        SELECT
            u.id AS agente_id,
            CONCAT(u.nombre, ' ', u.apellido) AS agente,
            COUNT(ta.id)                       AS total_asignados,
            SUM(t.estado = 'abierto')          AS abiertos,
            SUM(t.estado = 'en_proceso')       AS en_proceso,
            SUM(t.estado = 'cerrado')          AS cerrados,
            AVG(TIMESTAMPDIFF(HOUR, t.creado_en, t.cerrado_en)) AS promedio_horas_cierre
        FROM usuarios u
        JOIN ticket_agentes ta ON ta.agente_id = u.id AND ta.activo = 1
        JOIN tickets t         ON t.id = ta.ticket_id
        WHERE u.rol = 'agente'
        GROUP BY u.id, u.nombre, u.apellido
    """)

    op.execute("""
        CREATE VIEW v_resumen_por_area AS
        SELECT
            a.id AS area_id, a.nombre AS area,
            COUNT(t.id)                AS total_tickets,
            SUM(t.estado = 'abierto') AS abiertos,
            SUM(t.estado = 'en_proceso') AS en_proceso,
            SUM(t.estado = 'cerrado')    AS cerrados,
            AVG(TIMESTAMPDIFF(HOUR, t.creado_en, t.cerrado_en)) AS promedio_horas_cierre
        FROM areas a
        LEFT JOIN tickets t ON t.area_id = a.id
        GROUP BY a.id, a.nombre
    """)

    op.execute("""
        CREATE VIEW v_resumen_por_tipo_servicio AS
        SELECT
            ts.id AS tipo_servicio_id, ts.nombre AS tipo_servicio,
            COUNT(t.id)                  AS total_tickets,
            SUM(t.estado = 'abierto')    AS abiertos,
            SUM(t.estado = 'en_proceso') AS en_proceso,
            SUM(t.estado = 'cerrado')    AS cerrados,
            AVG(TIMESTAMPDIFF(HOUR, t.creado_en, t.cerrado_en)) AS promedio_horas_cierre
        FROM tipo_servicios ts
        LEFT JOIN tickets t ON t.tipo_servicio_id = ts.id
        GROUP BY ts.id, ts.nombre
    """)


def downgrade() -> None:
    # Elimina en orden inverso (respetando FKs)
    op.execute("DROP VIEW IF EXISTS v_resumen_por_tipo_servicio")
    op.execute("DROP VIEW IF EXISTS v_resumen_por_area")
    op.execute("DROP VIEW IF EXISTS v_resumen_por_agente")
    op.execute("DROP VIEW IF EXISTS v_tickets_con_agentes")
    op.execute("DROP TRIGGER IF EXISTS trg_tickets_numero")

    op.drop_table("reportes")
    op.drop_table("historial_estados")
    op.drop_table("evidencias")
    op.drop_table("observaciones")
    op.drop_table("ticket_agentes")
    op.drop_table("tickets")
    op.drop_table("areas")
    op.drop_table("tipo_servicios")
    op.drop_table("usuarios")
