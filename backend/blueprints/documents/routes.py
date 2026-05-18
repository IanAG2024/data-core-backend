from __future__ import annotations

import json

from uuid import UUID, uuid4

from flask import Blueprint, current_app, jsonify, request

from ...services import get_store
from ...services.files import save_uploaded_file
from ...services.store import parse_bool, parse_json_list

documents_bp = Blueprint("documents", __name__, url_prefix="/api/documents")


def _store():
	return get_store(current_app)


def _parse_payload() -> dict:
	if request.is_json:
		data = request.get_json(silent=True) or {}
	else:
		data = request.form.to_dict(flat=True)

	if "categoria_id" in data and data["categoria_id"] not in (None, ""):
		try:
			data["categoria_id"] = int(data["categoria_id"])
		except (TypeError, ValueError):
			data["categoria_id"] = None
	else:
		data["categoria_id"] = None

	if "usuario_id" in data and data["usuario_id"] == "":
		data["usuario_id"] = None

	data["es_publico"] = parse_bool(data.get("es_publico"), False)
	metadatos = data.get("metadatos")
	if isinstance(metadatos, str) and metadatos.strip():
		try:
			metadatos = json.loads(metadatos)
		except json.JSONDecodeError:
			metadatos = {}
	data["metadatos"] = metadatos
	data["etiquetas"] = parse_json_list(data.get("etiquetas"))
	data["palabras_clave"] = parse_json_list(data.get("palabras_clave"))
	return data


@documents_bp.get("")
def list_documents():
	page = request.args.get("page", default=1, type=int)
	per_page = request.args.get("per_page", default=20, type=int)
	query = request.args.get("q", default="", type=str).strip() or None
	tipo = request.args.get("tipo")
	categoria_id = request.args.get("categoria_id", type=int)
	usuario_id = request.args.get("usuario_id")
	solo_publicos = parse_bool(request.args.get("publico"), False)

	result = _store().list_documents(
		page=page,
		per_page=per_page,
		query=query,
		tipo=tipo,
		categoria_id=categoria_id,
		usuario_id=usuario_id,
		solo_publicos=solo_publicos,
	)
	return jsonify(
		items=result.items,
		total=result.total,
		pagination={
			"page": page,
			"per_page": per_page,
			"pages": max((result.total + per_page - 1) // per_page, 1),
		},
		query=query,
	)


@documents_bp.get("/<document_id>")
def get_document(document_id: str):
	try:
		UUID(document_id)
	except ValueError:
		return jsonify(error="document_id inválido"), 400

	document = _store().get_document(document_id)
	if not document:
		return jsonify(error="documento no encontrado"), 404
	return jsonify(document=document)


@documents_bp.post("")
def create_document():
	payload = _parse_payload()
	upload = request.files.get("file")
	try:
		document_id = str(UUID(str(payload.get("id")))) if payload.get("id") else str(uuid4())
	except (TypeError, ValueError):
		document_id = str(uuid4())
	payload["id"] = document_id

	if upload and upload.filename:
		file_info = save_uploaded_file(upload, current_app.config["UPLOAD_FOLDER"], document_id)
		payload.update(file_info)
		payload.setdefault("ruta_almacenamiento", file_info["ruta_almacenamiento"])
		payload.setdefault("nombre_original", file_info["nombre_original"])
		payload.setdefault("extension", file_info["extension"])
		payload.setdefault("mime_type", file_info["mime_type"])
		payload.setdefault("tamano_bytes", file_info["tamano_bytes"])
		payload.setdefault("hash_sha256", file_info["hash_sha256"])

	missing = [field for field in ("titulo", "tipo") if not payload.get(field)]
	if missing:
		return jsonify(error="Faltan campos obligatorios", missing=missing), 400

	payload.setdefault("nombre_original", payload["titulo"])
	document = _store().create_document(payload)
	return jsonify(document=document), 201


@documents_bp.put("/<document_id>")
def update_document(document_id: str):
	try:
		UUID(document_id)
	except ValueError:
		return jsonify(error="document_id inválido"), 400

	payload = _parse_payload()
	document = _store().update_document(document_id, payload)
	if not document:
		return jsonify(error="documento no encontrado"), 404
	return jsonify(document=document)


@documents_bp.delete("/<document_id>")
def delete_document(document_id: str):
	try:
		UUID(document_id)
	except ValueError:
		return jsonify(error="document_id inválido"), 400

	deleted = _store().delete_document(document_id)
	if not deleted:
		return jsonify(error="documento no encontrado"), 404
	return jsonify(message="documento eliminado")


@documents_bp.post("/<document_id>/access")
def record_access(document_id: str):
	try:
		UUID(document_id)
	except ValueError:
		return jsonify(error="document_id inválido"), 400

	payload = request.get_json(silent=True) or {}
	ok = _store().record_access(
		document_id,
		usuario_id=payload.get("usuario_id"),
		accion=payload.get("accion", "visualizar"),
	)
	if not ok:
		return jsonify(error="documento no encontrado"), 404
	return jsonify(message="acceso registrado", document_id=document_id)




