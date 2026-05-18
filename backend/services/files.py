from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path
from typing import Any

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def sha256_file(file_storage: FileStorage) -> str:
    position = file_storage.stream.tell()
    file_storage.stream.seek(0)
    digest = hashlib.sha256()

    for chunk in iter(lambda: file_storage.stream.read(8192), b""):
        digest.update(chunk)

    file_storage.stream.seek(position)
    return digest.hexdigest()


def save_uploaded_file(file_storage: FileStorage, upload_folder: str | Path, document_id: str) -> dict[str, Any]:
    directory = ensure_directory(Path(upload_folder) / document_id)
    filename = secure_filename(file_storage.filename or "archivo")
    storage_path = directory / filename
    file_storage.save(storage_path)

    mime_type = file_storage.mimetype or mimetypes.guess_type(filename)[0]
    size_bytes = storage_path.stat().st_size

    return {
        "nombre_original": file_storage.filename or filename,
        "ruta_almacenamiento": str(storage_path),
        "mime_type": mime_type,
        "extension": storage_path.suffix.lower() or None,
        "tamano_bytes": size_bytes,
        "hash_sha256": sha256_file(file_storage),
    }

