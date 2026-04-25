from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from app.models.reporte import Reporte


class ReporteRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, generado_por_id: str | None = None) -> list[Reporte]:
        query = (
            self.db.query(Reporte)
            .options(joinedload(Reporte.generado_por))
            .order_by(Reporte.generado_en.desc())
        )
        if generado_por_id:
            query = query.filter(Reporte.generado_por_id == generado_por_id)
        return query.all()

    def get_by_id(self, reporte_id: str) -> Reporte | None:
        return (
            self.db.query(Reporte)
            .options(joinedload(Reporte.generado_por))
            .filter(Reporte.id == reporte_id)
            .first()
        )

    def create(self, reporte: Reporte) -> Reporte:
        self.db.add(reporte)
        self.db.flush()
        self.db.refresh(reporte)
        return self.get_by_id(reporte.id)

    # ── Consultas para métricas ───────────────────────────────────────────────

    def metricas_por_area(
        self, fecha_inicio: date, fecha_fin: date, area_id: str | None = None
    ) -> list[dict]:
        sql = """
            SELECT
                a.id,
                a.nombre,
                COUNT(t.id)                    AS total,
                SUM(t.estado = 'abierto')      AS abiertos,
                SUM(t.estado = 'en_proceso')   AS en_proceso,
                SUM(t.estado = 'cerrado')      AS cerrados,
                AVG(TIMESTAMPDIFF(HOUR, t.creado_en, t.cerrado_en)) AS promedio_horas_cierre
            FROM areas a
            LEFT JOIN tickets t
                ON t.area_id = a.id
                AND DATE(t.creado_en) BETWEEN :fecha_inicio AND :fecha_fin
            WHERE a.activo = 1
              AND (:area_id IS NULL OR a.id = :area_id)
            GROUP BY a.id, a.nombre
            ORDER BY total DESC
        """
        rows = self.db.execute(
            text(sql),
            {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "area_id": area_id},
        ).fetchall()
        return [row._mapping for row in rows]

    def metricas_por_tipo_servicio(
        self, fecha_inicio: date, fecha_fin: date, tipo_id: str | None = None
    ) -> list[dict]:
        sql = """
            SELECT
                ts.id,
                ts.nombre,
                COUNT(t.id)                    AS total,
                SUM(t.estado = 'abierto')      AS abiertos,
                SUM(t.estado = 'en_proceso')   AS en_proceso,
                SUM(t.estado = 'cerrado')      AS cerrados,
                AVG(TIMESTAMPDIFF(HOUR, t.creado_en, t.cerrado_en)) AS promedio_horas_cierre
            FROM tipo_servicios ts
            LEFT JOIN tickets t
                ON t.tipo_servicio_id = ts.id
                AND DATE(t.creado_en) BETWEEN :fecha_inicio AND :fecha_fin
            WHERE ts.activo = 1
              AND (:tipo_id IS NULL OR ts.id = :tipo_id)
            GROUP BY ts.id, ts.nombre
            ORDER BY total DESC
        """
        rows = self.db.execute(
            text(sql),
            {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "tipo_id": tipo_id},
        ).fetchall()
        return [row._mapping for row in rows]

    def metricas_por_agente(
        self, fecha_inicio: date, fecha_fin: date, agente_id: str | None = None
    ) -> list[dict]:
        sql = """
            SELECT
                u.id,
                CONCAT(u.nombre, ' ', u.apellido) AS nombre,
                COUNT(DISTINCT ta.ticket_id)       AS total,
                SUM(t.estado = 'abierto')          AS abiertos,
                SUM(t.estado = 'en_proceso')       AS en_proceso,
                SUM(t.estado = 'cerrado')          AS cerrados,
                AVG(TIMESTAMPDIFF(HOUR, t.creado_en, t.cerrado_en)) AS promedio_horas_cierre
            FROM usuarios u
            JOIN ticket_agentes ta ON ta.agente_id = u.id
            JOIN tickets t
                ON t.id = ta.ticket_id
                AND DATE(t.creado_en) BETWEEN :fecha_inicio AND :fecha_fin
            WHERE u.rol = 'agente'
              AND u.activo = 1
              AND (:agente_id IS NULL OR u.id = :agente_id)
            GROUP BY u.id, u.nombre, u.apellido
            ORDER BY total DESC
        """
        rows = self.db.execute(
            text(sql),
            {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "agente_id": agente_id},
        ).fetchall()
        return [row._mapping for row in rows]
