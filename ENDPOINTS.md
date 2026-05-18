
# 📚 Sistema de Recuperación de Información

Una aplicación Flask completa para almacenar, buscar y gestionar documentos multimedia con persistencia en PostgreSQL.

## 🎯 Características

- ✅ **Almacenamiento de documentos** (texto, imágenes, videos, audio, documentos)
- ✅ **Búsqueda por palabras clave** con resultados ordenados por relevancia
- ✅ **Sistema de categorías** jerárquicas
- ✅ **Sistema de etiquetas** para clasificar documentos
- ✅ **Autenticación con JWT**
- ✅ **Recomendaciones automáticas** basadas en TF-IDF
- ✅ **Historial de búsquedas** y documentos populares
- ✅ **API REST** completamente documentada

## 📋 Requisitos Previos

- Python 3.9+
- PostgreSQL 12+
- pip

## 🚀 Instalación

### 1. Clonar/Descargar el proyecto

```bash
cd backendProyecto
```

### 2. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y configura tu base de datos:

```bash
cp .env.example .env
```

Edita `.env` con tus valores:
```
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/dbRecuperacioIn
FLASK_ENV=development
DEBUG=True
```

### 5. Inicializar la base de datos

```bash
# Crear tablas
python -m flask --app cli init-db

# Cargar datos iniciales (categorías, etiquetas, usuario de prueba)
python -m flask --app cli seed-db
```

### 6. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 📚 API Endpoints

### 🔐 Autenticación (`/api/auth`)

#### Registro
```http
POST /api/auth/registro
Content-Type: application/json

{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "password": "password123"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "juan@example.com",
  "password": "password123"
}
```
**Respuesta:**
```json
{
  "mensaje": "Autenticación exitosa",
  "usuario": { "id": "...", "nombre": "...", "email": "..." },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Obtener Perfil
```http
GET /api/auth/perfil
Authorization: Bearer {token}
```

#### Actualizar Perfil
```http
PUT /api/auth/perfil
Authorization: Bearer {token}
Content-Type: application/json

{
  "nombre": "Juan Pérez Updated"
}
```

#### Cambiar Contraseña
```http
POST /api/auth/cambiar-password
Authorization: Bearer {token}
Content-Type: application/json

{
  "password_antigua": "password123",
  "password_nueva": "newpassword456"
}
```

---

### 📄 Documentos (`/api/documentos`)

#### Subir Documento
```http
POST /api/documentos/subir
Authorization: Bearer {token}
Content-Type: multipart/form-data

Form Data:
- archivo: [archivo binario]
- titulo: "Mi Documento"
- descripcion: "Descripción del documento"
- categoria_id: 1
- es_publico: true
```

#### Obtener Documento
```http
GET /api/documentos/{documento_id}
Authorization: Bearer {token}
```

#### Mis Documentos
```http
GET /api/documentos/mis-documentos?pagina=1&por_pagina=10
Authorization: Bearer {token}
```

#### Listar Documentos Públicos
```http
GET /api/documentos?pagina=1&por_pagina=10&categoria_id=1&tipo=imagen
```

#### Actualizar Documento
```http
PUT /api/documentos/{documento_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "titulo": "Nuevo Título",
  "descripcion": "Nueva descripción",
  "es_publico": true
}
```

#### Eliminar Documento
```http
DELETE /api/documentos/{documento_id}
Authorization: Bearer {token}
```

#### Historial de Accesos
```http
GET /api/documentos/{documento_id}/accesos
Authorization: Bearer {token}
```

#### Agregar Palabras Clave
```http
POST /api/documentos/{documento_id}/palabras-clave
Authorization: Bearer {token}
Content-Type: application/json

{
  "palabras": ["palabra1", "palabra2", "palabra3"]
}
```

#### Obtener Palabras Clave
```http
GET /api/documentos/{documento_id}/palabras-clave
```

#### Agregar Etiqueta
```http
POST /api/documentos/{documento_id}/etiquetas
Authorization: Bearer {token}
Content-Type: application/json

{
  "etiqueta_id": 1
}
```

#### Remover Etiqueta
```http
DELETE /api/documentos/{documento_id}/etiquetas/{etiqueta_id}
Authorization: Bearer {token}
```

---

### 🔍 Búsqueda (`/api/busca`)

#### Buscar por Palabras Clave
```http
GET /api/busca/buscar?q=python&pagina=1&por_pagina=10&categoria_id=1&tipo=documento
Authorization: Bearer {token}
```

O mediante POST:
```http
POST /api/busca/buscar
Authorization: Bearer {token}
Content-Type: application/json

{
  "termino": "python",
  "filtros": {
    "categoria_id": 1,
    "tipo": "documento"
  }
}
```

#### Buscar por Categoría
```http
GET /api/busca/categoria/{categoria_id}?pagina=1&por_pagina=10
Authorization: Bearer {token}
```

#### Buscar por Etiquetas
```http
GET /api/busca/etiquetas?etiqueta_id=1&etiqueta_id=2&pagina=1&por_pagina=10
Authorization: Bearer {token}
```

#### Documentos Similares
```http
GET /api/busca/similares/{documento_id}
```

#### Historial de Búsquedas
```http
GET /api/busca/historial?pagina=1&por_pagina=10
Authorization: Bearer {token}
```

#### Búsquedas Populares
```http
GET /api/busca/populares?limite=10
```

---

### 📂 Categorías (`/api/categorias`)

#### Listar Categorías
```http
GET /api/categorias?pagina=1&por_pagina=10
```

#### Obtener Árbol de Categorías
```http
GET /api/categorias/arbol
```

#### Crear Categoría
```http
POST /api/categorias
Content-Type: application/json

