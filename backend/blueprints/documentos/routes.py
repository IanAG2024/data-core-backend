"""
Blueprint para gestionar documentos.
"""
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from uuid import UUID
import os
from backend.services.auth import TokenService
from backend.services.documento import DocumentoService
from backend.services.busca import BuscaService
from backend.services.categoria import EtiquetaService
from backend.models import db

documentos_bp = Blueprint('documentos', __name__, url_prefix='/api/documentos')


def obtener_usuario_id_del_token():
    """Extraer usuario_id del token de autenticación"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    return TokenService.obtener_usuario_id_del_token(token)


def archivo_permitido(filename):
    """Verificar si la extensión de archivo es permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@documentos_bp.route('/subir', methods=['POST'])
def subir_documento():
    """Subir nuevo documento"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        
        if 'archivo' not in request.files:
            return jsonify({'error': 'No se proporcionó archivo'}), 400
        
        archivo = request.files['archivo']
        
        if archivo.filename == '':
            return jsonify({'error': 'Archivo vacío'}), 400
        
        if not archivo_permitido(archivo.filename):
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
        # Obtener datos del formulario
        titulo = request.form.get('titulo', archivo.filename)
        descripcion = request.form.get('descripcion', '')
        categoria_id = request.form.get('categoria_id', type=int)
        es_publico = request.form.get('es_publico', 'false').lower() == 'true'
        
        # Crear carpeta de uploads si no existe
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Guardar archivo
        filename = secure_filename(archivo.filename)
        ruta_archivo = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        archivo.save(ruta_archivo)
        
        # Calcular hash y obtener información del archivo
        hash_archivo = DocumentoService.calcular_hash_archivo(ruta_archivo)
        tipo_archivo = DocumentoService.obtener_tipo_archivo(filename)
        tamano_bytes = os.path.getsize(ruta_archivo)
        
        # Crear documento
        documento = DocumentoService.crear_documento(
            usuario_id=usuario_id,
            titulo=titulo,
            nombre_original=archivo.filename,
            ruta_almacenamiento=ruta_archivo,
            tipo_archivo=tipo_archivo,
            extension=filename.rsplit('.', 1)[1].lower(),
            mime_type=archivo.content_type,
            tamano_bytes=tamano_bytes,
            hash_sha256=hash_archivo,
            es_publico=es_publico,
            categoria_id=categoria_id,
            descripcion=descripcion,
            metadatos={'filename_original': archivo.filename}
        )
        
        return jsonify({
            'mensaje': 'Documento subido exitosamente',
            'documento': documento.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Error al subir: {str(e)}'}), 500


@documentos_bp.route('/<documento_id>', methods=['GET'])
def obtener_documento(documento_id):
    """Obtener detalles de un documento"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        doc_id = UUID(documento_id)
        
        documento = DocumentoService.obtener_documento(doc_id)
        
        if not documento:
            return jsonify({'error': 'Documento no encontrado'}), 404
        
        # Verificar permisos
        if not documento.es_publico and documento.usuario_id != usuario_id:
            return jsonify({'error': 'No tienes permiso para acceder a este documento'}), 403
        
        # Registrar acceso
        DocumentoService.registrar_acceso(doc_id, usuario_id, 'visualizar')
        
        return jsonify(documento.to_dict(include_contenido=True)), 200
    
    except ValueError:
        return jsonify({'error': 'ID de documento inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@documentos_bp.route('/mis-documentos', methods=['GET'])
def mis_documentos():
    """Obtener documentos del usuario autenticado"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        
        if not usuario_id:
            return jsonify({'error': 'Se requiere autenticación'}), 401
        
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)
        
        resultado = DocumentoService.obtener_documentos_usuario(usuario_id, pagina, por_pagina)
        
        return jsonify({
            'total': resultado.total,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'documentos': [doc.to_dict() for doc in resultado.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@documentos_bp.route('/<documento_id>', methods=['PUT'])
def actualizar_documento(documento_id):
    """Actualizar documento"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        doc_id = UUID(documento_id)
        
        documento = DocumentoService.obtener_documento(doc_id)
        
        if not documento:
            return jsonify({'error': 'Documento no encontrado'}), 404
        
        # Verificar permisos
        if documento.usuario_id != usuario_id:
            return jsonify({'error': 'No tienes permiso para modificar este documento'}), 403
        
        data = request.get_json()
        documento_actualizado = DocumentoService.actualizar_documento(doc_id, **data)
        
        return jsonify({
            'mensaje': 'Documento actualizado',
            'documento': documento_actualizado.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@documentos_bp.route('/<documento_id>', methods=['DELETE'])
def eliminar_documento(documento_id):
    """Eliminar documento"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        doc_id = UUID(documento_id)
        
        documento = DocumentoService.obtener_documento(doc_id)
        
        if not documento:
            return jsonify({'error': 'Documento no encontrado'}), 404
        
        # Verificar permisos
        if documento.usuario_id != usuario_id:
            return jsonify({'error': 'No tienes permiso para eliminar este documento'}), 403
        
        DocumentoService.eliminar_documento(doc_id)
        
        return jsonify({'mensaje': 'Documento eliminado'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@documentos_bp.route('', methods=['GET'])
def listar_documentos():
    """Listar documentos públicos"""
    try:
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)
        categoria_id = request.args.get('categoria_id', type=int)
        tipo = request.args.get('tipo')
        
        resultado = DocumentoService.listar_documentos(
            pagina=pagina,
            por_pagina=por_pagina,
            categoria_id=categoria_id,
            tipo=tipo,
            es_publico=True
        )
        
        return jsonify({
            'total': resultado.total,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'documentos': [doc.to_dict() for doc in resultado.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@documentos_bp.route('/<documento_id>/accesos', methods=['GET'])
def obtener_accesos(documento_id):
    """Obtener historial de accesos a un documento"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        doc_id = UUID(documento_id)
        
        documento = DocumentoService.obtener_documento(doc_id)
        
        if not documento:
            return jsonify({'error': 'Documento no encontrado'}), 404
        
        if documento.usuario_id != usuario_id:
            return jsonify({'error': 'No tienes permiso'}), 403
        
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)
        
        accesos = DocumentoService.obtener_accesos_documento(doc_id, pagina, por_pagina)
        
        return jsonify({
            'total': accesos.total,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'accesos': [a.to_dict() for a in accesos.items]
        }), 200
    
    except ValueError:
        return jsonify({'error': 'ID de documento inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@documentos_bp.route('/<documento_id>/palabras-clave', methods=['POST'])
def agregar_palabras_clave(documento_id):
    """Agregar palabras clave a documento"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        doc_id = UUID(documento_id)
        
        documento = DocumentoService.obtener_documento(doc_id)
        
        if not documento:
            return jsonify({'error': 'Documento no encontrado'}), 404
        
        if documento.usuario_id != usuario_id:
            return jsonify({'error': 'No tienes permiso'}), 403
        
        data = request.get_json()
        palabras = data.get('palabras', [])
        
        if not palabras:
            return jsonify({'error': 'Se requiere una lista de palabras'}), 400
        
        palabras_agregadas = BuscaService.agregar_palabras_clave(doc_id, palabras)
        
        return jsonify({
            'mensaje': 'Palabras clave agregadas',
            'palabras_clave': [p.to_dict() for p in palabras_agregadas]
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@documentos_bp.route('/<documento_id>/palabras-clave', methods=['GET'])
def obtener_palabras_clave(documento_id):
    """Obtener palabras clave de un documento"""
    try:
        doc_id = UUID(documento_id)
        
        palabras = BuscaService.obtener_palabras_clave(doc_id)
        
        return jsonify({
            'documento_id': documento_id,
            'palabras_clave': palabras
        }), 200
    
    except ValueError:
        return jsonify({'error': 'ID de documento inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@documentos_bp.route('/<documento_id>/etiquetas', methods=['POST'])
def agregar_etiqueta(documento_id):
    """Agregar etiqueta a documento"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        doc_id = UUID(documento_id)
        
        documento = DocumentoService.obtener_documento(doc_id)
        
        if not documento:
            return jsonify({'error': 'Documento no encontrado'}), 404
        
        if documento.usuario_id != usuario_id:
            return jsonify({'error': 'No tienes permiso'}), 403
        
        data = request.get_json()
        etiqueta_id = data.get('etiqueta_id')
        
        if not etiqueta_id:
            return jsonify({'error': 'Se requiere etiqueta_id'}), 400
        
        documento_actualizado = EtiquetaService.agregar_etiqueta_a_documento(doc_id, etiqueta_id)
        
        return jsonify({
            'mensaje': 'Etiqueta agregada',
            'documento': documento_actualizado.to_dict(),
            'etiquetas': [e.to_dict() for e in documento_actualizado.etiquetas]
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@documentos_bp.route('/<documento_id>/etiquetas/<int:etiqueta_id>', methods=['DELETE'])
def remover_etiqueta(documento_id, etiqueta_id):
    """Remover etiqueta de documento"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        doc_id = UUID(documento_id)
        
        documento = DocumentoService.obtener_documento(doc_id)
        
        if not documento:
            return jsonify({'error': 'Documento no encontrado'}), 404
        
        if documento.usuario_id != usuario_id:
            return jsonify({'error': 'No tienes permiso'}), 403
        
        documento_actualizado = EtiquetaService.remover_etiqueta_de_documento(doc_id, etiqueta_id)
        
        return jsonify({
            'mensaje': 'Etiqueta removida',
            'documento': documento_actualizado.to_dict(),
            'etiquetas': [e.to_dict() for e in documento_actualizado.etiquetas]
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@documentos_bp.route('/<documento_id>/etiquetas', methods=['GET'])
def obtener_etiquetas_documento(documento_id):
    """Obtener etiquetas de un documento"""
    try:
        doc_id = UUID(documento_id)
        
        etiquetas = EtiquetaService.obtener_etiquetas_documento(doc_id)
        
        return jsonify({
            'documento_id': documento_id,
            'etiquetas': etiquetas
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@documentos_bp.route('/<documento_id>/archivo', methods=['GET'])
def obtener_archivo(documento_id):
    """
    Obtener/Descargar/Visualizar archivo del documento
    
    Soporta:
    - Imágenes: <img src="/api/documentos/{id}/archivo">
    - Videos: <video><source src="/api/documentos/{id}/archivo"></video>
    - Audio: <audio><source src="/api/documentos/{id}/archivo"></audio>
    - PDF: <iframe src="/api/documentos/{id}/archivo"></iframe>
    """
    try:
        doc_id = UUID(documento_id)
        documento = DocumentoService.obtener_documento(doc_id)
        
        if not documento:
            return jsonify({'error': 'Documento no encontrado'}), 404
        
        # Verificar que el archivo existe
        if not os.path.exists(documento.ruta_almacenamiento):
            return jsonify({'error': 'Archivo no existe en el sistema'}), 404
        
        # Registrar acceso
        usuario_id = obtener_usuario_id_del_token()
        DocumentoService.registrar_acceso(doc_id, usuario_id, 'descargar')
        
        # Servir el archivo
        # as_attachment=False permite visualizar en el navegador
        # as_attachment=True fuerza la descarga
        return send_file(
            documento.ruta_almacenamiento,
            mimetype=documento.mime_type,
            download_name=documento.nombre_original,
            as_attachment=False
        )
        
    except ValueError:
        return jsonify({'error': 'ID de documento inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error al obtener archivo: {str(e)}'}), 500


@documentos_bp.route('/<documento_id>/descargar', methods=['GET'])
def descargar_archivo(documento_id):
    """
    Descargar archivo del documento (fuerza descarga)
    
    Igual que /archivo pero fuerza descargar en lugar de visualizar
    """
    try:
        doc_id = UUID(documento_id)
        documento = DocumentoService.obtener_documento(doc_id)
        
        if not documento:
            return jsonify({'error': 'Documento no encontrado'}), 404
        
        # Verificar que el archivo existe
        if not os.path.exists(documento.ruta_almacenamiento):
            return jsonify({'error': 'Archivo no existe en el sistema'}), 404
        
        # Registrar acceso
        usuario_id = obtener_usuario_id_del_token()
        DocumentoService.registrar_acceso(doc_id, usuario_id, 'descargar')
        
        # Servir el archivo como descarga
        return send_file(
            documento.ruta_almacenamiento,
            mimetype=documento.mime_type,
            download_name=documento.nombre_original,
            as_attachment=True
        )
        
    except ValueError:
        return jsonify({'error': 'ID de documento inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error al descargar: {str(e)}'}), 500

