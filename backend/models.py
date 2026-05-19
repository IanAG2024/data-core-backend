"""
Modelos SQLAlchemy para la aplicación de recuperación de información.
"""
from datetime import datetime
from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from sqlalchemy.sql import func

db = SQLAlchemy()


# Enums
class TipoArchivo(str):
    """Tipos de archivo permitidos"""
    TEXTO = 'texto'
    WORD = 'word'
    EXCEL = 'excel'
    POWERPOINT = 'powerpoint'
    IMAGEN = 'imagen'
    VIDEO = 'video'
    AUDIO = 'audio'
    PDF = 'pdf'
    OTRO = 'otro'


class EstadoProcesamiento(str):
    """Estados del procesamiento de documentos"""
    PENDIENTE = 'pendiente'
    PROCESANDO = 'procesando'
    COMPLETADO = 'completado'
    ERROR = 'error'


class Usuarios(db.Model):
    """Modelo para usuarios del sistema"""
    __tablename__ = 'usuarios'
    __table_args__ = {'schema': 'buscador'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    documentos = db.relationship('Documentos', backref='usuario', lazy=True, cascade='all, delete-orphan')
    accesos = db.relationship('AccesosDocumentos', backref='usuario', lazy=True, cascade='all, delete-orphan')
    busquedas = db.relationship('HistorialBusquedas', backref='usuario', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': str(self.id),
            'nombre': self.nombre,
            'email': self.email,
            'activo': self.activo,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
        }


class Categorias(db.Model):
    """Modelo para categorías de documentos"""
    __tablename__ = 'categorias'
    __table_args__ = {'schema': 'buscador'}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    categoria_padre = db.Column(db.Integer, db.ForeignKey('buscador.categorias.id'), nullable=True)
    creado_en = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    # Relaciones
    documentos = db.relationship('Documentos', backref='categoria', lazy=True, cascade='all, delete-orphan')
    subcategorias = db.relationship('Categorias', backref=db.backref('padre', remote_side=[id]))

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'categoria_padre': self.categoria_padre,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
        }


class Etiquetas(db.Model):
    """Modelo para etiquetas"""
    __tablename__ = 'etiquetas'
    __table_args__ = {'schema': 'buscador'}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#6B7280')

    # Relaciones
    documentos = db.relationship('Documentos', secondary='buscador.documento_etiquetas', 
                                backref=db.backref('etiquetas', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'color': self.color,
        }


class Documentos(db.Model):
    """Modelo para documentos almacenados"""
    __tablename__ = 'documentos'
    __table_args__ = (
        Index('idx_doc_categoria', 'categoria_id'),
        Index('idx_doc_usuario', 'usuario_id'),
        {'schema': 'buscador'}
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    usuario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('buscador.usuarios.id'), nullable=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('buscador.categorias.id'), nullable=True)
    titulo = db.Column(db.String(500), nullable=False)
    descripcion = db.Column(db.Text)
    tipo = db.Column(db.String(50), default=TipoArchivo.OTRO)
    extension = db.Column(db.String(20))
    mime_type = db.Column(db.String(100))
    nombre_original = db.Column(db.String(500), nullable=False)
    ruta_almacenamiento = db.Column(db.Text, nullable=False)
    tamano_bytes = db.Column(db.BigInteger)
    hash_sha256 = db.Column(db.String(64))
    es_publico = db.Column(db.Boolean, default=False)
    contenido_texto = db.Column(db.Text)
    idioma = db.Column(db.String(10), default='spanish')
    tsv_busqueda = db.Column(db.Text)  # Full-text search vector
    metadatos = db.Column(JSONB, default={})
    estado = db.Column(db.String(50), default=EstadoProcesamiento.PENDIENTE)
    error_mensaje = db.Column(db.Text)
    creado_en = db.Column(db.DateTime(timezone=True), default=func.now())
    actualizado_en = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    ultimo_acceso = db.Column(db.DateTime(timezone=True))

    # Relaciones
    accesos = db.relationship('AccesosDocumentos', backref='documento', lazy=True, cascade='all, delete-orphan')
    palabras_clave = db.relationship('PalabrasClave', backref='documento', lazy=True, cascade='all, delete-orphan')
    previews = db.relationship('Previews', backref='documento', lazy=True, cascade='all, delete-orphan')
    recomendaciones = db.relationship('Recomendaciones', backref='documento', lazy=True, 
                                     foreign_keys='Recomendaciones.documento_id',
                                     cascade='all, delete-orphan')

    def to_dict(self, include_contenido=False):
        data = {
            'id': str(self.id),
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'tipo': self.tipo,
            'nombre_original': self.nombre_original,
            'tamano_bytes': self.tamano_bytes,
            'es_publico': self.es_publico,
            'idioma': self.idioma,
            'estado': self.estado,
            'categoria_id': self.categoria_id,
            'usuario_id': str(self.usuario_id) if self.usuario_id else None,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
            'actualizado_en': self.actualizado_en.isoformat() if self.actualizado_en else None,
        }
        if include_contenido:
            data['contenido_texto'] = self.contenido_texto
        return data


class DocumentoEtiquetas(db.Model):
    """Tabla de asociación entre documentos y etiquetas"""
    __tablename__ = 'documento_etiquetas'
    __table_args__ = {'schema': 'buscador'}

    documento_id = db.Column(UUID(as_uuid=True), db.ForeignKey('buscador.documentos.id'), primary_key=True)
    etiqueta_id = db.Column(db.Integer, db.ForeignKey('buscador.etiquetas.id'), primary_key=True)


class AccesosDocumentos(db.Model):
    """Modelo para registrar accesos a documentos"""
    __tablename__ = 'accesos_documentos'
    __table_args__ = {'schema': 'buscador'}

    id = db.Column(db.BigInteger, primary_key=True)
    documento_id = db.Column(UUID(as_uuid=True), db.ForeignKey('buscador.documentos.id'), nullable=False)
    usuario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('buscador.usuarios.id'), nullable=True)
    accion = db.Column(db.String(50), default='visualizar')
    accedido_en = db.Column(db.DateTime(timezone=True), default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'documento_id': str(self.documento_id),
            'usuario_id': str(self.usuario_id) if self.usuario_id else None,
            'accion': self.accion,
            'accedido_en': self.accedido_en.isoformat() if self.accedido_en else None,
        }


