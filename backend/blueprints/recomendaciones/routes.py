"""
Blueprint para recomendaciones de documentos.
"""
from flask import Blueprint, request, jsonify
from uuid import UUID
from backend.services.recomendacion import RecomendacionService

recomendacion_bp = Blueprint('recomendaciones', __name__, url_prefix='/api/recomendaciones')


@recomendacion_bp.route('/documento/<documento_id>', methods=['GET'])
def obtener_recomendaciones(documento_id):
    """Obtener recomendaciones para un documento"""
    try:
        doc_id = UUID(documento_id)
        
        limite = request.args.get('limite', 5, type=int)
        
        recomendaciones = RecomendacionService.obtener_recomendaciones(doc_id, limite)
        
        return jsonify({
            'documento_id': documento_id,
            'limite': limite,
            'recomendaciones': recomendaciones
        }), 200
    
    except ValueError:
        return jsonify({'error': 'ID de documento inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@recomendacion_bp.route('/documento/<documento_id>/generar', methods=['POST'])
def generar_recomendaciones(documento_id):
    """Generar recomendaciones para un documento"""
    try:
        doc_id = UUID(documento_id)
        
        data = request.get_json() or {}
        limite = data.get('limite', 5)
        algoritmo = data.get('algoritmo', 'tfidf')  # 'tfidf' o 'categoria'
        
        if algoritmo == 'categoria':
            recomendaciones = RecomendacionService.generar_recomendaciones_categoria(doc_id, limite)
        else:
            recomendaciones = RecomendacionService.generar_recomendaciones_tfidf(doc_id, limite)
        
        return jsonify({
            'mensaje': f'Recomendaciones generadas usando {algoritmo}',
            'documento_id': documento_id,
            'recomendaciones': recomendaciones
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@recomendacion_bp.route('/populares', methods=['GET'])
def obtener_populares():
    """Obtener documentos populares"""
    try:
        limite = request.args.get('limite', 10, type=int)
        
        documentos_populares = RecomendacionService.obtener_documentos_populares(limite)
        
        return jsonify({
            'limite': limite,
            'documentos': documentos_populares
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@recomendacion_bp.route('/generar-todas', methods=['POST'])
def generar_todas():
    """Generar recomendaciones para todos los documentos (puede tomar tiempo)"""
    try:
        RecomendacionService.generar_todas_recomendaciones()
        
        return jsonify({
            'mensaje': 'Generación de recomendaciones completada'
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@recomendacion_bp.route('/documento/<documento_id>', methods=['DELETE'])
def eliminar_recomendaciones(documento_id):
    """Eliminar recomendaciones de un documento"""
    try:
        doc_id = UUID(documento_id)
        
        RecomendacionService.eliminar_recomendaciones(doc_id)
        
        return jsonify({
            'mensaje': 'Recomendaciones eliminadas',
            'documento_id': documento_id
        }), 200
    
    except ValueError:
        return jsonify({'error': 'ID de documento inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500