{
  "nombre": "Nueva Categoría",
  "descripcion": "Descripción",
  "categoria_padre": null
}
```

#### Obtener Categoría
```http
GET /api/categorias/{categoria_id}
```

#### Actualizar Categoría
```http
PUT /api/categorias/{categoria_id}
Content-Type: application/json

{
  "nombre": "Categoría Actualizada",
  "descripcion": "Nueva descripción"
}
```

#### Eliminar Categoría
```http
DELETE /api/categorias/{categoria_id}
```

#### Obtener Subcategorías
```http
GET /api/categorias/{categoria_id}/subcategorias
```

---

### 🏷️ Etiquetas (`/api/etiquetas`)

#### Listar Etiquetas
```http
GET /api/etiquetas?pagina=1&por_pagina=10
```

#### Crear Etiqueta
```http
POST /api/etiquetas
Content-Type: application/json

{
  "nombre": "Nueva Etiqueta",
  "color": "#FF5733"
}
```

#### Obtener Etiqueta
```http
GET /api/etiquetas/{etiqueta_id}
```

#### Actualizar Etiqueta
```http
PUT /api/etiquetas/{etiqueta_id}
Content-Type: application/json

{
  "nombre": "Etiqueta Actualizada",
  "color": "#33FF57"
}
```

#### Eliminar Etiqueta
```http
DELETE /api/etiquetas/{etiqueta_id}
```

---

### 💡 Recomendaciones (`/api/recomendaciones`)

#### Obtener Recomendaciones
```http
GET /api/recomendaciones/documento/{documento_id}?limite=5
```

#### Generar Recomendaciones
```http
POST /api/recomendaciones/documento/{documento_id}/generar
Content-Type: application/json

{
  "limite": 5,
  "algoritmo": "tfidf"  # o "categoria"
}
```

#### Documentos Populares
```http
GET /api/recomendaciones/populares?limite=10
```

#### Generar Todas las Recomendaciones
```http
POST /api/recomendaciones/generar-todas
```

#### Eliminar Recomendaciones
```http
DELETE /api/recomendaciones/documento/{documento_id}
```

---

## 🗃️ Modelo de Datos

### Tablas Principales

- **usuarios**: Información de usuarios
- **documentos**: Documentos almacenados
- **categorias**: Categorías jerárquicas
- **etiquetas**: Etiquetas para clasificar
- **documento_etiquetas**: Relación M:N
- **palabras_clave**: Palabras clave de documentos
- **accesos_documentos**: Historial de accesos
- **historial_busquedas**: Registro de búsquedas
- **recomendaciones**: Recomendaciones calculadas
- **previews**: Previsualizaciones de documentos

## 🔧 Configuración

### Variables de Entorno Disponibles

```env
# Seguridad
SECRET_KEY=tu-clave-secreta

# Base de Datos
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Almacenamiento
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=52428800  # 50 MB

# Flask
FLASK_ENV=development
FLASK_APP=app.py
DEBUG=True
```

## 📝 Tipos de Archivo Permitidos

Por defecto se aceptan:
- Texto: `.txt`
- Documentos: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`
- Imágenes: `.png`, `.jpg`, `.jpeg`, `.gif`
- Video: `.mp4`, `.avi`, `.mov`
- Audio: `.mp3`, `.wav`, `.flac`

## 🛠️ Desarrollo

### Estructura del Proyecto

```
backend/
├── __init__.py          # Factory de aplicación
├── config.py            # Configuración
├── models.py            # Modelos SQLAlchemy
├── services/            # Lógica de negocio
│   ├── auth.py
│   ├── documento.py
│   ├── busca.py
│   ├── categoria.py
│   └── recomendacion.py
└── blueprints/          # Rutas de API
    ├── auth/
    ├── documentos/
    ├── busca/
    ├── categorias/
    └── recomendaciones/
```

### Agregar Nuevo Endpoint

1. Crear servicio en `backend/services/`
2. Crear blueprint en `backend/blueprints/`
3. Registrar blueprint en `backend/__init__.py`

## 🧪 Pruebas

```bash
# Ejecutar pruebas
python -m pytest

# Con cobertura
python -m pytest --cov=backend
```

## 📚 Documentación Adicional

- [PostgreSQL Setup](./docs/postgresql.md)
- [JWT Authentication](./docs/auth.md)
- [Search Implementation](./docs/search.md)
- [Recommendations Algorithm](./docs/recommendations.md)

## ⚠️ Notas Importantes

1. **Seguridad**: Cambia `SECRET_KEY` en producción
2. **Almacenamiento**: Configura volumen persistente para `/uploads`
3. **Base de Datos**: Usa PostgreSQL en producción
4. **CORS**: Habilita según necesidades de frontend
5. **SSL**: Implementa SSL/TLS en producción

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -am 'Agregar mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

## 📄 Licencia

MIT License - Ver LICENSE.md

## 👥 Autor

Desarrollado como sistema de recuperación de información.

---

**¿Preguntas?** Abre un issue o contacta al equipo de desarrollo.
