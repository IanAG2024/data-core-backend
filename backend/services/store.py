from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
import re
from typing import Any, Optional
from uuid import uuid4

try:
    import psycopg
    from psycopg.rows import dict_row
except Exception:  # pragma: no cover - optional dependency
    psycopg = None
    dict_row = None

TOKEN_RE = re.compile(r"[\wáéíóúñüÁÉÍÓÚÑÜ]+", re.UNICODE)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def normalize_text(value: str | None) -> str:
    return (value or "").strip().lower()


def tokenize(value: str | None) -> list[str]:
    return TOKEN_RE.findall(normalize_text(value))


def ensure_json(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def parse_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y", "si", "sí"}


def parse_json_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        import json

        parsed = json.loads(stripped)
        return parsed if isinstance(parsed, list) else []
    return []


@dataclass
class StoreResult:
    items: list[dict[str, Any]]
    total: int


@dataclass
class InMemoryStore:
    seed_demo_data: bool = True
    categories: dict[int, dict[str, Any]] = field(default_factory=dict)
    tags: dict[int, dict[str, Any]] = field(default_factory=dict)
    documents: dict[str, dict[str, Any]] = field(default_factory=dict)
    search_history: list[dict[str, Any]] = field(default_factory=list)
    access_log: list[dict[str, Any]] = field(default_factory=list)
    recommendations_data: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    _category_seq: int = 1
    _tag_seq: int = 1

    def __post_init__(self) -> None:
        if self.seed_demo_data:
            self._seed()

    def _seed(self) -> None:
        self.create_category({"nombre": "General", "descripcion": "Documentos sin categoría específica"})
        self.create_category({"nombre": "Académico", "descripcion": "Material académico y de investigación"})
        self.create_category({"nombre": "Multimedia", "descripcion": "Archivos de audio, video e imágenes"})
        self.create_category({"nombre": "Documentos", "descripcion": "Word, Excel, PowerPoint y PDF"})
        self.create_category({"nombre": "Personal", "descripcion": "Archivos personales del usuario"})

        for nombre, color in [
            ("investigacion", "#3B82F6"),
            ("tutorial", "#10B981"),
            ("presentacion", "#F59E0B"),
            ("datos", "#EF4444"),
            ("multimedia", "#8B5CF6"),
            ("machine-learning", "#EC4899"),
            ("python", "#14B8A6"),
            ("base-de-datos", "#F97316"),
        ]:
            self.create_tag({"nombre": nombre, "color": color})

        docs = [
            {
                "titulo": "Introducción a Machine Learning con Python",
                "descripcion": "Documento explicando los fundamentos de ML usando scikit-learn y NLTK",
                "tipo": "pdf",
                "extension": ".pdf",
                "mime_type": "application/pdf",
                "nombre_original": "ml_intro.pdf",
                "ruta_almacenamiento": "/uploads/docs/ml_intro.pdf",
                "tamano_bytes": 2048000,
                "contenido_texto": "Machine Learning es una rama de la inteligencia artificial que permite a los sistemas aprender automáticamente. Python es el lenguaje más utilizado con bibliotecas como scikit-learn, NLTK y pandas.",
                "estado": "completado",
                "es_publico": True,
                "categoria_id": 2,
                "etiquetas": ["machine-learning", "python", "investigacion"],
                "palabras_clave": ["machine learning", "python", "ia"],
            },
            {
                "titulo": "Tutorial Base de Datos PostgreSQL",
                "descripcion": "Guía completa sobre PostgreSQL con ejemplos prácticos",
                "tipo": "word",
                "extension": ".docx",
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "nombre_original": "tutorial_postgres.docx",
                "ruta_almacenamiento": "/uploads/docs/tutorial_postgres.docx",
                "tamano_bytes": 512000,
                "contenido_texto": "PostgreSQL es un sistema de gestión de bases de datos relacional de código abierto. Soporta búsqueda full-text, JSON, y extensiones avanzadas como pg_trgm.",
                "estado": "completado",
                "es_publico": True,
                "categoria_id": 4,
                "etiquetas": ["tutorial", "base-de-datos"],
                "palabras_clave": ["postgresql", "base de datos", "trigram"],
            },
            {
                "titulo": "Presentación Proyecto Final - Buscador Multimedia",
                "descripcion": "Slides de presentación del sistema de búsqueda y almacenamiento",
                "tipo": "powerpoint",
                "extension": ".pptx",
                "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "nombre_original": "proyecto_final.pptx",
                "ruta_almacenamiento": "/uploads/docs/proyecto_final.pptx",
                "tamano_bytes": 3072000,
                "contenido_texto": "Sistema de búsqueda y almacenamiento multimedia. Tecnologías: Python, PostgreSQL, NLTK, scikit-learn. Funcionalidades: búsqueda por palabras clave, ordenamiento por relevancia, soporte multimedia.",
                "estado": "completado",
                "es_publico": True,
                "categoria_id": 4,
                "etiquetas": ["presentacion", "multimedia", "python"],
                "palabras_clave": ["buscador", "multimedia", "relevancia"],
            },
        ]
        for payload in docs:
            self.create_document(payload)

    def health(self) -> dict[str, Any]:
        return {"backend": "memory", "status": "ok", "documents": len(self.documents)}

    def list_categories(self) -> list[dict[str, Any]]:
        return sorted(self.categories.values(), key=lambda item: item["id"])

    def create_category(self, payload: dict[str, Any]) -> dict[str, Any]:
        category_id = self._category_seq
        self._category_seq += 1
        record = {
            "id": category_id,
            "nombre": payload.get("nombre", "Sin nombre"),
            "descripcion": payload.get("descripcion"),
            "categoria_padre": payload.get("categoria_padre"),
            "creado_en": utcnow().isoformat(),
        }
        self.categories[category_id] = record
        return record

    def list_tags(self) -> list[dict[str, Any]]:
        return sorted(self.tags.values(), key=lambda item: item["id"])

    def create_tag(self, payload: dict[str, Any]) -> dict[str, Any]:
        tag_id = self._tag_seq
        self._tag_seq += 1
        record = {
            "id": tag_id,
            "nombre": payload.get("nombre", "sin-etiqueta"),
            "color": payload.get("color", "#6B7280"),
        }
        self.tags[tag_id] = record
        return record

    def _tag_names(self, values: list[Any]) -> list[str]:
        names: list[str] = []
        for value in values:
            if isinstance(value, str):
                names.append(value.strip())
            elif isinstance(value, dict):
                names.append(str(value.get("nombre", "")).strip())
        return [name for name in names if name]

    def create_document(self, payload: dict[str, Any]) -> dict[str, Any]:
        document_id = str(payload.get("id") or uuid4())
        created_at = utcnow().isoformat()
        record = {
            "id": document_id,
            "usuario_id": payload.get("usuario_id"),
            "categoria_id": payload.get("categoria_id"),
            "titulo": payload.get("titulo", "Sin título"),
            "descripcion": payload.get("descripcion"),
            "tipo": payload.get("tipo", "otro"),
            "extension": payload.get("extension"),
            "mime_type": payload.get("mime_type"),
            "nombre_original": payload.get("nombre_original", payload.get("titulo", "archivo")),
            "ruta_almacenamiento": payload.get("ruta_almacenamiento", ""),
            "tamano_bytes": payload.get("tamano_bytes"),
            "hash_sha256": payload.get("hash_sha256"),
            "es_publico": parse_bool(payload.get("es_publico"), False),
            "contenido_texto": payload.get("contenido_texto"),
            "idioma": payload.get("idioma", "spanish"),
            "metadatos": ensure_json(payload.get("metadatos")),
            "estado": payload.get("estado", "pendiente"),
            "error_mensaje": payload.get("error_mensaje"),
            "creado_en": created_at,
            "actualizado_en": created_at,
            "ultimo_acceso": None,
            "etiquetas": self._tag_names(payload.get("etiquetas", [])),
            "palabras_clave": [
                {
                    "palabra": item if isinstance(item, str) else str(item.get("palabra", "")),
                    "peso": float(item.get("peso", 1.0)) if isinstance(item, dict) else 1.0,
                    "fuente": item.get("fuente", "manual") if isinstance(item, dict) else "manual",
                }
                for item in parse_json_list(payload.get("palabras_clave", []))
            ],
            "accesos": [],
        }
        self.documents[document_id] = record
        return record

    def update_document(self, document_id: str, payload: dict[str, Any]) -> Optional[dict[str, Any]]:
        record = self.documents.get(document_id)
        if not record:
            return None
        for field_name in [
            "usuario_id",
            "categoria_id",
            "titulo",
            "descripcion",
            "tipo",
            "extension",
            "mime_type",
            "nombre_original",
            "ruta_almacenamiento",
            "tamano_bytes",
            "hash_sha256",
            "contenido_texto",
            "idioma",
            "estado",
            "error_mensaje",
        ]:
            if field_name in payload and payload[field_name] is not None:
                record[field_name] = payload[field_name]
        if "es_publico" in payload:
            record["es_publico"] = parse_bool(payload.get("es_publico"), record["es_publico"])
        if "metadatos" in payload and payload["metadatos"] is not None:
            record["metadatos"] = ensure_json(payload["metadatos"])
        if "etiquetas" in payload and payload["etiquetas"] is not None:
            record["etiquetas"] = self._tag_names(parse_json_list(payload["etiquetas"]))
        if "palabras_clave" in payload and payload["palabras_clave"] is not None:
            record["palabras_clave"] = [
                {
                    "palabra": item if isinstance(item, str) else str(item.get("palabra", "")),
                    "peso": float(item.get("peso", 1.0)) if isinstance(item, dict) else 1.0,
                    "fuente": item.get("fuente", "manual") if isinstance(item, dict) else "manual",
                }
                for item in parse_json_list(payload["palabras_clave"])
            ]
        record["actualizado_en"] = utcnow().isoformat()
        return record

    def delete_document(self, document_id: str) -> bool:
        return self.documents.pop(document_id, None) is not None

    def get_document(self, document_id: str) -> Optional[dict[str, Any]]:
        return self.documents.get(document_id)

    def _document_search_blob(self, document: dict[str, Any]) -> str:
        keyword_text = " ".join(keyword["palabra"] for keyword in document.get("palabras_clave", []))
        tag_text = " ".join(document.get("etiquetas", []))
        category = self.categories.get(document.get("categoria_id"), {})
        return " ".join(
            filter(
                None,
                [
                    document.get("titulo"),
                    document.get("descripcion"),
                    document.get("contenido_texto"),
                    keyword_text,
                    tag_text,
                    category.get("nombre"),
                ],
            )
        )

    def _document_score(self, document: dict[str, Any], query: str) -> float:
        normalized_query = normalize_text(query)
        if not normalized_query:
            return 0.0

        query_tokens = set(tokenize(normalized_query))
        blob = normalize_text(self._document_search_blob(document))
        blob_tokens = set(tokenize(blob))
        title_tokens = set(tokenize(document.get("titulo")))
        description_tokens = set(tokenize(document.get("descripcion")))
        content_tokens = set(tokenize(document.get("contenido_texto")))
        keyword_tokens = {normalize_text(item["palabra"]) for item in document.get("palabras_clave", [])}
        tag_tokens = {normalize_text(tag) for tag in document.get("etiquetas", [])}

        search_pool = title_tokens | description_tokens | content_tokens | keyword_tokens | tag_tokens
        title_overlap = len(query_tokens & title_tokens) / max(len(query_tokens), 1)
        pool_overlap = len(query_tokens & search_pool) / max(len(query_tokens), 1)
        sequence = SequenceMatcher(None, normalized_query, blob).ratio()
        exact_bonus = 0.2 if normalized_query in blob else 0.0
        popularity = min(len(document.get("accesos", [])), 1000) / 1000.0
        recency = 0.0
        last_access = document.get("ultimo_acceso")
        if last_access:
            recency = 0.05
        return round(
            title_overlap * 0.45
            + pool_overlap * 0.25
            + sequence * 0.2
            + exact_bonus
            + popularity * 0.05
            + recency,
            6,
        )

    def search_documents(
        self,
        query: str,
        *,
        tipo: str | None = None,
        categoria_id: int | None = None,
        usuario_id: str | None = None,
        solo_publicos: bool = False,
        limite: int = 20,
        offset: int = 0,
    ) -> StoreResult:
        normalized_query = normalize_text(query)
        scored: list[tuple[float, dict[str, Any]]] = []
        for document in self.documents.values():
            if document.get("estado") != "completado":
                continue
            if tipo and document.get("tipo") != tipo:
                continue
            if categoria_id and document.get("categoria_id") != categoria_id:
                continue
            if usuario_id and document.get("usuario_id") != usuario_id:
                continue
            if solo_publicos and not document.get("es_publico"):
                continue

            score = self._document_score(document, normalized_query)
            if normalized_query and score <= 0:
                continue
            scored.append((score, document))

        scored.sort(key=lambda item: (item[0], item[1].get("creado_en", "")), reverse=True)
        total = len(scored)
        page = scored[offset : offset + limite]
        items = [self._document_view(document, score) for score, document in page]
        if normalized_query:
            self.record_search(normalized_query, total_resultados=total)
        return StoreResult(items=items, total=total)

    def list_documents(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        tipo: str | None = None,
        categoria_id: int | None = None,
        usuario_id: str | None = None,
        solo_publicos: bool = False,
        query: str | None = None,
    ) -> StoreResult:
        documents = list(self.documents.values())
        if query:
            return self.search_documents(
                query,
                tipo=tipo,
                categoria_id=categoria_id,
                usuario_id=usuario_id,
                solo_publicos=solo_publicos,
                limite=per_page,
                offset=(page - 1) * per_page,
            )

        filtered = []
        for document in documents:
            if tipo and document.get("tipo") != tipo:
                continue
            if categoria_id and document.get("categoria_id") != categoria_id:
                continue
            if usuario_id and document.get("usuario_id") != usuario_id:
                continue
            if solo_publicos and not document.get("es_publico"):
                continue
            filtered.append(document)
        filtered.sort(key=lambda item: item.get("creado_en", ""), reverse=True)
        total = len(filtered)
        start = max(page - 1, 0) * per_page
        page_items = filtered[start : start + per_page]
        items = [self._document_view(document, None) for document in page_items]
        return StoreResult(items=items, total=total)

    def _document_view(self, document: dict[str, Any], score: float | None) -> dict[str, Any]:
        category = self.categories.get(document.get("categoria_id"))
        return {
            **{k: v for k, v in document.items() if k not in {"accesos"}},
            "categoria": category,
            "score": score,
            "total_accesos": len(document.get("accesos", [])),
            "etiquetas": document.get("etiquetas", []),
            "palabras_clave": document.get("palabras_clave", []),
        }

    def record_access(self, document_id: str, usuario_id: str | None = None, accion: str = "visualizar") -> bool:
        document = self.documents.get(document_id)
        if not document:
            return False
        access = {"usuario_id": usuario_id, "accion": accion, "accedido_en": utcnow().isoformat()}
        document.setdefault("accesos", []).append(access)
        document["ultimo_acceso"] = access["accedido_en"]
        self.access_log.append({"documento_id": document_id, **access})
        return True

    def record_search(self, termino: str, total_resultados: int = 0, usuario_id: str | None = None, filtros: dict[str, Any] | None = None, ip_origen: str | None = None) -> dict[str, Any]:
        entry = {
            "termino": termino,
            "total_resultados": total_resultados,
            "usuario_id": usuario_id,
            "filtros": filtros or {},
            "ip_origen": ip_origen,
            "buscado_en": utcnow().isoformat(),
        }
        self.search_history.append(entry)
        return entry

    def search_suggestions(self, query: str, limit: int = 10) -> list[str]:
        normalized = normalize_text(query)
        if not normalized:
            return self.popular_terms(limit)
        candidates: list[tuple[float, str]] = []
        seen: set[str] = set()
        query_tokens = set(tokenize(normalized))

        for document in self.documents.values():
            for value in [document.get("titulo"), document.get("descripcion"), document.get("contenido_texto")]:
                if not value:
                    continue
                for token in tokenize(value):
                    if token in seen:
                        continue
                    if normalized in token or token in normalized or query_tokens & set(tokenize(token)):
                        score = SequenceMatcher(None, normalized, token).ratio()
                        candidates.append((score, token))
                        seen.add(token)
            for tag in document.get("etiquetas", []):
                if tag in seen:
                    continue
                if normalized in tag or tag in normalized:
                    candidates.append((1.0, tag))
                    seen.add(tag)
        for term in self.popular_terms(limit * 2):
            if term not in seen and (normalized in term or term in normalized):
                candidates.append((0.95, term))
                seen.add(term)
        candidates.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in candidates[:limit]]

    def popular_terms(self, limit: int = 10) -> list[str]:
        counts: dict[str, int] = {}
        for entry in self.search_history:
            counts[entry["termino"]] = counts.get(entry["termino"], 0) + 1
        ordered = sorted(counts.items(), key=lambda item: (item[1], item[0]), reverse=True)
        return [term for term, _ in ordered[:limit]]

    def recommendations(self, document_id: str, limit: int = 5) -> list[dict[str, Any]]:
        source = self.documents.get(document_id)
        if not source:
            return []
        source_terms = set(tokenize(self._document_search_blob(source)))
        source_tags = set(source.get("etiquetas", []))
        results: list[tuple[float, dict[str, Any]]] = []
        for document in self.documents.values():
            if document["id"] == document_id:
                continue
            doc_terms = set(tokenize(self._document_search_blob(document)))
            doc_tags = set(document.get("etiquetas", []))
            overlap = len(source_terms & doc_terms)
            tag_overlap = len(source_tags & doc_tags)
            score = overlap * 0.7 + tag_overlap * 1.2 + self._document_score(document, source.get("titulo", ""))
            if score > 0:
                results.append((score, document))
        results.sort(key=lambda item: item[0], reverse=True)
        return [{"documento": self._document_view(document, score), "score": score} for score, document in results[:limit]]


