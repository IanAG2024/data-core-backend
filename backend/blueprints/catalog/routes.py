from uuid import UUID

from flask import Blueprint, current_app, jsonify, request

from ...services import get_store

catalog_bp = Blueprint("catalog", __name__, url_prefix="/api")


@catalog_bp.get("/categories")
def list_categories():
    store = get_store(current_app)
    items = store.list_categories()
    return jsonify(items=items, total=len(items))


@catalog_bp.get("/tags")
def list_tags():
    store = get_store(current_app)
    items = store.list_tags()
    return jsonify(items=items, total=len(items))


@catalog_bp.get("/recommendations/<document_id>")
def document_recommendations(document_id: str):
    try:
        UUID(document_id)
    except ValueError:
        return jsonify(error="document_id inválido"), 400

    store = get_store(current_app)
    items = store.recommendations(document_id, limit=request.args.get("limit", default=5, type=int))
    return jsonify(document_id=document_id, total=len(items), items=items)


@catalog_bp.get("/stats/popular-terms")
def popular_terms():
    store = get_store(current_app)
    limit = request.args.get("limit", default=10, type=int)
    items = store.popular_terms(limit=limit)
    return jsonify(items=items, total=len(items))


