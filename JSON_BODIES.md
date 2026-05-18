# 📋 JSON BODIES PARA TODOS LOS ENDPOINTS

## 🔐 AUTENTICACIÓN

### POST /api/auth/registro
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "password": "Password123!"
}
```

### POST /api/auth/login
```json
{
  "email": "juan@example.com",
  "password": "Password123!"
}
```

### PUT /api/auth/perfil
```json
{
  "nombre": "Juan Carlos Pérez"
}
```

### POST /api/auth/cambiar-password
```json
{
  "password_antigua": "Password123!",
  "password_nueva": "NewPassword456!"
}
```

---

## 📂 CATEGORÍAS

### POST /api/categorias - Crear Categoría
```json
{
  "nombre": "Documentos Administrativos",
  "descripcion": "Categoría para documentos administrativos"
}
```

### POST /api/categorias - Crear Subcategoría
```json
{
  "nombre": "Contratos",
  "descripcion": "Contratos y acuerdos",
  "categoria_padre": 1
}
```

### PUT /api/categorias/{id}
```json
{
  "nombre": "Documentos Legales",
  "descripcion": "Todos los documentos legales de la empresa"
}
```

---

## 🏷️ ETIQUETAS

### POST /api/etiquetas - Crear Etiqueta
```json
{
  "nombre": "Importante",
  "color": "#FF0000"
}
```

### POST /api/etiquetas - Etiqueta Urgente
```json
{
  "nombre": "Urgente",
  "color": "#FFA500"
}
```

### POST /api/etiquetas - Etiqueta Revisado
```json
{
  "nombre": "Revisado",
  "color": "#00FF00"
}
```

### POST /api/etiquetas - Etiqueta En Proceso
```json
{
  "nombre": "En Proceso",
  "color": "#0000FF"
}
```

### PUT /api/etiquetas/{id}
```json
{
  "nombre": "Muy Importante",
  "color": "#8B0000"
}
```

---

## 📄 DOCUMENTOS

### POST /api/documentos/subir (Form-Data - NO JSON)
```
Form Data:
- archivo: [archivo binario]
- titulo: "Documento de Prueba"
- descripcion: "Un documento para probar el sistema"
- categoria_id: 1
- es_publico: true
```

**Equivalente en JSON (para referencia):**
```json
{
  "titulo": "Documento de Prueba",
  "descripcion": "Un documento para probar el sistema",
  "categoria_id": 1,
  "es_publico": true,
  "archivo": "binary_file_data"
}
```

### PUT /api/documentos/{id}
```json
{
  "titulo": "Documento de Prueba Actualizado",
  "descripcion": "Descripción actualizada",
  "es_publico": false
}
```

### POST /api/documentos/{id}/palabras-clave
```json
{
  "palabras": [
    "documento",
    "prueba",
    "sistema",
    "test",
    "importante"
  ]
}
```

### POST /api/documentos/{id}/etiquetas
```json
{
  "etiqueta_id": 1
}
```

---

## 🔍 BÚSQUEDA

### POST /api/busca/buscar - Búsqueda Simple
```json
{
  "termino": "python"
}
```

### POST /api/busca/buscar - Búsqueda Avanzada
```json
{
  "termino": "sistema",
  "filtros": {
    "categoria_id": 1,
    "tipo": "documento"
  }
}
```

### POST /api/busca/etiquetas
```json
{
  "etiqueta_ids": [1, 2, 3]
}
```

---

## 💡 RECOMENDACIONES

### POST /api/recomendaciones/documento/{id}/generar - TF-IDF
```json
{
  "limite": 5,
  "algoritmo": "tfidf"
}
```

### POST /api/recomendaciones/documento/{id}/generar - Por Categoría
```json
{
  "limite": 5,
  "algoritmo": "categoria"
}
```

---

## 🔄 FLUJO COMPLETO CON TODOS LOS BODIES

### 1. Registro
```json
{
  "nombre": "Test User",
  "email": "test@example.com",
  "password": "TestPass123!"
}
```
**Respuesta guardada:** TOKEN, USER_ID

### 2. Crear Categoría
```json
{
  "nombre": "Documentos",
  "descripcion": "Categoría de documentos"
}
```
**Respuesta guardada:** CATEGORIA_ID = 1

### 3. Crear Etiqueta
```json
{
  "nombre": "Importante",
  "color": "#FF0000"
}
```
**Respuesta guardada:** ETIQUETA_ID = 1

### 4. Subir Documento (Form-Data)
```
multipart/form-data:
- archivo: documento.txt
- titulo: "Mi Documento"
- descripcion: "Descripción del documento"
- categoria_id: 1
- es_publico: true
```
**Respuesta guardada:** DOCUMENTO_ID

### 5. Agregar Palabras Clave
```json
{
  "palabras": [
    "documento",
    "prueba",
    "sistema",
    "búsqueda",
    "información"
  ]
}
```

### 6. Agregar Etiqueta
```json
{
  "etiqueta_id": 1
}
```

### 7. Buscar
```json
{
  "termino": "documento",
  "filtros": {
    "categoria_id": 1
  }
}
```

### 8. Generar Recomendaciones
```json
{
  "limite": 5,
  "algoritmo": "tfidf"
}
```

---

## 📊 RESUMEN RÁPIDO POR TIPO

### POST Bodies (Crear)
```json
{
  "nombre": "string",
  "descripcion": "string",
  "email": "string",
  "password": "string",
  "color": "#XXXXXX",
  "titulo": "string",
  "palabras": ["string"],
  "etiqueta_id": 1,
  "categoria_id": 1,
  "etiqueta_ids": [1, 2, 3],
  "termino": "string",
  "filtros": {},
  "limite": 5,
  "algoritmo": "tfidf"
}
```

### PUT Bodies (Actualizar)
```json
{
  "nombre": "string",
  "email": "string",
  "descripcion": "string",
  "titulo": "string",
  "color": "#XXXXXX",
  "es_publico": true,
  "password_antigua": "string",
  "password_nueva": "string"
}
```

### Tipos de Campos
```json
{
  "id": "UUID o integer",
  "nombre": "string",
  "email": "string válido",
  "password": "string seguro",
  "descripcion": "string",
  "titulo": "string",
  "color": "#XXXXXX (hex color)",
  "es_publico": true,
  "categoria_id": 1,
  "etiqueta_id": 1,
  "etiqueta_ids": [1, 2, 3],
  "palabras": ["palabra1", "palabra2"],
  "termino": "string",
  "filtros": {
    "categoria_id": 1,
    "tipo": "texto"
  },
  "limite": 5,
  "algoritmo": "tfidf"
}
```

---

## 🔗 HEADERS REQUERIDOS

### Para solicitudes autenticadas (con TOKEN)
```json
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "Content-Type": "application/json"
}
```

### Para solicitudes normales
```json
{
  "Content-Type": "application/json"
}
```

### Para subir archivos (multipart)
```
Content-Type: multipart/form-data
Authorization: Bearer TOKEN
```

---

## 📝 EJEMPLOS LISTOS PARA COPIAR/PEGAR

### Ejemplo 1: Flujo Completo Mínimo
```bash
# 1. Registrarse
curl -X POST http://localhost:5000/api/auth/registro \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test","email":"test@example.com","password":"Pass123!"}'

