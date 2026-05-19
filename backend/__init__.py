from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from backend.models import db
from backend.blueprints.auth import auth_bp
from backend.blueprints.documentos import documentos_bp
from backend.blueprints.busca import busca_bp
from backend.blueprints.categorias import categoria_bp, etiqueta_bp
from backend.blueprints.recomendaciones import recomendacion_bp

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno
load_dotenv()


def create_app(config_object: str | dict = "backend.config.Config") -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    if isinstance(config_object, dict):
        app.config.update(config_object)
    else:
        app.config.from_object(config_object)

    # Habilitar CORS para el frontend en desarrollo
    CORS(app, resources={r"/api/*": {"origins": [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]}}, supports_credentials=True)

    # Inicializar SQLAlchemy
    db.init_app(app)

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(documentos_bp)
    app.register_blueprint(busca_bp)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(etiqueta_bp)
    app.register_blueprint(recomendacion_bp)

    # Manejadores de errores
    @app.errorhandler(400)
    def bad_request(error):
        description = getattr(error, "description", str(error))
        return jsonify(error="bad_request", message=description), 400

    @app.errorhandler(404)
    def not_found(error):
        description = getattr(error, "description", "Recurso no encontrado")
        return jsonify(error="not_found", message=description), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        description = getattr(error, "description", "Método no permitido")
        return jsonify(error="method_not_allowed", message=description), 405

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify(error="internal_error", message="Error interno del servidor"), 500

    # Crear tablas de base de datos
    with app.app_context():
        db.create_all()

    return app

