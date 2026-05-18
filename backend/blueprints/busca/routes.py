"""
Blueprint para búsqueda de documentos.
"""
from flask import Blueprint, request, jsonify
from uuid import UUID
from backend.services.auth import TokenService
from backend.services.busca import BuscaService

busca_bp = Blueprint('busca', __name__, url_prefix='/api/busca')


def obtener_usuario_id_del_token():
    """Extraer usuario_id del token de autenticación"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    return TokenService.obtener_usuario_id_del_token(token)


@busca_bp.route('/buscar', methods=['GET', 'POST'])
def buscar():
    """Buscar documentos por palabras clave"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        
        # Obtener parámetros
        if request.method == 'POST':
            data = request.get_json()
            termino = data.get('termino', '')
            filtros = data.get('filtros', {})
        else:
            termino = request.args.get('q', '')
            filtros = {
                'categoria_id': request.args.get('categoria_id', type=int),
                'tipo': request.args.get('tipo'),
            }
            # Eliminar None values
            filtros = {k: v for k, v in filtros.items() if v is not None}
        
        if not termino:
            return jsonify({'error': 'Se requiere un término de búsqueda'}), 400
        
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)
        
        resultado = BuscaService.buscar_por_palabras_clave(
            termino=termino,
            usuario_id=usuario_id,
            pagina=pagina,
            por_pagina=por_pagina,
            filtros=filtros
        )
        
        return jsonify({
            'termino': termino,
            'filtros': filtros,
            'total': resultado['total'],
            'pagina': pagina,
            'por_pagina': por_pagina,
            'resultados': resultado['resultados']
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@busca_bp.route('/categoria/<int:categoria_id>', methods=['GET'])
def buscar_por_categoria(categoria_id):
    """Buscar documentos por categoría"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)
        
        resultado = BuscaService.buscar_por_categoria(
            categoria_id=categoria_id,
            usuario_id=usuario_id,
            pagina=pagina,
            por_pagina=por_pagina
        )
        
        return jsonify({
            'categoria_id': categoria_id,
            'total': resultado['total'],
            'pagina': pagina,
            'por_pagina': por_pagina,
            'resultados': resultado['resultados']
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@busca_bp.route('/etiquetas', methods=['GET', 'POST'])
def buscar_por_etiquetas():
    """Buscar documentos por etiquetas"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        
        # Obtener IDs de etiquetas
        if request.method == 'POST':
            data = request.get_json()
            etiqueta_ids = data.get('etiqueta_ids', [])
        else:
            etiqueta_ids = request.args.getlist('etiqueta_id', type=int)
        
        if not etiqueta_ids:
            return jsonify({'error': 'Se requiere al menos una etiqueta'}), 400
        
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)
        
        resultado = BuscaService.buscar_por_etiquetas(
            etiqueta_ids=etiqueta_ids,
            usuario_id=usuario_id,
            pagina=pagina,
            por_pagina=por_pagina
        )
        
        return jsonify({
            'etiqueta_ids': etiqueta_ids,
            'total': resultado['total'],
            'pagina': pagina,
            'por_pagina': por_pagina,
            'resultados': resultado['resultados']
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@busca_bp.route('/similares/<documento_id>', methods=['GET'])
def documentos_similares(documento_id):
    """Obtener documentos similares a uno dado"""
    try:
        doc_id = UUID(documento_id)
        
        similares = BuscaService.buscar_documentos_similares(
            documento_id=doc_id,
            limite=10
        )
        
        return jsonify({
            'documento_id': documento_id,
            'similares': similares
        }), 200
    
    except ValueError:
        return jsonify({'error': 'ID de documento inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@busca_bp.route('/historial', methods=['GET'])
def obtener_historial():
    """Obtener historial de búsquedas del usuario"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        
        if not usuario_id:
            return jsonify({'error': 'Se requiere autenticación'}), 401
        
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)
        
        historial = BuscaService.obtener_historial_busquedas(usuario_id, pagina, por_pagina)
        
        return jsonify({
            'total': historial.total,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'historial': [h.to_dict() for h in historial.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@busca_bp.route('/populares', methods=['GET'])
def obtener_populares():
    """Obtener búsquedas populares"""
    try:
        limite = request.args.get('limite', 10, type=int)
        
        populares = BuscaService.obtener_busquedas_populares(limite)
        
        return jsonify({
            'limite': limite,
            'resultados': populares
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500
