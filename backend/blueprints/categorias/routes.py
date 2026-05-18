"""
Blueprint para gestionar categorías y etiquetas.
"""
from flask import Blueprint, request, jsonify
from backend.services.auth import TokenService
from backend.services.categoria import CategoriaService, EtiquetaService

categoria_bp = Blueprint('categorias', __name__, url_prefix='/api/categorias')


@categoria_bp.route('', methods=['GET'])
def listar_categorias():
    """Listar categorías"""
    try:
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)
        
        categorias = CategoriaService.listar_categorias(pagina, por_pagina)
        
        return jsonify({
            'total': categorias.total,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'categorias': [c.to_dict() for c in categorias.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@categoria_bp.route('/arbol', methods=['GET'])
def obtener_arbol():
    """Obtener estructura en árbol de categorías"""
    try:
        arbol = CategoriaService.obtener_arbol_categorias()
        return jsonify({'arbol': arbol}), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@categoria_bp.route('', methods=['POST'])
def crear_categoria():
    """Crear nueva categoría"""
    try:
        data = request.get_json()
        
        if not data or not data.get('nombre'):
            return jsonify({'error': 'El nombre de la categoría es requerido'}), 400
        
        categoria = CategoriaService.crear_categoria(
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            categoria_padre=data.get('categoria_padre')
        )
        
        return jsonify({
            'mensaje': 'Categoría creada exitosamente',
            'categoria': categoria.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@categoria_bp.route('/<int:categoria_id>', methods=['GET'])
def obtener_categoria(categoria_id):
    """Obtener categoría por ID"""
    try:
        categoria = CategoriaService.obtener_categoria(categoria_id)
        
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada'}), 404
        
        return jsonify(categoria.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@categoria_bp.route('/<int:categoria_id>', methods=['PUT'])
def actualizar_categoria(categoria_id):
    """Actualizar categoría"""
    try:
        data = request.get_json()
        
        categoria = CategoriaService.actualizar_categoria(categoria_id, **data)
        
        return jsonify({
            'mensaje': 'Categoría actualizada',
            'categoria': categoria.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@categoria_bp.route('/<int:categoria_id>', methods=['DELETE'])
def eliminar_categoria(categoria_id):
    """Eliminar categoría"""
    try:
        CategoriaService.eliminar_categoria(categoria_id)
        
        return jsonify({'mensaje': 'Categoría eliminada'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@categoria_bp.route('/<int:categoria_id>/subcategorias', methods=['GET'])
def obtener_subcategorias(categoria_id):
    """Obtener subcategorías de una categoría"""
    try:
        subcategorias = CategoriaService.obtener_subcategorias(categoria_id)
        
        return jsonify({
            'categoria_id': categoria_id,
            'subcategorias': [s.to_dict() for s in subcategorias]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


# ENDPOINTS PARA ETIQUETAS

etiqueta_bp = Blueprint('etiquetas', __name__, url_prefix='/api/etiquetas')


@etiqueta_bp.route('', methods=['GET'])
def listar_etiquetas():
    """Listar etiquetas"""
    try:
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)
        
        etiquetas = EtiquetaService.listar_etiquetas(pagina, por_pagina)
        
        return jsonify({
            'total': etiquetas.total,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'etiquetas': [e.to_dict() for e in etiquetas.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@etiqueta_bp.route('', methods=['POST'])
def crear_etiqueta():
    """Crear nueva etiqueta"""
    try:
        data = request.get_json()
        
        if not data or not data.get('nombre'):
            return jsonify({'error': 'El nombre de la etiqueta es requerido'}), 400
        
        etiqueta = EtiquetaService.crear_etiqueta(
            nombre=data['nombre'],
            color=data.get('color', '#6B7280')
        )
        
        return jsonify({
            'mensaje': 'Etiqueta creada exitosamente',
            'etiqueta': etiqueta.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@etiqueta_bp.route('/<int:etiqueta_id>', methods=['GET'])
def obtener_etiqueta(etiqueta_id):
    """Obtener etiqueta por ID"""
    try:
        etiqueta = EtiquetaService.obtener_etiqueta(etiqueta_id)
        
        if not etiqueta:
            return jsonify({'error': 'Etiqueta no encontrada'}), 404
        
        return jsonify(etiqueta.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@etiqueta_bp.route('/<int:etiqueta_id>', methods=['PUT'])
def actualizar_etiqueta(etiqueta_id):
    """Actualizar etiqueta"""
    try:
        data = request.get_json()
        
        etiqueta = EtiquetaService.actualizar_etiqueta(etiqueta_id, **data)
        
        return jsonify({
            'mensaje': 'Etiqueta actualizada',
            'etiqueta': etiqueta.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@etiqueta_bp.route('/<int:etiqueta_id>', methods=['DELETE'])
def eliminar_etiqueta(etiqueta_id):
    """Eliminar etiqueta"""
    try:
        EtiquetaService.eliminar_etiqueta(etiqueta_id)
        
        return jsonify({'mensaje': 'Etiqueta eliminada'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500
