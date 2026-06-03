from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

EMPRESA_TITLES = {
    "mavi": "Mavi GPS",
    "tei": "Tei GPS",
    "egana": "Egaña Automotriz — Servicios de Llaves",
}

MESES_ES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def _period_label(anio, mes):
    return f"{MESES_ES[mes]} {anio}"


def _build_doc(buffer, title, anio, mes, landscape_mode=False):
    pagesize = landscape(A4) if landscape_mode else A4
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=6,
        textColor=colors.HexColor("#1e3a5f"),
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=12,
    )
    periodo = _period_label(anio, mes)
    elements = [
        Paragraph(title, title_style),
        Paragraph(f"Período: <b>{periodo}</b>", subtitle_style),
        Paragraph(
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            subtitle_style,
        ),
        Spacer(1, 0.3 * cm),
    ]
    return doc, elements, styles


def export_gps_pdf(empresa, records, anio, mes):
    buffer = BytesIO()
    title = f"Reporte mensual — {EMPRESA_TITLES[empresa]}"
    doc, elements, _ = _build_doc(buffer, title, anio, mes, landscape_mode=True)

    if not records:
        elements.append(
            Paragraph(
                f"No hay registros en {_period_label(anio, mes)}.",
                getSampleStyleSheet()["Normal"],
            )
        )
    else:
        data = [
            [
                "Fecha",
                "Código",
                "Ubicación",
                "Dist. (km)",
                "Marca",
                "Modelo",
                "Patente",
            ]
        ]
        total_dist = 0
        for r in records:
            data.append(
                [
                    r["fecha"],
                    r["codigo"],
                    r["ubicacion"][:40] + ("…" if len(r["ubicacion"]) > 40 else ""),
                    f"{r['distancia']:.1f}",
                    r["marca"],
                    r["modelo"],
                    r["patente"],
                ]
            )
            total_dist += r["distancia"]

        data.append(["", "", "TOTAL KM", f"{total_dist:.1f}", "", "", f"{len(records)} serv."])

        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("ALIGN", (2, 1), (2, -2), "LEFT"),
                    ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f0f4f8")]),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8eef4")),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def export_llaves_pdf(records, anio, mes):
    buffer = BytesIO()
    title = f"Reporte mensual — {EMPRESA_TITLES['egana']}"
    doc, elements, _ = _build_doc(buffer, title, anio, mes, landscape_mode=True)

    if not records:
        elements.append(
            Paragraph(
                f"No hay registros en {_period_label(anio, mes)}.",
                getSampleStyleSheet()["Normal"],
            )
        )
    else:
        data = [
            [
                "Fecha",
                "Marca",
                "Modelo",
                "Patente",
                "Insumos ($)",
                "Cobro ($)",
                "Ganancia ($)",
            ]
        ]
        total_insumos = 0
        total_cobro = 0
        total_ganancia = 0
        for r in records:
            ganancia = r["cobro_servicio"] - r["valor_insumos"]
            data.append(
                [
                    r["fecha"],
                    r["marca"],
                    r["modelo"],
                    r["patente"],
                    f"{r['valor_insumos']:,.0f}",
                    f"{r['cobro_servicio']:,.0f}",
                    f"{ganancia:,.0f}",
                ]
            )
            total_insumos += r["valor_insumos"]
            total_cobro += r["cobro_servicio"]
            total_ganancia += ganancia

        data.append(
            [
                "",
                "",
                "TOTALES",
                f"{len(records)} serv.",
                f"{total_insumos:,.0f}",
                f"{total_cobro:,.0f}",
                f"{total_ganancia:,.0f}",
            ]
        )

        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5c2d0e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#faf5f0")]),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f0e6dc")),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
