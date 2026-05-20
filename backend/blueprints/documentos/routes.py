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
from backend.services.extractor import extraer_texto, tokenizar_para_busqueda
from backend.models import db

documentos_bp = Blueprint('documentos', __name__, url_prefix='/api/documentos')


def obtener_usuario_id_del_token():
    """Extraer usuario_id del token de autenticación"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    return TokenService.obtener_usuario_id_del_token(token)


@documentos_bp.route('/subir', methods=['POST'])
def subir_documento():
    """Subir nuevo documento — acepta cualquier tipo de archivo"""
    try:
        usuario_id = obtener_usuario_id_del_token()
        
        if 'archivo' not in request.files:
            return jsonify({'error': 'No se proporcionó archivo'}), 400
        
        archivo = request.files['archivo']
        
        if not archivo.filename or archivo.filename == '':
            return jsonify({'error': 'Archivo vacío'}), 400
        # Validar extensión del archivo
        filename_lower = archivo.filename.lower()
        extension = filename_lower.rsplit('.', 1)[1] if '.' in filename_lower else ''
        
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())
        if extension and extension not in allowed_extensions:
            return jsonify({
                'error': f'Tipo de archivo no permitido: .{extension}',
                'extensiones_permitidas': list(sorted(allowed_extensions))
            }), 400
        
        
        titulo = request.form.get('titulo', archivo.filename)
        descripcion = request.form.get('descripcion', '')
        categoria_id = request.form.get('categoria_id', type=int)
        es_publico = request.form.get('es_publico', 'false').lower() == 'true'
        
        # Crear carpeta de uploads si no existe
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Guardar archivo
        filename = secure_filename(archivo.filename)
        # Preservar extensión si secure_filename la eliminó (ej: .py → _py)
        if '.' not in filename and '.' in archivo.filename:
            ext = archivo.filename.rsplit('.', 1)[1].lower()
            filename = filename + '.' + ext
        ruta_archivo = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        archivo.save(ruta_archivo)
        
        # Calcular hash y obtener información del archivo
        hash_archivo = DocumentoService.calcular_hash_archivo(ruta_archivo)
        tipo_archivo = DocumentoService.obtener_tipo_archivo(filename)
        tamano_bytes = os.path.getsize(ruta_archivo)

        # ── Extracción de texto ──────────────────────────────────────────
        # Extraemos el contenido del archivo para que la búsqueda funcione
        # sobre el contenido completo, no sólo sobre el título.
        try:
            contenido_texto = extraer_texto(ruta_archivo)
        except Exception as e:
            # Si falla la extracción, lo registramos pero continuamos
            print(f"Error extrayendo texto de {ruta_archivo}: {str(e)}")
            contenido_texto = None
        
        # Crear documento (con contenido_texto ya poblado)
        documento = DocumentoService.crear_documento(
            usuario_id=usuario_id,
            titulo=titulo,
            nombre_original=archivo.filename,
            ruta_almacenamiento=ruta_archivo,
            tipo_archivo=tipo_archivo,
            extension=filename.rsplit('.', 1)[1].lower() if '.' in filename else '',
            mime_type=archivo.content_type,
            tamano_bytes=tamano_bytes,
            hash_sha256=hash_archivo,
            es_publico=es_publico,
            categoria_id=categoria_id,
            descripcion=descripcion,
            contenido_texto=contenido_texto,
            estado='completado' if contenido_texto is not None else 'pendiente',
            metadatos={'filename_original': archivo.filename}
        )

        # ── Generar palabras clave automáticamente ───────────────────────
        # Tokenizamos título + descripción + contenido para poblar la tabla
        # palabras_clave, que es la que usa la búsqueda por similitud.
        texto_completo = ' '.join(filter(None, [titulo, descripcion, contenido_texto]))
        tokens = tokenizar_para_busqueda(texto_completo)
        if tokens:
            try:
                BuscaService.agregar_palabras_clave(
                    documento_id=documento.id,
                    palabras=tokens[:200],  # máximo 200 tokens por documento
                    fuente='auto',
                    peso=0.8,
                )
            except Exception:
                pass  # no bloqueamos si falla la indexación
        
        return jsonify({
            'mensaje': 'Documento subido exitosamente',
            'documento': documento.to_dict()
        }), 201
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error al subir documento: {error_detail}")
        return jsonify({
            'error': f'Error al subir: {str(e)}',
            'detalle': error_detail if current_app.debug else None
        }), 500


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
    """Listar documentos (todos, sin requerir autenticación)"""
    try:
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 50, type=int)
        categoria_id = request.args.get('categoria_id', type=int)
        tipo = request.args.get('tipo')
        
        resultado = DocumentoService.listar_documentos(
            pagina=pagina,
            por_pagina=por_pagina,
            categoria_id=categoria_id,
            tipo=tipo,
            es_publico=None  # Devuelve todos
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
    Obtener/Visualizar archivo del documento en el navegador.
    """
    try:
        doc_id = UUID(documento_id)
        documento = DocumentoService.obtener_documento(doc_id)

        if not documento:
            return jsonify({'error': 'Documento no encontrado'}), 404

        # Asegurar ruta absoluta
        ruta = documento.ruta_almacenamiento
        if not os.path.isabs(ruta):
            from backend.config import BASE_DIR
            ruta = os.path.join(str(BASE_DIR), ruta)

        if not os.path.exists(ruta):
            return jsonify({'error': 'Archivo no existe en el sistema'}), 404

        usuario_id = obtener_usuario_id_del_token()
        DocumentoService.registrar_acceso(doc_id, usuario_id, 'visualizar')

        # Asegurar ruta absoluta
        ruta = documento.ruta_almacenamiento
        if not os.path.isabs(ruta):
            from backend.config import BASE_DIR
            ruta = os.path.join(str(BASE_DIR), ruta)

        # Determinar mime_type seguro
        mime = documento.mime_type or 'application/octet-stream'

        return send_file(
            ruta,
            mimetype=mime,
            download_name=documento.nombre_original,
            as_attachment=False,
            conditional=True,
        )
        
    except ValueError:
        return jsonify({'error': 'ID de documento inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error al obtener archivo: {str(e)}'}), 500