class PalabrasClave(db.Model):
    """Modelo para palabras clave de documentos"""
    __tablename__ = 'palabras_clave'
    __table_args__ = (
        Index('idx_pc_documento', 'documento_id'),
        {'schema': 'buscador'}
    )

    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(UUID(as_uuid=True), db.ForeignKey('buscador.documentos.id'), nullable=False)
    palabra = db.Column(db.String(200), nullable=False)
    peso = db.Column(db.Float, default=1.0)
    fuente = db.Column(db.String(50), default='manual')

    def to_dict(self):
        return {
            'id': self.id,
            'documento_id': str(self.documento_id),
            'palabra': self.palabra,
            'peso': self.peso,
            'fuente': self.fuente,
        }


class Previews(db.Model):
    """Modelo para previsualizaciones de documentos"""
    __tablename__ = 'previews'
    __table_args__ = {'schema': 'buscador'}

    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(UUID(as_uuid=True), db.ForeignKey('buscador.documentos.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'thumbnail', 'preview_page', etc.
    ruta = db.Column(db.Text, nullable=False)
    ancho = db.Column(db.Integer)
    alto = db.Column(db.Integer)
    generado_en = db.Column(db.DateTime(timezone=True), default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'documento_id': str(self.documento_id),
            'tipo': self.tipo,
            'ruta': self.ruta,
            'ancho': self.ancho,
            'alto': self.alto,
        }


class HistorialBusquedas(db.Model):
    """Modelo para registrar historial de búsquedas"""
    __tablename__ = 'historial_busquedas'
    __table_args__ = (
        Index('idx_hist_usuario', 'usuario_id'),
        {'schema': 'buscador'}
    )

    id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('buscador.usuarios.id'), nullable=True)
    termino = db.Column(db.Text, nullable=False)
    filtros = db.Column(JSONB, default={})
    total_resultados = db.Column(db.Integer, default=0)
    ip_origen = db.Column(db.Text)
    buscado_en = db.Column(db.DateTime(timezone=True), default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': str(self.usuario_id) if self.usuario_id else None,
            'termino': self.termino,
            'filtros': self.filtros,
            'total_resultados': self.total_resultados,
            'buscado_en': self.buscado_en.isoformat() if self.buscado_en else None,
        }


class Recomendaciones(db.Model):
    """Modelo para recomendaciones de documentos"""
    __tablename__ = 'recomendaciones'
    __table_args__ = (
        db.UniqueConstraint('documento_id', 'recomendado_id', name='recomendaciones_unique'),
        {'schema': 'buscador'}
    )

    id = db.Column(db.BigInteger, primary_key=True)
    documento_id = db.Column(UUID(as_uuid=True), db.ForeignKey('buscador.documentos.id'), nullable=False)
    recomendado_id = db.Column(UUID(as_uuid=True), db.ForeignKey('buscador.documentos.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    algoritmo = db.Column(db.String(50), default='tfidf')
    calculado_en = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    # Relación con el documento recomendado
    documento_recomendado = db.relationship('Documentos', foreign_keys=[recomendado_id], backref='recomendado_por')

    def to_dict(self):
        return {
            'id': self.id,
            'documento_id': str(self.documento_id),
            'recomendado_id': str(self.recomendado_id),
            'score': self.score,
            'algoritmo': self.algoritmo,
            'calculado_en': self.calculado_en.isoformat() if self.calculado_en else None,
        }