class PostgresStore:
    def __init__(self, dsn: str, upload_folder: str | Path | None = None):
        if psycopg is None:
            raise RuntimeError("psycopg no está instalado")
        self.dsn = dsn
        self.upload_folder = str(upload_folder) if upload_folder else None

    def _connect(self):
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def health(self) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT current_database() AS database, current_schema() AS schema, NOW() AS now")
            row = cur.fetchone() or {}
        return {"backend": "postgresql", "status": "ok", **row}

    def list_categories(self) -> list[dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT id, nombre, descripcion, categoria_padre, creado_en FROM buscador.categorias ORDER BY id")
            return cur.fetchall()

    def list_tags(self) -> list[dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT id, nombre, color FROM buscador.etiquetas ORDER BY nombre")
            return cur.fetchall()

    def get_document(self, document_id: str) -> Optional[dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT d.*, c.nombre AS categoria_nombre, c.descripcion AS categoria_descripcion
                FROM buscador.documentos d
                LEFT JOIN buscador.categorias c ON c.id = d.categoria_id
                WHERE d.id = %s
                """,
                (document_id,),
            )
            document = cur.fetchone()
            if not document:
                return None
            cur.execute(
                """
                SELECT e.id, e.nombre, e.color
                FROM buscador.documento_etiquetas de
                JOIN buscador.etiquetas e ON e.id = de.etiqueta_id
                WHERE de.documento_id = %s
                ORDER BY e.nombre
                """,
                (document_id,),
            )
            document["etiquetas"] = cur.fetchall()
            cur.execute(
                """
                SELECT id, palabra, peso, fuente
                FROM buscador.palabras_clave
                WHERE documento_id = %s
                ORDER BY peso DESC, palabra
                """,
                (document_id,),
            )
            document["palabras_clave"] = cur.fetchall()
            return document

    def list_documents(self, **kwargs) -> StoreResult:
        query = kwargs.get("query") or ""
        tipo = kwargs.get("tipo")
        categoria_id = kwargs.get("categoria_id")
        usuario_id = kwargs.get("usuario_id")
        solo_publicos = kwargs.get("solo_publicos", False)
        page = kwargs.get("page", 1)
        per_page = kwargs.get("per_page", 20)
        offset = (page - 1) * per_page
        with self._connect() as conn, conn.cursor() as cur:
            if query:
                cur.execute(
                    """
                    SELECT *
                    FROM buscador.buscar_documentos(%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (query, tipo, categoria_id, usuario_id, solo_publicos, per_page, offset),
                )
                items = cur.fetchall()
                return StoreResult(items=items, total=len(items))
            sql = ["SELECT d.* FROM buscador.documentos d WHERE TRUE"]
            params: list[Any] = []
            if tipo:
                sql.append("AND d.tipo = %s")
                params.append(tipo)
            if categoria_id:
                sql.append("AND d.categoria_id = %s")
                params.append(categoria_id)
            if usuario_id:
                sql.append("AND d.usuario_id = %s")
                params.append(usuario_id)
            if solo_publicos:
                sql.append("AND d.es_publico = TRUE")
            sql.append("ORDER BY d.creado_en DESC LIMIT %s OFFSET %s")
            params.extend([per_page, offset])
            cur.execute(" ".join(sql), tuple(params))
            items = cur.fetchall()
            count_sql = ["SELECT COUNT(*) AS total FROM buscador.documentos d WHERE TRUE"]
            count_params: list[Any] = []
            if tipo:
                count_sql.append("AND d.tipo = %s")
                count_params.append(tipo)
            if categoria_id:
                count_sql.append("AND d.categoria_id = %s")
                count_params.append(categoria_id)
            if usuario_id:
                count_sql.append("AND d.usuario_id = %s")
                count_params.append(usuario_id)
            if solo_publicos:
                count_sql.append("AND d.es_publico = TRUE")
            cur.execute(" ".join(count_sql), tuple(count_params))
            total = int((cur.fetchone() or {"total": 0})["total"])
            return StoreResult(items=items, total=total)

    def create_document(self, payload: dict[str, Any]) -> dict[str, Any]:
        document_id = payload.get("id") or str(uuid4())
        etiquetas = payload.pop("etiquetas", []) or []
        palabras_clave = payload.pop("palabras_clave", []) or []
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO buscador.documentos (
                    id, usuario_id, categoria_id, titulo, descripcion, tipo, extension,
                    mime_type, nombre_original, ruta_almacenamiento, tamano_bytes, hash_sha256,
                    es_publico, contenido_texto, idioma, metadatos, estado, error_mensaje
                ) VALUES (
                    %(id)s, %(usuario_id)s, %(categoria_id)s, %(titulo)s, %(descripcion)s, %(tipo)s, %(extension)s,
                    %(mime_type)s, %(nombre_original)s, %(ruta_almacenamiento)s, %(tamano_bytes)s, %(hash_sha256)s,
                    %(es_publico)s, %(contenido_texto)s, %(idioma)s, %(metadatos)s, %(estado)s, %(error_mensaje)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    usuario_id = EXCLUDED.usuario_id,
                    categoria_id = EXCLUDED.categoria_id,
                    titulo = EXCLUDED.titulo,
                    descripcion = EXCLUDED.descripcion,
                    tipo = EXCLUDED.tipo,
                    extension = EXCLUDED.extension,
                    mime_type = EXCLUDED.mime_type,
                    nombre_original = EXCLUDED.nombre_original,
                    ruta_almacenamiento = EXCLUDED.ruta_almacenamiento,
                    tamano_bytes = EXCLUDED.tamano_bytes,
                    hash_sha256 = EXCLUDED.hash_sha256,
                    es_publico = EXCLUDED.es_publico,
                    contenido_texto = EXCLUDED.contenido_texto,
                    idioma = EXCLUDED.idioma,
                    metadatos = EXCLUDED.metadatos,
                    estado = EXCLUDED.estado,
                    error_mensaje = EXCLUDED.error_mensaje,
                    actualizado_en = NOW()
                """,
                {
                    "id": document_id,
                    "usuario_id": payload.get("usuario_id"),
                    "categoria_id": payload.get("categoria_id"),
                    "titulo": payload.get("titulo"),
                    "descripcion": payload.get("descripcion"),
                    "tipo": payload.get("tipo", "otro"),
                    "extension": payload.get("extension"),
                    "mime_type": payload.get("mime_type"),
                    "nombre_original": payload.get("nombre_original"),
                    "ruta_almacenamiento": payload.get("ruta_almacenamiento"),
                    "tamano_bytes": payload.get("tamano_bytes"),
                    "hash_sha256": payload.get("hash_sha256"),
                    "es_publico": parse_bool(payload.get("es_publico"), False),
                    "contenido_texto": payload.get("contenido_texto"),
                    "idioma": payload.get("idioma", "spanish"),
                    "metadatos": payload.get("metadatos") if isinstance(payload.get("metadatos"), dict) else {},
                    "estado": payload.get("estado", "pendiente"),
                    "error_mensaje": payload.get("error_mensaje"),
                },
            )
            self._sync_tags(cur, document_id, etiquetas)
            self._sync_keywords(cur, document_id, palabras_clave)
        document = self.get_document(document_id)
        if not document:
            raise RuntimeError("No se pudo recuperar el documento recién creado")
        return document

    def update_document(self, document_id: str, payload: dict[str, Any]) -> Optional[dict[str, Any]]:
        etiquetas = payload.get("etiquetas", None)
        palabras_clave = payload.get("palabras_clave", None)
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE buscador.documentos
                SET usuario_id = COALESCE(%(usuario_id)s, usuario_id),
                    categoria_id = COALESCE(%(categoria_id)s, categoria_id),
                    titulo = COALESCE(%(titulo)s, titulo),
                    descripcion = COALESCE(%(descripcion)s, descripcion),
                    tipo = COALESCE(%(tipo)s, tipo),
                    extension = COALESCE(%(extension)s, extension),
                    mime_type = COALESCE(%(mime_type)s, mime_type),
                    nombre_original = COALESCE(%(nombre_original)s, nombre_original),
                    ruta_almacenamiento = COALESCE(%(ruta_almacenamiento)s, ruta_almacenamiento),
                    tamano_bytes = COALESCE(%(tamano_bytes)s, tamano_bytes),
                    hash_sha256 = COALESCE(%(hash_sha256)s, hash_sha256),
                    es_publico = COALESCE(%(es_publico)s, es_publico),
                    contenido_texto = COALESCE(%(contenido_texto)s, contenido_texto),
                    idioma = COALESCE(%(idioma)s, idioma),
                    metadatos = COALESCE(%(metadatos)s, metadatos),
                    estado = COALESCE(%(estado)s, estado),
                    error_mensaje = COALESCE(%(error_mensaje)s, error_mensaje),
                    actualizado_en = NOW()
                WHERE id = %(id)s
                """,
                {
                    "id": document_id,
                    "usuario_id": payload.get("usuario_id"),
                    "categoria_id": payload.get("categoria_id"),
                    "titulo": payload.get("titulo"),
                    "descripcion": payload.get("descripcion"),
                    "tipo": payload.get("tipo"),
                    "extension": payload.get("extension"),
                    "mime_type": payload.get("mime_type"),
                    "nombre_original": payload.get("nombre_original"),
                    "ruta_almacenamiento": payload.get("ruta_almacenamiento"),
                    "tamano_bytes": payload.get("tamano_bytes"),
                    "hash_sha256": payload.get("hash_sha256"),
                    "es_publico": payload.get("es_publico") if "es_publico" in payload else None,
                    "contenido_texto": payload.get("contenido_texto"),
                    "idioma": payload.get("idioma"),
                    "metadatos": payload.get("metadatos") if isinstance(payload.get("metadatos"), dict) else None,
                    "estado": payload.get("estado"),
                    "error_mensaje": payload.get("error_mensaje"),
                },
            )
            if cur.rowcount == 0:
                return None
            if etiquetas is not None:
                cur.execute("DELETE FROM buscador.documento_etiquetas WHERE documento_id = %s", (document_id,))
                self._sync_tags(cur, document_id, etiquetas)
            if palabras_clave is not None:
                cur.execute("DELETE FROM buscador.palabras_clave WHERE documento_id = %s", (document_id,))
                self._sync_keywords(cur, document_id, palabras_clave)
        return self.get_document(document_id)

    def delete_document(self, document_id: str) -> bool:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM buscador.documentos WHERE id = %s", (document_id,))
            return cur.rowcount > 0

    def _sync_tags(self, cur, document_id: str, etiquetas: list[Any]) -> None:
        for tag in etiquetas:
            nombre = tag if isinstance(tag, str) else str(tag.get("nombre", "")).strip()
            if not nombre:
                continue
            cur.execute(
                """
                INSERT INTO buscador.etiquetas (nombre)
                VALUES (%s)
                ON CONFLICT (nombre) DO NOTHING
                RETURNING id
                """,
                (nombre,)
            )
            row = cur.fetchone()
            if row and row.get("id"):
                tag_id = row["id"]
            else:
                cur.execute("SELECT id FROM buscador.etiquetas WHERE lower(nombre) = lower(%s)", (nombre,))
                tag_id = (cur.fetchone() or {}).get("id")
            if tag_id:
                cur.execute(
                    """
                    INSERT INTO buscador.documento_etiquetas (documento_id, etiqueta_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (document_id, tag_id),
                )

    def _sync_keywords(self, cur, document_id: str, palabras_clave: list[Any]) -> None:
        for item in palabras_clave:
            if isinstance(item, str):
                palabra = item.strip()
                peso = 1.0
                fuente = "manual"
            else:
                palabra = str(item.get("palabra", "")).strip()
                peso = float(item.get("peso", 1.0))
                fuente = item.get("fuente", "manual")
            if not palabra:
                continue
            cur.execute(
                """
                INSERT INTO buscador.palabras_clave (documento_id, palabra, peso, fuente)
                VALUES (%s, %s, %s, %s)
                """,
                (document_id, palabra, peso, fuente),
            )

    def record_access(self, document_id: str, usuario_id: str | None = None, accion: str = "visualizar") -> bool:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT buscador.registrar_acceso(%s, %s, %s)", (document_id, usuario_id, accion))
            return True

    def record_search(self, termino: str, total_resultados: int = 0, usuario_id: str | None = None, filtros: dict[str, Any] | None = None, ip_origen: str | None = None) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT buscador.registrar_busqueda(%s, %s, %s, %s, %s)", (termino, total_resultados, usuario_id, filtros or {}, ip_origen))
        return {"termino": termino, "total_resultados": total_resultados}

    def search_documents(self, query: str, **kwargs) -> StoreResult:
        tipo = kwargs.get("tipo")
        categoria_id = kwargs.get("categoria_id")
        usuario_id = kwargs.get("usuario_id")
        solo_publicos = kwargs.get("solo_publicos", False)
        limit = kwargs.get("limite", 20)
        offset = kwargs.get("offset", 0)
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM buscador.buscar_documentos(%s, %s, %s, %s, %s, %s, %s)
                """,
                (query, tipo, categoria_id, usuario_id, solo_publicos, limit, offset),
            )
            items = cur.fetchall()
            return StoreResult(items=items, total=len(items))

    def search_suggestions(self, query: str, limit: int = 10) -> list[str]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT termino FROM buscador.terminos_populares(%s)", (limit,))
            popular = [row["termino"] for row in cur.fetchall()]
            if query:
                cur.execute(
                    """
                    SELECT titulo AS suggestion FROM buscador.documentos
                    WHERE titulo ILIKE %s
                    ORDER BY similarity(titulo, %s) DESC
                    LIMIT %s
                    """,
                    (f"%{query}%", query, limit),
                )
                titles = [row["suggestion"] for row in cur.fetchall()]
            else:
                titles = []
        seen: set[str] = set()
        suggestions: list[str] = []
        for item in titles + popular:
            if item not in seen:
                suggestions.append(item)
                seen.add(item)
        return suggestions[:limit]

    def popular_terms(self, limit: int = 10) -> list[str]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT termino FROM buscador.terminos_populares(%s)", (limit,))
            return [row["termino"] for row in cur.fetchall()]

    def recommendations(self, document_id: str, limit: int = 5) -> list[dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT d.*, r.score, r.algoritmo
                FROM buscador.recomendaciones r
                JOIN buscador.documentos d ON d.id = r.recomendado_id
                WHERE r.documento_id = %s
                ORDER BY r.score DESC
                LIMIT %s
                """,
                (document_id, limit),
            )
            return cur.fetchall()


def create_store(config: dict[str, Any]) -> Any:
    database_url = config.get("DATABASE_URL")
    if database_url and psycopg is not None:
        return PostgresStore(database_url, upload_folder=config.get("UPLOAD_FOLDER"))
    return InMemoryStore(seed_demo_data=not bool(config.get("TESTING")))


def get_store(app) -> Any:
    store = app.extensions.get("store")
    if store is None:
        raise RuntimeError("Almacén no configurado en la aplicación")
    return store