@documentos_bp.route('/<documento_id>/descargar', methods=['GET'])
def descargar_archivo(documento_id):
    """
    Descargar archivo del documento (fuerza descarga en el navegador).
    """
    try:
        doc_id = UUID(documento_id)
        documento = DocumentoService.obtener_documento(doc_id)

        if not documento:
            return jsonify({'error': 'Documento no encontrado'}), 404

        # Asegurar ruta absoluta
        ruta = documento.ruta_almacenamiento
        if not os.path.isabs(ruta):
            from backend.config import BASE_DIR
            ruta = os.path.join(str(BASE_DIR), ruta)

        if not os.path.exists(ruta):
            return jsonify({'error': 'Archivo no existe en el sistema'}), 404

        usuario_id = obtener_usuario_id_del_token()
        DocumentoService.registrar_acceso(doc_id, usuario_id, 'descargar')

        mime = documento.mime_type or 'application/octet-stream'

        return send_file(
            ruta,
            mimetype=mime,
            download_name=documento.nombre_original,
            as_attachment=True,
        )

    except ValueError:
        return jsonify({'error': 'ID de documento inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error al descargar: {str(e)}'}), 500


@documentos_bp.route('/<documento_id>/contenido', methods=['GET'])
def obtener_contenido_texto(documento_id):
    """
    Devuelve el contenido de texto de un archivo (código fuente, txt, json, etc.)
    para que el frontend pueda renderizarlo directamente en el visor.
    Límite: 500 KB para evitar respuestas muy grandes.
    """
    TIPOS_TEXTO = {
        'texto', 'otro',  # tipos del backend que pueden ser texto
    }
    EXTENSIONES_TEXTO = {
        'txt', 'md', 'markdown', 'rst', 'csv', 'json', 'yaml', 'yml',
        'xml', 'toml', 'ini', 'cfg', 'conf', 'env', 'log',
        'html', 'htm', 'css', 'scss', 'sass',
        'js', 'jsx', 'ts', 'tsx', 'vue', 'svelte',
        'py', 'pyw', 'java', 'kt', 'c', 'h', 'cpp', 'cc', 'cs',
        'go', 'rs', 'rb', 'php', 'swift', 'dart', 'r', 'sql',
        'sh', 'bash', 'zsh', 'ps1', 'bat', 'lua', 'pl',
        'scala', 'ex', 'exs', 'hs', 'clj',
    }
    MAX_BYTES = 512 * 1024  # 500 KB

    try:
        doc_id = UUID(documento_id)
        documento = DocumentoService.obtener_documento(doc_id)

        if not documento:
            return jsonify({'error': 'Documento no encontrado'}), 404

        # Asegurar ruta absoluta
        ruta = documento.ruta_almacenamiento
        if not os.path.isabs(ruta):
            from backend.config import BASE_DIR
            ruta = os.path.join(str(BASE_DIR), ruta)

        if not os.path.exists(ruta):
            return jsonify({'error': 'Archivo no existe en el sistema'}), 404

        ext = (documento.extension or '').lower()
        if ext not in EXTENSIONES_TEXTO and documento.tipo not in TIPOS_TEXTO:
            return jsonify({'error': 'Este archivo no es de texto'}), 400

        tamano = os.path.getsize(ruta)
        if tamano > MAX_BYTES:
            return jsonify({
                'error': f'Archivo demasiado grande para vista previa ({tamano // 1024} KB). Descárgalo para verlo completo.',
                'demasiado_grande': True,
            }), 413

        with open(ruta, 'r', encoding='utf-8', errors='replace') as f:
            contenido = f.read()

        return jsonify({
            'contenido': contenido,
            'extension': ext,
            'tamano_bytes': tamano,
        }), 200

    except ValueError:
        return jsonify({'error': 'ID de documento inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error al leer contenido: {str(e)}'}), 500


