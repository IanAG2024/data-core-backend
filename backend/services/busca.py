"""
Servicio de búsqueda de documentos.
"""
from uuid import UUID
from datetime import datetime
from flask import current_app
from sqlalchemy import or_, and_
from backend.models import db, Documentos, PalabrasClave, HistorialBusquedas, Categorias


class BuscaService:
    """Servicio para búsqueda de documentos"""

    @staticmethod
    def buscar_por_palabras_clave(termino: str, usuario_id: UUID | None = None, 
                                 pagina: int = 1, por_pagina: int = 10,
                                 filtros: dict | None = None) -> dict:
        """
        Buscar documentos por palabras clave
        Ordena por relevancia
        """
        if filtros is None:
            filtros = {}
        
        # Construir query base
        query = Documentos.query
        
        # Aplicar filtros
        if usuario_id:
            query = query.filter(
                or_(
                    Documentos.usuario_id == usuario_id,
                    Documentos.es_publico == True
                )
            )
        else:
            query = query.filter(Documentos.es_publico == True)
        
        # Filtro por categoría
        if filtros.get('categoria_id'):
            query = query.filter_by(categoria_id=filtros['categoria_id'])
        
        # Filtro por tipo de archivo
        if filtros.get('tipo'):
            query = query.filter_by(tipo=filtros['tipo'])
        
        # Búsqueda por palabras clave
        palabras = termino.split()
        for palabra in palabras:
            palabra_lower = f"%{palabra.lower()}%"
            query = query.filter(
                or_(
                    Documentos.titulo.ilike(palabra_lower),
                    Documentos.descripcion.ilike(palabra_lower),
                    Documentos.contenido_texto.ilike(palabra_lower),
                    Documentos.nombre_original.ilike(palabra_lower),
                )
            )
        
        # Contar total de resultados
        total_resultados = query.count()
        
        # Ordenar por relevancia (coincidencias en título tienen más peso)
        # Esto es una aproximación simple - en producción usarías PostgreSQL full-text search
        resultados = query.paginate(page=pagina, per_page=por_pagina)
        
        # Registrar búsqueda en historial
        BuscaService.registrar_busqueda(
            usuario_id=usuario_id,
            termino=termino,
            filtros=filtros,
            total_resultados=total_resultados
        )
        
        return {
            'total': total_resultados,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'resultados': [doc.to_dict() for doc in resultados.items]
        }

    @staticmethod
    def buscar_por_categoria(categoria_id: int, usuario_id: UUID | None = None,
                            pagina: int = 1, por_pagina: int = 10):
        """Buscar documentos por categoría"""
        query = Documentos.query.filter_by(categoria_id=categoria_id)
        
        if usuario_id:
            query = query.filter(
                or_(
                    Documentos.usuario_id == usuario_id,
                    Documentos.es_publico == True
                )
            )
        else:
            query = query.filter(Documentos.es_publico == True)
        
        resultados = query.paginate(page=pagina, per_page=por_pagina)
        
        return {
            'total': resultados.total,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'resultados': [doc.to_dict() for doc in resultados.items]
        }

    @staticmethod
    def buscar_documentos_similares(documento_id: UUID, limite: int = 5) -> list:
        """
        Encontrar documentos similares basado en palabras clave
        Útil para recomendaciones
        """
        documento = Documentos.query.get(documento_id)
        if not documento:
            return []
        
        # Obtener palabras clave del documento
        palabras_clave_doc = PalabrasClave.query.filter_by(
            documento_id=documento_id
        ).all()
        
        if not palabras_clave_doc:
            return []
        
        palabras = [pc.palabra for pc in palabras_clave_doc]
        
        # Buscar documentos con palabras clave similares
        similares = Documentos.query.filter(
            Documentos.id != documento_id,
            Documentos.es_publico == True
        ).join(
            PalabrasClave,
            Documentos.id == PalabrasClave.documento_id
        ).filter(
            PalabrasClave.palabra.in_(palabras)
        ).distinct().limit(limite).all()
        
        return [doc.to_dict() for doc in similares]

    @staticmethod
    def registrar_busqueda(usuario_id: UUID | None, termino: str, 
                          filtros: dict | None = None, 
                          total_resultados: int = 0,
                          ip_origen: str | None = None):
        """Registrar búsqueda en historial"""
        busqueda = HistorialBusquedas(
            usuario_id=usuario_id,
            termino=termino,
            filtros=filtros or {},
            total_resultados=total_resultados,
            ip_origen=ip_origen
        )
        db.session.add(busqueda)
        db.session.commit()
        return busqueda

    @staticmethod
    def obtener_historial_busquedas(usuario_id: UUID, pagina: int = 1, por_pagina: int = 10):
        """Obtener historial de búsquedas de un usuario"""
        return HistorialBusquedas.query.filter_by(usuario_id=usuario_id).order_by(
            HistorialBusquedas.buscado_en.desc()
        ).paginate(page=pagina, per_page=por_pagina)

    @staticmethod
    def obtener_busquedas_populares(limite: int = 10):
        """Obtener búsquedas más populares"""
        from sqlalchemy import func
        
        resultados = db.session.query(
            HistorialBusquedas.termino,
            func.count(HistorialBusquedas.id).label('cantidad')
        ).group_by(HistorialBusquedas.termino).order_by(
            func.count(HistorialBusquedas.id).desc()
        ).limit(limite).all()
        
        return [{'termino': r[0], 'cantidad': r[1]} for r in resultados]

    @staticmethod
    def agregar_palabras_clave(documento_id: UUID, palabras: list, fuente: str = 'manual', peso: float = 1.0):
        """Agregar palabras clave a un documento"""
        documento = Documentos.query.get(documento_id)
        if not documento:
            raise ValueError(f"Documento con ID {documento_id} no encontrado")
        
        for palabra in palabras:
            # Verificar si la palabra ya existe
            palabra_existente = PalabrasClave.query.filter_by(
                documento_id=documento_id,
                palabra=palabra.lower()
            ).first()
            
            if not palabra_existente:
                nueva_palabra = PalabrasClave(
                    documento_id=documento_id,
                    palabra=palabra.lower(),
                    peso=peso,
                    fuente=fuente
                )
                db.session.add(nueva_palabra)
        
        db.session.commit()
        return PalabrasClave.query.filter_by(documento_id=documento_id).all()

    @staticmethod
    def obtener_palabras_clave(documento_id: UUID) -> list:
        """Obtener palabras clave de un documento"""
        palabras = PalabrasClave.query.filter_by(documento_id=documento_id).all()
        return [p.to_dict() for p in palabras]

    @staticmethod
    def buscar_por_etiquetas(etiqueta_ids: list, usuario_id: UUID | None = None,
                            pagina: int = 1, por_pagina: int = 10):
        """Buscar documentos por etiquetas"""
        query = Documentos.query
        
        # Filtrar por etiquetas
        if etiqueta_ids:
            from backend.models import Etiquetas
            query = query.join(Etiquetas).filter(Etiquetas.id.in_(etiqueta_ids))
        
        if usuario_id:
            query = query.filter(
                or_(
                    Documentos.usuario_id == usuario_id,
                    Documentos.es_publico == True
                )
            )
        else:
            query = query.filter(Documentos.es_publico == True)
        
        resultados = query.paginate(page=pagina, per_page=por_pagina)
        
        return {
            'total': resultados.total,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'resultados': [doc.to_dict() for doc in resultados.items]
        }
