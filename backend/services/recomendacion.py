"""
Servicio para recomendaciones de documentos.
"""
from uuid import UUID
from datetime import datetime
from backend.models import db, Recomendaciones, Documentos, PalabrasClave


class RecomendacionService:
    """Servicio para generar y gestionar recomendaciones"""

    @staticmethod
    def generar_recomendaciones_tfidf(documento_id: UUID, limite: int = 5) -> list:
        """
        Generar recomendaciones usando algoritmo TF-IDF simplificado
        Basado en palabras clave similares
        """
        documento = Documentos.query.get(documento_id)
        if not documento:
            raise ValueError(f"Documento con ID {documento_id} no encontrado")
        
        # Obtener palabras clave del documento
        palabras_doc = PalabrasClave.query.filter_by(documento_id=documento_id).all()
        
        if not palabras_doc:
            return []
        
        palabras_ids = [pc.id for pc in palabras_doc]
        palabras_texto = [pc.palabra for pc in palabras_doc]
        
        # Buscar documentos con palabras clave similares
        documentos_similares = Documentos.query.join(
            PalabrasClave,
            Documentos.id == PalabrasClave.documento_id
        ).filter(
            Documentos.id != documento_id,
            PalabrasClave.palabra.in_(palabras_texto)
        ).distinct().all()
        
        recomendaciones_data = []
        
        for doc_similar in documentos_similares:
            # Calcular score basado en palabras clave coincidentes
            palabras_similares = PalabrasClave.query.filter_by(
                documento_id=doc_similar.id
            ).filter(PalabrasClave.palabra.in_(palabras_texto)).all()
            
            # Score: suma de pesos de palabras coincidentes
            score = sum(pc.peso for pc in palabras_similares)
            
            recomendaciones_data.append({
                'documento_id': doc_similar.id,
                'score': score
            })
        
        # Ordenar por score descendente y limitar
        recomendaciones_data = sorted(recomendaciones_data, key=lambda x: x['score'], reverse=True)[:limite]
        
        # Guardar recomendaciones en BD
        for rec_data in recomendaciones_data:
            # Verificar si ya existe
            rec_existente = Recomendaciones.query.filter_by(
                documento_id=documento_id,
                recomendado_id=rec_data['documento_id']
            ).first()
            
            if not rec_existente:
                nueva_rec = Recomendaciones(
                    documento_id=documento_id,
                    recomendado_id=rec_data['documento_id'],
                    score=rec_data['score'],
                    algoritmo='tfidf'
                )
                db.session.add(nueva_rec)
        
        db.session.commit()
        
        # Retornar documentos recomendados
        return [
            Documentos.query.get(rec['documento_id']).to_dict() 
            for rec in recomendaciones_data
        ]

    @staticmethod
    def generar_recomendaciones_categoria(documento_id: UUID, limite: int = 5) -> list:
        """
        Generar recomendaciones basadas en categoría
        Documentos de la misma categoría
        """
        documento = Documentos.query.get(documento_id)
        if not documento:
            raise ValueError(f"Documento con ID {documento_id} no encontrado")
        
        if not documento.categoria_id:
            return []
        
        # Obtener documentos de la misma categoría
        documentos_similares = Documentos.query.filter(
            Documentos.id != documento_id,
            Documentos.categoria_id == documento.categoria_id,
            Documentos.es_publico == True
        ).limit(limite).all()
        
        recomendaciones_data = []
        
        for doc_similar in documentos_similares:
            score = 0.5  # Score base para documentos en misma categoría
            
            # Aumentar score si tienen palabras clave en común
            palabras_doc = [pc.palabra for pc in 
                          PalabrasClave.query.filter_by(documento_id=documento_id).all()]
            palabras_similar = [pc.palabra for pc in 
                              PalabrasClave.query.filter_by(documento_id=doc_similar.id).all()]
            
            palabras_comunes = len(set(palabras_doc) & set(palabras_similar))
            score += palabras_comunes * 0.1
            
            recomendaciones_data.append({
                'documento_id': doc_similar.id,
                'score': score
            })
        
        # Ordenar por score
        recomendaciones_data = sorted(recomendaciones_data, key=lambda x: x['score'], reverse=True)
        
        # Guardar recomendaciones
        for rec_data in recomendaciones_data:
            rec_existente = Recomendaciones.query.filter_by(
                documento_id=documento_id,
                recomendado_id=rec_data['documento_id']
            ).first()
            
            if not rec_existente:
                nueva_rec = Recomendaciones(
                    documento_id=documento_id,
                    recomendado_id=rec_data['documento_id'],
                    score=rec_data['score'],
                    algoritmo='categoria'
                )
                db.session.add(nueva_rec)
        
        db.session.commit()
        
        return [
            Documentos.query.get(rec['documento_id']).to_dict() 
            for rec in recomendaciones_data
        ]

    @staticmethod
    def obtener_recomendaciones(documento_id: UUID, limite: int = 5) -> list:
        """Obtener recomendaciones almacenadas de un documento"""
        recomendaciones = Recomendaciones.query.filter_by(
            documento_id=documento_id
        ).order_by(Recomendaciones.score.desc()).limit(limite).all()
        
        return [
            {
                **rec.documento_recomendado.to_dict(),
                'score': rec.score,
                'algoritmo': rec.algoritmo
            } 
            for rec in recomendaciones
        ]

    @staticmethod
    def generar_todas_recomendaciones():
        """Generar recomendaciones para todos los documentos"""
        documentos = Documentos.query.all()
        
        for documento in documentos:
            try:
                RecomendacionService.generar_recomendaciones_tfidf(documento.id)
                RecomendacionService.generar_recomendaciones_categoria(documento.id)
            except Exception as e:
                print(f"Error generando recomendaciones para {documento.id}: {e}")

    @staticmethod
    def eliminar_recomendaciones(documento_id: UUID) -> bool:
        """Eliminar recomendaciones de un documento"""
        Recomendaciones.query.filter_by(documento_id=documento_id).delete()
        db.session.commit()
        return True

    @staticmethod
    def obtener_documentos_populares(limite: int = 10):
        """
        Obtener documentos más accedidos (basado en recomendaciones/accesos)
        """
        from backend.models import AccesosDocumentos
        from sqlalchemy import func
        
        documentos_populares = db.session.query(
            Documentos,
            func.count(AccesosDocumentos.id).label('total_accesos')
        ).join(
            AccesosDocumentos,
            Documentos.id == AccesosDocumentos.documento_id,
            isouter=True
        ).filter(
            Documentos.es_publico == True
        ).group_by(Documentos.id).order_by(
            func.count(AccesosDocumentos.id).desc()
        ).limit(limite).all()
        
        return [
            {
                **doc[0].to_dict(),
                'total_accesos': doc[1] or 0
            } 
            for doc in documentos_populares
        ]