@documentos_bp.route('/admin/reindexar', methods=['POST'])
def reindexar_documentos():
    """
    Re-indexa todos los documentos que no tienen contenido_texto extraído.
    Útil para procesar documentos subidos antes de implementar la extracción.
    """
    try:
        from backend.models import Documentos
        documentos_sin_texto = Documentos.query.filter(
            Documentos.contenido_texto == None
        ).all()

        procesados = 0
        errores = 0

        for doc in documentos_sin_texto:
            try:
                # Extraer texto del archivo físico
                contenido = extraer_texto(doc.ruta_almacenamiento)
                if contenido:
                    doc.contenido_texto = contenido
                    doc.estado = 'completado'

                    # Generar tokens automáticamente
                    texto_completo = ' '.join(filter(None, [doc.titulo, doc.descripcion, contenido]))
                    tokens = tokenizar_para_busqueda(texto_completo)
                    if tokens:
                        BuscaService.agregar_palabras_clave(
                            documento_id=doc.id,
                            palabras=tokens[:200],
                            fuente='auto',
                            peso=0.8,
                        )
                    procesados += 1
                else:
                    # Archivos no textuales (imágenes, vídeos, etc.): marcar como completado igual
                    doc.estado = 'completado'
                    # Agregar al menos el título como palabra clave
                    tokens_titulo = tokenizar_para_busqueda(' '.join(filter(None, [doc.titulo, doc.descripcion])))
                    if tokens_titulo:
                        BuscaService.agregar_palabras_clave(
                            documento_id=doc.id,
                            palabras=tokens_titulo[:50],
                            fuente='auto',
                            peso=0.5,
                        )
                    procesados += 1
            except Exception:
                errores += 1

        db.session.commit()

        return jsonify({
            'mensaje': f'Re-indexación completada: {procesados} procesados, {errores} errores',
            'procesados': procesados,
            'errores': errores,
            'total': len(documentos_sin_texto),
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error en re-indexación: {str(e)}'}), 500
