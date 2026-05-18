"""
Servicio para gestionar categorías y etiquetas.
"""
from datetime import datetime
from backend.models import db, Categorias, Etiquetas


class CategoriaService:
    """Servicio para gestionar categorías"""

    @staticmethod
    def crear_categoria(nombre: str, descripcion: str = None, 
                       categoria_padre: int = None) -> Categorias:
        """Crear nueva categoría"""
        if Categorias.query.filter_by(nombre=nombre).first():
            raise ValueError(f"La categoría {nombre} ya existe")
        
        categoria = Categorias(
            nombre=nombre,
            descripcion=descripcion,
            categoria_padre=categoria_padre
        )
        
        db.session.add(categoria)
        db.session.commit()
        return categoria

    @staticmethod
    def obtener_categoria(categoria_id: int) -> Categorias | None:
        """Obtener categoría por ID"""
        return Categorias.query.get(categoria_id)

    @staticmethod
    def actualizar_categoria(categoria_id: int, **kwargs) -> Categorias:
        """Actualizar categoría"""
        categoria = Categorias.query.get(categoria_id)
        if not categoria:
            raise ValueError(f"Categoría con ID {categoria_id} no encontrada")
        
        campos_permitidos = ['nombre', 'descripcion', 'categoria_padre']
        for campo, valor in kwargs.items():
            if campo in campos_permitidos and valor is not None:
                setattr(categoria, campo, valor)
        
        db.session.commit()
        return categoria

    @staticmethod
    def eliminar_categoria(categoria_id: int) -> bool:
        """Eliminar categoría"""
        categoria = Categorias.query.get(categoria_id)
        if not categoria:
            raise ValueError(f"Categoría con ID {categoria_id} no encontrada")
        
        db.session.delete(categoria)
        db.session.commit()
        return True

    @staticmethod
    def listar_categorias(pagina: int = 1, por_pagina: int = 10):
        """Listar categorías con paginación"""
        return Categorias.query.paginate(page=pagina, per_page=por_pagina)

    @staticmethod
    def obtener_categorias_raiz():
        """Obtener categorías sin padre (nivel raíz)"""
        return Categorias.query.filter_by(categoria_padre=None).all()

    @staticmethod
    def obtener_subcategorias(categoria_id: int):
        """Obtener subcategorías de una categoría"""
        return Categorias.query.filter_by(categoria_padre=categoria_id).all()

    @staticmethod
    def obtener_arbol_categorias():
        """Obtener estructura en árbol de categorías"""
        categorias_raiz = CategoriaService.obtener_categorias_raiz()
        
        def construir_arbol(categoria):
            subcategorias = CategoriaService.obtener_subcategorias(categoria.id)
            return {
                'id': categoria.id,
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion,
                'subcategorias': [construir_arbol(sub) for sub in subcategorias]
            }
        
        return [construir_arbol(cat) for cat in categorias_raiz]


class EtiquetaService:
    """Servicio para gestionar etiquetas"""

    @staticmethod
    def crear_etiqueta(nombre: str, color: str = '#6B7280') -> Etiquetas:
        """Crear nueva etiqueta"""
        if Etiquetas.query.filter_by(nombre=nombre).first():
            raise ValueError(f"La etiqueta {nombre} ya existe")
        
        etiqueta = Etiquetas(
            nombre=nombre,
            color=color
        )
        
        db.session.add(etiqueta)
        db.session.commit()
        return etiqueta

    @staticmethod
    def obtener_etiqueta(etiqueta_id: int) -> Etiquetas | None:
        """Obtener etiqueta por ID"""
        return Etiquetas.query.get(etiqueta_id)

    @staticmethod
    def obtener_etiqueta_por_nombre(nombre: str) -> Etiquetas | None:
        """Obtener etiqueta por nombre"""
        return Etiquetas.query.filter_by(nombre=nombre).first()

    @staticmethod
    def actualizar_etiqueta(etiqueta_id: int, **kwargs) -> Etiquetas:
        """Actualizar etiqueta"""
        etiqueta = Etiquetas.query.get(etiqueta_id)
        if not etiqueta:
            raise ValueError(f"Etiqueta con ID {etiqueta_id} no encontrada")
        
        campos_permitidos = ['nombre', 'color']
        for campo, valor in kwargs.items():
            if campo in campos_permitidos and valor is not None:
                setattr(etiqueta, campo, valor)
        
        db.session.commit()
        return etiqueta

    @staticmethod
    def eliminar_etiqueta(etiqueta_id: int) -> bool:
        """Eliminar etiqueta"""
        etiqueta = Etiquetas.query.get(etiqueta_id)
        if not etiqueta:
            raise ValueError(f"Etiqueta con ID {etiqueta_id} no encontrada")
        
        db.session.delete(etiqueta)
        db.session.commit()
        return True

    @staticmethod
    def listar_etiquetas(pagina: int = 1, por_pagina: int = 10):
        """Listar etiquetas con paginación"""
        return Etiquetas.query.paginate(page=pagina, per_page=por_pagina)

    @staticmethod
    def agregar_etiqueta_a_documento(documento_id, etiqueta_id: int):
        """Agregar etiqueta a documento"""
        from backend.models import Documentos
        
        documento = Documentos.query.get(documento_id)
        etiqueta = Etiquetas.query.get(etiqueta_id)
        
        if not documento:
            raise ValueError(f"Documento con ID {documento_id} no encontrado")
        if not etiqueta:
            raise ValueError(f"Etiqueta con ID {etiqueta_id} no encontrada")
        
        if etiqueta not in documento.etiquetas:
            documento.etiquetas.append(etiqueta)
            db.session.commit()
        
        return documento

    @staticmethod
    def remover_etiqueta_de_documento(documento_id, etiqueta_id: int):
        """Remover etiqueta de documento"""
        from backend.models import Documentos
        
        documento = Documentos.query.get(documento_id)
        etiqueta = Etiquetas.query.get(etiqueta_id)
        
        if not documento:
            raise ValueError(f"Documento con ID {documento_id} no encontrado")
        if not etiqueta:
            raise ValueError(f"Etiqueta con ID {etiqueta_id} no encontrada")
        
        if etiqueta in documento.etiquetas:
            documento.etiquetas.remove(etiqueta)
            db.session.commit()
        
        return documento

    @staticmethod
    def obtener_etiquetas_documento(documento_id):
        """Obtener etiquetas de un documento"""
        from backend.models import Documentos
        
        documento = Documentos.query.get(documento_id)
        if not documento:
            raise ValueError(f"Documento con ID {documento_id} no encontrado")
        
        return [e.to_dict() for e in documento.etiquetas]
