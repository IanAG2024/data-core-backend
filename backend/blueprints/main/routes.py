from flask import Blueprint, current_app, jsonify

from ...services import get_store

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return jsonify(
        service="buscador",
        message="Backend listo para almacenamiento y búsqueda",
        endpoints=[
            "/health",
            "/api/documents",
            "/api/search",
            "/api/categories",
            "/api/tags",
            "/api/recommendations/<document_id>",
        ],
    )


@main_bp.get("/health")
def health():
    store = get_store(current_app)
    return jsonify(store.health())
