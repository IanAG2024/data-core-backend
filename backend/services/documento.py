"""
Servicio para gestionar documentos.
"""
import hashlib
import os
from uuid import UUID
from datetime import datetime
from pathlib import Path
from flask import current_app
from backend.models import db, Documentos, AccesosDocumentos, PalabrasClave, Previews, TipoArchivo, EstadoProcesamiento


class DocumentoService:
    """Servicio para gestionar documentos"""

    @staticmethod
    def crear_documento(usuario_id: UUID | None, titulo: str, nombre_original: str, 
                       ruta_almacenamiento: str, tipo_archivo: str, **kwargs) -> Documentos:
        """Crear nuevo documento"""
        
        documento = Documentos(
            usuario_id=usuario_id,
            titulo=titulo,
            nombre_original=nombre_original,
            ruta_almacenamiento=ruta_almacenamiento,
            tipo=tipo_archivo,
            extension=kwargs.get('extension'),
            mime_type=kwargs.get('mime_type'),
            tamano_bytes=kwargs.get('tamano_bytes'),
            hash_sha256=kwargs.get('hash_sha256'),
            es_publico=kwargs.get('es_publico', False),
            contenido_texto=kwargs.get('contenido_texto'),
            idioma=kwargs.get('idioma', 'spanish'),
            metadatos=kwargs.get('metadatos', {}),
            categoria_id=kwargs.get('categoria_id'),
            descripcion=kwargs.get('descripcion'),
            estado=EstadoProcesamiento.PENDIENTE,
        )
        
        db.session.add(documento)
        db.session.commit()
        return documento

    @staticmethod
    def obtener_documento(documento_id: UUID) -> Documentos | None:
        """Obtener documento por ID"""
        return Documentos.query.get(documento_id)

    @staticmethod
    def obtener_documentos_usuario(usuario_id: UUID, pagina: int = 1, por_pagina: int = 10):
        """Obtener documentos de un usuario con paginación"""
        return Documentos.query.filter_by(usuario_id=usuario_id).paginate(
            page=pagina, per_page=por_pagina
        )

    @staticmethod
    def actualizar_documento(documento_id: UUID, **kwargs) -> Documentos:
        """Actualizar documento"""
        documento = Documentos.query.get(documento_id)
        if not documento:
            raise ValueError(f"Documento con ID {documento_id} no encontrado")
        
        campos_permitidos = ['titulo', 'descripcion', 'categoria_id', 'es_publico', 
                            'contenido_texto', 'estado', 'error_mensaje', 'metadatos']
        for campo, valor in kwargs.items():
            if campo in campos_permitidos and valor is not None:
                setattr(documento, campo, valor)
        
        documento.actualizado_en = datetime.utcnow()
        db.session.commit()
        return documento

    @staticmethod
    def eliminar_documento(documento_id: UUID) -> bool:
        """Eliminar documento"""
        documento = Documentos.query.get(documento_id)
        if not documento:
            raise ValueError(f"Documento con ID {documento_id} no encontrado")
        
        # Eliminar archivo físico
        if os.path.exists(documento.ruta_almacenamiento):
            try:
                os.remove(documento.ruta_almacenamiento)
            except OSError:
                pass
        
        db.session.delete(documento)
        db.session.commit()
        return True

    @staticmethod
    def listar_documentos(pagina: int = 1, por_pagina: int = 10, categoria_id: int | None = None, 
                         tipo: str | None = None, es_publico: bool | None = None):
        """Listar documentos con filtros y paginación"""
        query = Documentos.query
        
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        if tipo:
            query = query.filter_by(tipo=tipo)
        if es_publico is not None:
            query = query.filter_by(es_publico=es_publico)
        
        return query.paginate(page=pagina, per_page=por_pagina)

    @staticmethod
    def registrar_acceso(documento_id: UUID, usuario_id: UUID | None = None, accion: str = 'visualizar'):
        """Registrar acceso a documento"""
        acceso = AccesosDocumentos(
            documento_id=documento_id,
            usuario_id=usuario_id,
            accion=accion
        )
        
        # Actualizar último acceso del documento
        documento = Documentos.query.get(documento_id)
        if documento:
            documento.ultimo_acceso = datetime.utcnow()
        
        db.session.add(acceso)
        db.session.commit()
        return acceso

    @staticmethod
    def obtener_accesos_documento(documento_id: UUID, pagina: int = 1, por_pagina: int = 10):
        """Obtener historial de accesos a un documento"""
        return AccesosDocumentos.query.filter_by(documento_id=documento_id).paginate(
            page=pagina, per_page=por_pagina
        )

    @staticmethod
    def calcular_hash_archivo(ruta_archivo: str) -> str:
        """Calcular hash SHA256 de un archivo"""
        sha256_hash = hashlib.sha256()
        with open(ruta_archivo, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def obtener_tipo_archivo(nombre_archivo: str) -> str:
        """Determinar tipo de archivo según extensión"""
        extension = Path(nombre_archivo).suffix.lower().lstrip('.')
        
        tipos = {
            'txt': TipoArchivo.TEXTO,
            'pdf': TipoArchivo.DOCUMENTO,
            'docx': TipoArchivo.DOCUMENTO,
            'doc': TipoArchivo.DOCUMENTO,
            'xlsx': TipoArchivo.DOCUMENTO,
            'xls': TipoArchivo.DOCUMENTO,
            'pptx': TipoArchivo.DOCUMENTO,
            'ppt': TipoArchivo.DOCUMENTO,
            'png': TipoArchivo.IMAGEN,
            'jpg': TipoArchivo.IMAGEN,
            'jpeg': TipoArchivo.IMAGEN,
            'gif': TipoArchivo.IMAGEN,
            'mp4': TipoArchivo.VIDEO,
            'avi': TipoArchivo.VIDEO,
            'mov': TipoArchivo.VIDEO,
            'mp3': TipoArchivo.AUDIO,
            'wav': TipoArchivo.AUDIO,
            'flac': TipoArchivo.AUDIO,
        }
        
        return tipos.get(extension, TipoArchivo.OTRO)
