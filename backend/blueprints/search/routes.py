from flask import Blueprint, current_app, jsonify, request

from ...services import get_store
from ...services.store import parse_bool

search_bp = Blueprint("search", __name__, url_prefix="/api/search")


def _store():
	return get_store(current_app)


@search_bp.get("")
def search_documents():
	query = request.args.get("q", default="", type=str).strip()
	if not query:
		return jsonify(error="El parámetro 'q' es obligatorio"), 400

	filters = {
		"tipo": request.args.get("tipo"),
		"categoria_id": request.args.get("categoria_id", type=int),
		"usuario_id": request.args.get("usuario_id"),
		"publico": parse_bool(request.args.get("publico"), False),
	}
	page = request.args.get("page", default=1, type=int)
	per_page = request.args.get("per_page", default=20, type=int)

	result = _store().search_documents(
		query,
		tipo=filters["tipo"],
		categoria_id=filters["categoria_id"],
		usuario_id=filters["usuario_id"],
		solo_publicos=filters["publico"],
		limite=per_page,
		offset=(page - 1) * per_page,
	)
	_store().record_search(query, total_resultados=result.total, filtros=filters)
	return jsonify(
		query=query,
		filters=filters,
		total=result.total,
		pagination={"page": page, "per_page": per_page},
		results=result.items,
	)


@search_bp.get("/suggestions")
def search_suggestions():
	query = request.args.get("q", default="", type=str).strip()
	limit = request.args.get("limit", default=10, type=int)
	suggestions = _store().search_suggestions(query, limit=limit)
	return jsonify(
		query=query,
		total=len(suggestions),
		suggestions=suggestions,
	)


@search_bp.get("/popular")
def popular_searches():
	limit = request.args.get("limit", default=10, type=int)
	items = _store().popular_terms(limit=limit)
	return jsonify(items=items, total=len(items))


