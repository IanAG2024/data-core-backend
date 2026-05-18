# 🚀 Guía Rápida de Inicio

## Pasos Iniciales

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Base de Datos
Edita el archivo `.env` con tus credenciales PostgreSQL:
```bash
DATABASE_URL=postgresql://postgres:tu_contraseña@127.0.0.1:5432/dbRecuperacioIn
```

### 3. Inicializar BD
```bash
# Crear tablas
python -m flask --app cli init-db

# Cargar datos iniciales (recomendado)
python -m flask --app cli seed-db
```

### 4. Ejecutar Aplicación
```bash
python app.py
```

O usa el script automático:
```bash
./run.sh
```

La aplicación estará en: **http://localhost:5000**

---

## 📖 Ejemplo de Uso Completo

### 1️⃣ Registrar Usuario
```bash
curl -X POST http://localhost:5000/api/auth/registro \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "password": "password123"
  }'
```

**Respuesta:**
```json
{
  "mensaje": "Usuario registrado exitosamente",
  "usuario": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre": "Juan Pérez",
    "email": "juan@example.com"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Guarda el token para próximas solicitudes**

---

### 2️⃣ Crear Categoría
```bash
curl -X POST http://localhost:5000/api/categorias \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Proyectos Python",
    "descripcion": "Documentos relacionados con proyectos Python"
  }'
```

**Respuesta:**
```json
{
  "mensaje": "Categoría creada exitosamente",
  "categoria": {
    "id": 1,
    "nombre": "Proyectos Python",
    "descripcion": "Documentos relacionados con proyectos Python"
  }
}
```

---

### 3️⃣ Subir Documento
```bash
curl -X POST http://localhost:5000/api/documentos/subir \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "archivo=@documento.pdf" \
  -F "titulo=Mi Documento PDF" \
  -F "descripcion=Un documento importante" \
  -F "categoria_id=1" \
  -F "es_publico=true"
```

**Respuesta:**
```json
{
  "mensaje": "Documento subido exitosamente",
  "documento": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "titulo": "Mi Documento PDF",
    "nombre_original": "documento.pdf",
    "tipo": "documento",
    "tamano_bytes": 15234,
    "creado_en": "2026-05-17T10:30:00"
  }
}
```

---

### 4️⃣ Agregar Palabras Clave
```bash
curl -X POST http://localhost:5000/api/documentos/550e8400-e29b-41d4-a716-446655440001/palabras-clave \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "palabras": ["python", "api", "flask", "recuperación"]
  }'
```

---

### 5️⃣ Buscar Documentos
```bash
curl -X GET "http://localhost:5000/api/busca/buscar?q=python&pagina=1&por_pagina=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Respuesta:**
```json
{
  "termino": "python",
  "filtros": {},
  "total": 5,
  "pagina": 1,
  "por_pagina": 10,
  "resultados": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "titulo": "Mi Documento PDF",
      "descripcion": "Un documento importante",
      "tipo": "documento"
    }
  ]
}
```

---

### 6️⃣ Obtener Documentos Similares
```bash
curl -X GET http://localhost:5000/api/busca/similares/550e8400-e29b-41d4-a716-446655440001 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 7️⃣ Generar Recomendaciones
```bash
curl -X POST http://localhost:5000/api/recomendaciones/documento/550e8400-e29b-41d4-a716-446655440001/generar \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "limite": 5,
    "algoritmo": "tfidf"
  }'
```

---

### 8️⃣ Obtener Recomendaciones
```bash
curl -X GET "http://localhost:5000/api/recomendaciones/documento/550e8400-e29b-41d4-a716-446655440001?limite=5"
```

---

## 🧪 Pruebas con Python

Crea un archivo `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

# 1. Registro
print("📝 Registrando usuario...")
resp = requests.post(f"{BASE_URL}/auth/registro", json={
    "nombre": "Test User",
    "email": "test@example.com",
    "password": "test123"
})
token = resp.json()["token"]
print(f"✓ Token: {token[:50]}...")

