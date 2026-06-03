from datetime import datetime
import os

from flask import Flask, render_template, request, jsonify, send_file
from database import (
    init_db,
    add_gps,
    add_llaves,
    list_gps,
    list_llaves,
    delete_gps,
    delete_llaves,
    get_gps_for_pdf,
    get_llaves_for_pdf,
)
from pdf_export import export_gps_pdf, export_llaves_pdf

app = Flask(__name__)
init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/gps/<empresa>", methods=["GET"])
def api_list_gps(empresa):
    if empresa not in ("mavi", "tei"):
        return jsonify({"error": "Empresa no válida"}), 400
    return jsonify(list_gps(empresa))


@app.route("/api/gps/<empresa>", methods=["POST"])
def api_add_gps(empresa):
    if empresa not in ("mavi", "tei"):
        return jsonify({"error": "Empresa no válida"}), 400
    data = request.get_json() or {}
    required = ["codigo", "ubicacion", "distancia", "marca", "modelo", "patente", "fecha"]
    for field in required:
        if not data.get(field) and data.get(field) != 0:
            return jsonify({"error": f"Falta el campo: {field}"}), 400
    try:
        distancia = float(data["distancia"])
        if distancia < 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "Distancia inválida"}), 400

    row_id = add_gps(
        empresa=empresa,
        codigo=str(data["codigo"]).strip(),
        ubicacion=str(data["ubicacion"]).strip(),
        distancia=distancia,
        marca=str(data["marca"]).strip(),
        modelo=str(data["modelo"]).strip(),
        patente=str(data["patente"]).strip().upper(),
        fecha=str(data["fecha"]),
        notas=str(data.get("notas", "")).strip(),
    )
    return jsonify({"id": row_id, "message": "Servicio registrado"}), 201


@app.route("/api/gps/<empresa>/<int:record_id>", methods=["DELETE"])
def api_delete_gps(empresa, record_id):
    if empresa not in ("mavi", "tei"):
        return jsonify({"error": "Empresa no válida"}), 400
    if delete_gps(empresa, record_id):
        return jsonify({"message": "Eliminado"})
    return jsonify({"error": "No encontrado"}), 404


@app.route("/api/llaves", methods=["GET"])
def api_list_llaves():
    return jsonify(list_llaves())


@app.route("/api/llaves", methods=["POST"])
def api_add_llaves():
    data = request.get_json() or {}
    required = ["marca", "modelo", "patente", "valor_insumos", "cobro_servicio", "fecha"]
    for field in required:
        if data.get(field) is None or (field != "valor_insumos" and field != "cobro_servicio" and not data.get(field)):
            return jsonify({"error": f"Falta el campo: {field}"}), 400
    try:
        insumos = float(data["valor_insumos"])
        cobro = float(data["cobro_servicio"])
        if insumos < 0 or cobro < 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "Valores monetarios inválidos"}), 400

    row_id = add_llaves(
        marca=str(data["marca"]).strip(),
        modelo=str(data["modelo"]).strip(),
        patente=str(data["patente"]).strip().upper(),
        valor_insumos=insumos,
        cobro_servicio=cobro,
        fecha=str(data["fecha"]),
        notas=str(data.get("notas", "")).strip(),
    )
    ganancia = round(cobro - insumos, 2)
    return jsonify({"id": row_id, "ganancia": ganancia, "message": "Servicio registrado"}), 201


@app.route("/api/llaves/<int:record_id>", methods=["DELETE"])
def api_delete_llaves(record_id):
    if delete_llaves(record_id):
        return jsonify({"message": "Eliminado"})
    return jsonify({"error": "No encontrado"}), 404


def _parse_mes_anio():
    now = datetime.now()
    try:
        mes = int(request.args.get("mes", now.month))
        anio = int(request.args.get("anio", now.year))
    except (TypeError, ValueError):
        return None, None
    if mes < 1 or mes > 12 or anio < 2000 or anio > 2100:
        return None, None
    return anio, mes


@app.route("/api/pdf/<empresa>")
def api_pdf(empresa):
    anio, mes = _parse_mes_anio()
    if anio is None:
        return jsonify({"error": "Mes o año inválido"}), 400

    periodo = f"{anio}-{mes:02d}"
    if empresa == "mavi":
        records = get_gps_for_pdf("mavi", anio, mes)
        buffer = export_gps_pdf("mavi", records, anio, mes)
        filename = f"reporte_mavi_gps_{periodo}.pdf"
    elif empresa == "tei":
        records = get_gps_for_pdf("tei", anio, mes)
        buffer = export_gps_pdf("tei", records, anio, mes)
        filename = f"reporte_tei_gps_{periodo}.pdf"
    elif empresa == "egana":
        records = get_llaves_for_pdf(anio, mes)
        buffer = export_llaves_pdf(records, anio, mes)
        filename = f"reporte_egana_llaves_{periodo}.pdf"
    else:
        return jsonify({"error": "Empresa no válida"}), 400

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    print("\n  Gestión de servicios — GPS y Llaves")
    print(f"  Abra en el navegador: http://127.0.0.1:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