# Guardar TOKEN de respuesta

# 2. Crear categoría
curl -X POST http://localhost:5000/api/categorias \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Docs","descripcion":"Documentos"}'

# Guardar CATEGORIA_ID=1

# 3. Crear etiqueta
curl -X POST http://localhost:5000/api/etiquetas \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Importante","color":"#FF0000"}'

# Guardar ETIQUETA_ID=1

# 4. Subir documento
curl -X POST http://localhost:5000/api/documentos/subir \
  -H "Authorization: Bearer TOKEN" \
  -F "archivo=@documento.txt" \
  -F "titulo=Mi Doc" \
  -F "categoria_id=1" \
  -F "es_publico=true"

# Guardar DOCUMENTO_ID

# 5. Agregar palabras clave
curl -X POST http://localhost:5000/api/documentos/DOCUMENTO_ID/palabras-clave \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"palabras":["documento","prueba","sistema"]}'

# 6. Buscar
curl -X GET "http://localhost:5000/api/busca/buscar?q=documento" \
  -H "Authorization: Bearer TOKEN"

# 7. Generar recomendaciones
curl -X POST http://localhost:5000/api/recomendaciones/documento/DOCUMENTO_ID/generar \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"limite":5,"algoritmo":"tfidf"}'
```

---

## ✅ CHECKLIST DE BODIES

### Autenticación
- [x] POST registro
- [x] POST login
- [x] PUT perfil
- [x] POST cambiar-password

### Estructura
- [x] POST categorías
- [x] PUT categorías
- [x] POST etiquetas
- [x] PUT etiquetas

### Documentos
- [x] POST subir (form-data)
- [x] PUT actualizar
- [x] POST palabras-clave
- [x] POST etiquetas

### Búsqueda
- [x] POST buscar simple
- [x] POST buscar avanzada
- [x] POST buscar etiquetas

### Recomendaciones
- [x] POST generar TF-IDF
- [x] POST generar categoría

---

¡Todos los JSON bodies listos para copiar! 📋

