from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.schemas.reporte import ReporteParams, ReporteOut
from app.services.reporte_service import ReporteService

router = APIRouter()


@router.get(
    "/reportes",
    response_model=list[ReporteOut],
    summary="Listar reportes generados",
    description="Solo administradores. Retorna todos los reportes sin métricas detalladas.",
)
def listar_reportes(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return ReporteService(db).get_all()


@router.get(
    "/reportes/{reporte_id}",
    response_model=ReporteOut,
    summary="Ver reporte con métricas",
    description="Retorna el reporte con sus métricas calculadas al momento de la consulta.",
)
def obtener_reporte(
    reporte_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return ReporteService(db).get_by_id(reporte_id)


@router.post(
    "/reportes",
    response_model=ReporteOut,
    status_code=201,
    summary="Generar reporte",
    description=(
        "Genera y persiste un reporte con métricas. "
        "Tipos disponibles: por_area, por_tipo_servicio, por_agente. "
        "filtro_id es opcional — si se omite, incluye todos."
    ),
)
def generar_reporte(
    params: ReporteParams,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return ReporteService(db).generar(params, current_user)


@router.get(
    "/reportes/{reporte_id}/exportar/pdf",
    summary="Exportar reporte a PDF",
    description="Descarga el reporte como archivo PDF.",
    response_class=Response,
)
def exportar_pdf(
    reporte_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    pdf_bytes = ReporteService(db).exportar_pdf(reporte_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=reporte_{reporte_id[:8]}.pdf"
        },
    )


@router.get(
    "/reportes/{reporte_id}/exportar/excel",
    summary="Exportar reporte a Excel",
    description="Descarga el reporte como archivo XLSX.",
    response_class=Response,
)
def exportar_excel(
    reporte_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    xlsx_bytes = ReporteService(db).exportar_xlsx(reporte_id)
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=reporte_{reporte_id[:8]}.xlsx"
        },
    )