# 2. Crear categoría
print("\n📂 Creando categoría...")
resp = requests.post(f"{BASE_URL}/categorias", json={
    "nombre": "Test Category",
    "descripcion": "Una categoría de prueba"
})
categoria_id = resp.json()["categoria"]["id"]
print(f"✓ Categoría ID: {categoria_id}")

# 3. Buscar (sin documentos)
print("\n🔍 Buscando documentos...")
resp = requests.get(
    f"{BASE_URL}/busca/buscar?q=test",
    headers={"Authorization": f"Bearer {token}"}
)
print(f"✓ Resultados encontrados: {resp.json()['total']}")

print("\n✅ Pruebas completadas!")
```

Ejecuta:
```bash
python test_api.py
```

---

## 🗂️ Estructura de Carpetas Creadas

```
FlaskRecuperacionInformacion/
├── app.py                          # Punto de entrada
├── cli.py                          # Comandos CLI
├── run.sh                          # Script de ejecución
├── requirements.txt                # Dependencias
├── .env                           # Variables de entorno (NO VERSIONAR)
├── .env.example                   # Plantilla de variables
├── ENDPOINTS.md                   # Documentación completa de API
├── QUICK_START.md                 # Esta guía
├── backend/
│   ├── __init__.py               # Factory de aplicación
│   ├── config.py                 # Configuración
│   ├── models.py                 # Modelos SQLAlchemy
│   ├── services/
│   │   ├── auth.py              # Autenticación y usuarios
│   │   ├── documento.py         # Gestión de documentos
│   │   ├── busca.py             # Búsqueda y palabras clave
│   │   ├── categoria.py         # Categorías y etiquetas
│   │   └── recomendacion.py     # Recomendaciones
│   └── blueprints/
│       ├── auth/                # Endpoints de autenticación
│       ├── documentos/          # Endpoints de documentos
│       ├── busca/               # Endpoints de búsqueda
│       ├── categorias/          # Endpoints de categorías/etiquetas
│       └── recomendaciones/     # Endpoints de recomendaciones
├── uploads/                      # Archivos subidos (crear automáticamente)
├── templates/                    # Plantillas HTML (futuro)
└── static/                       # Archivos estáticos (futuro)
```

---

## 🔑 Endpoints Principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/registro` | Registrar usuario |
| POST | `/api/auth/login` | Iniciar sesión |
| POST | `/api/documentos/subir` | Subir documento |
| GET | `/api/documentos/mis-documentos` | Mis documentos |
| GET | `/api/busca/buscar` | Buscar documentos |
| GET | `/api/categorias` | Listar categorías |
| POST | `/api/recomendaciones/documento/{id}/generar` | Generar recomendaciones |

👉 Ver `ENDPOINTS.md` para documentación completa

---

## 🐛 Solución de Problemas

### Error: `No module named 'backend'`
```bash
# Asegurate de estar en el directorio raíz del proyecto
pwd
# Debe mostrar: .../backendProyecto
```

### Error: `database connection refused`
```bash
# Verifica que PostgreSQL esté corriendo
# Macbook: brew services start postgresql
# Linux: sudo service postgresql start
# Windows: Inicia PostgreSQL desde Services
```

### Error: `SQLALCHEMY_DATABASE_URI not set`
```bash
# Crea el archivo .env
cp .env.example .env
# Edita .env con tus credenciales PostgreSQL
```

### Error al subir archivo
```bash
# Crear carpeta uploads
mkdir -p uploads
chmod 755 uploads
```

---

## 📚 Próximos Pasos

1. **Frontend**: Crear interfaz web con React/Vue para consumir la API
2. **Procesamiento de Contenido**: Implementar OCR para imágenes y PDFs
3. **Búsqueda Avanzada**: Integrar Elasticsearch para búsqueda full-text
4. **Deploy**: Configurar Docker y CI/CD
5. **Tests**: Agregar pruebas unitarias e integración

---

## 💬 Soporte

Para más información:
- 📖 Lee `ENDPOINTS.md`
- 🔧 Revisa `backend/config.py`
- 📝 Consulta `backend/models.py` para el esquema de BD

¡Listo para comenzar! 🎉
