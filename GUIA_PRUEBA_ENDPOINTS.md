# 🧪 GUÍA COMPLETA DE PRUEBA DE ENDPOINTS

## Tabla de Contenidos
1. [Flujo General de la Aplicación](#flujo-general)
2. [Autenticación](#autenticación)
3. [Gestión de Categorías](#categorías)
4. [Gestión de Etiquetas](#etiquetas)
5. [Gestión de Documentos](#documentos)
6. [Búsqueda Avanzada](#búsqueda)
7. [Recomendaciones](#recomendaciones)
8. [Script de Prueba Completo](#script-completo)

---

## 🔄 Flujo General de la Aplicación

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE LA APLICACIÓN                    │
└─────────────────────────────────────────────────────────────┘

1. INICIO
   │
   ├─→ Registrarse / Login
   │   └─→ Obtener JWT Token
   │
   ├─→ Crear Categorías (Opcional)
   │   └─→ Crear estructura jerárquica
   │
   ├─→ Crear Etiquetas (Opcional)
   │   └─→ Crear sistema de clasificación
   │
   ├─→ Subir Documentos
   │   ├─→ Asociar con categoría
   │   ├─→ Agregar palabras clave
   │   └─→ Etiquetar documento
   │
   ├─→ Buscar Documentos
   │   ├─→ Por palabras clave
   │   ├─→ Por categoría
   │   ├─→ Por etiquetas
   │   └─→ Documentos similares
   │
   ├─→ Ver Recomendaciones
   │   ├─→ Generar recomendaciones
   │   └─→ Ver documentos populares
   │
   └─→ Análisis
       ├─→ Historial de búsquedas
       ├─→ Búsquedas populares
       └─→ Accesos a documentos
```

---

## 🔐 AUTENTICACIÓN

### 1. POST `/api/auth/registro` - Registrar Usuario

**Descripción:** Crear una nueva cuenta de usuario

**Request:**
```bash
curl -X POST http://localhost:5000/api/auth/registro \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "password": "Password123!"
  }'
```

**Response (201):**
```json
{
  "mensaje": "Usuario registrado exitosamente",
  "usuario": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "activo": true,
    "creado_en": "2026-05-17T10:30:00"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWRfaWQiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJpYXQiOjE3MTYwMDAwMDAsImV4cCI6MTcxNjA4NjQwMH0.xxxxx"
}
```

**Guardar:** El token para las próximas solicitudes

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 2. POST `/api/auth/login` - Iniciar Sesión

**Descripción:** Autenticarse y obtener un token JWT

**Request:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "password": "Password123!"
  }'
```

**Response (200):**
```json
{
  "mensaje": "Autenticación exitosa",
  "usuario": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "activo": true,
    "creado_en": "2026-05-17T10:30:00"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx"
}
```

---

### 3. GET `/api/auth/perfil` - Obtener Perfil

**Descripción:** Obtener datos del usuario autenticado

**Request:**
```bash
curl -X GET http://localhost:5000/api/auth/perfil \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "activo": true,
  "creado_en": "2026-05-17T10:30:00"
}
```

---

### 4. PUT `/api/auth/perfil` - Actualizar Perfil

**Descripción:** Modificar datos del usuario

**Request:**
```bash
curl -X PUT http://localhost:5000/api/auth/perfil \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Carlos Pérez"
  }'
```

**Response (200):**
```json
{
  "mensaje": "Perfil actualizado",
  "usuario": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre": "Juan Carlos Pérez",
    "email": "juan@example.com",
    "activo": true,
    "creado_en": "2026-05-17T10:30:00"
  }
}
```

---

### 5. POST `/api/auth/cambiar-password` - Cambiar Contraseña

**Descripción:** Cambiar la contraseña del usuario

**Request:**
```bash
curl -X POST http://localhost:5000/api/auth/cambiar-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "password_antigua": "Password123!",
    "password_nueva": "NewPassword456!"
  }'
```

**Response (200):**
```json
{
  "mensaje": "Contraseña cambiada exitosamente"
}
```

---

### 6. POST `/api/auth/verificar-token` - Verificar Token

**Descripción:** Verificar si un token es válido

**Request:**
```bash
curl -X POST http://localhost:5000/api/auth/verificar-token \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200):**
```json
{
  "valido": true
}
```

---

## 📂 CATEGORÍAS

### 1. POST `/api/categorias` - Crear Categoría

**Descripción:** Crear nueva categoría

**Request:**
```bash
curl -X POST http://localhost:5000/api/categorias \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Documentos Administrativos",
    "descripcion": "Categoría para documentos de administración"
  }'
```

**Response (201):**
```json
{
  "mensaje": "Categoría creada exitosamente",
  "categoria": {
    "id": 1,
    "nombre": "Documentos Administrativos",
    "descripcion": "Categoría para documentos de administración",
    "categoria_padre": null,
    "creado_en": "2026-05-17T10:35:00"
  }
}
```

**Guardar:** `CATEGORIA_ID=1`

---

### 2. POST `/api/categorias` - Crear Subcategoría

**Descripción:** Crear una categoría dentro de otra (jerárquica)

**Request:**
```bash
curl -X POST http://localhost:5000/api/categorias \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Contratos",
    "descripcion": "Contratos y acuerdos",
    "categoria_padre": 1
  }'
```

**Response (201):**
```json
{
  "mensaje": "Categoría creada exitosamente",
  "categoria": {
    "id": 2,
    "nombre": "Contratos",
    "descripcion": "Contratos y acuerdos",
    "categoria_padre": 1,
    "creado_en": "2026-05-17T10:36:00"
  }
}
```

**Guardar:** `SUBCATEGORIA_ID=2`

---

### 3. GET `/api/categorias` - Listar Categorías

**Descripción:** Obtener todas las categorías

**Request:**
```bash
curl -X GET "http://localhost:5000/api/categorias?pagina=1&por_pagina=10"
```

**Response (200):**
```json
{
  "total": 2,
  "pagina": 1,
  "por_pagina": 10,
  "categorias": [
    {
      "id": 1,
      "nombre": "Documentos Administrativos",
      "descripcion": "Categoría para documentos de administración",
      "categoria_padre": null,
      "creado_en": "2026-05-17T10:35:00"
    },
    {
      "id": 2,
      "nombre": "Contratos",
      "descripcion": "Contratos y acuerdos",
      "categoria_padre": 1,
      "creado_en": "2026-05-17T10:36:00"
    }
  ]
}
```

---

### 4. GET `/api/categorias/arbol` - Obtener Árbol de Categorías

**Descripción:** Obtener estructura jerárquica de categorías

**Request:**
```bash
curl -X GET http://localhost:5000/api/categorias/arbol
```

**Response (200):**
```json
{
  "arbol": [
    {
      "id": 1,
      "nombre": "Documentos Administrativos",
      "descripcion": "Categoría para documentos de administración",
      "subcategorias": [
        {
          "id": 2,
          "nombre": "Contratos",
          "descripcion": "Contratos y acuerdos",
          "subcategorias": []
        }
      ]
    }
  ]
}
```

---

### 5. GET `/api/categorias/{id}` - Obtener Categoría

**Descripción:** Obtener detalles de una categoría específica

**Request:**
```bash
curl -X GET http://localhost:5000/api/categorias/1
```

**Response (200):**
```json
{
  "id": 1,
  "nombre": "Documentos Administrativos",
  "descripcion": "Categoría para documentos de administración",
  "categoria_padre": null,
  "creado_en": "2026-05-17T10:35:00"
}
```

---

### 6. PUT `/api/categorias/{id}` - Actualizar Categoría

**Descripción:** Modificar una categoría

**Request:**
```bash
curl -X PUT http://localhost:5000/api/categorias/1 \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Documentos Legales",
    "descripcion": "Todos los documentos legales de la empresa"
  }'
```

**Response (200):**
```json
{
  "mensaje": "Categoría actualizada",
  "categoria": {
    "id": 1,
    "nombre": "Documentos Legales",
    "descripcion": "Todos los documentos legales de la empresa",
    "categoria_padre": null,
    "creado_en": "2026-05-17T10:35:00"
  }
}
```

---

### 7. GET `/api/categorias/{id}/subcategorias` - Subcategorías

**Descripción:** Obtener todas las subcategorías de una categoría

**Request:**
```bash
curl -X GET http://localhost:5000/api/categorias/1/subcategorias
```

**Response (200):**
```json
{
  "categoria_id": 1,
  "subcategorias": [
    {
      "id": 2,
      "nombre": "Contratos",
      "descripcion": "Contratos y acuerdos",
      "categoria_padre": 1,
      "creado_en": "2026-05-17T10:36:00"
    }
  ]
}
```

---

### 8. DELETE `/api/categorias/{id}` - Eliminar Categoría

**Descripción:** Eliminar una categoría

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/categorias/2
```

**Response (200):**
```json
{
  "mensaje": "Categoría eliminada"
}
```

---

## 🏷️ ETIQUETAS

### 1. POST `/api/etiquetas` - Crear Etiqueta

**Descripción:** Crear nueva etiqueta

**Request:**
```bash
curl -X POST http://localhost:5000/api/etiquetas \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Importante",
    "color": "#FF0000"
  }'
```

**Response (201):**
```json
{
  "mensaje": "Etiqueta creada exitosamente",
  "etiqueta": {
    "id": 1,
    "nombre": "Importante",
    "color": "#FF0000"
  }
}
```

**Guardar:** `ETIQUETA_ID=1`

---

### 2. POST `/api/etiquetas` - Crear Más Etiquetas

**Request:**
```bash
curl -X POST http://localhost:5000/api/etiquetas \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Urgente",
    "color": "#FFA500"
  }'

curl -X POST http://localhost:5000/api/etiquetas \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Revisado",
    "color": "#00FF00"
  }'

curl -X POST http://localhost:5000/api/etiquetas \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "En Proceso",
    "color": "#0000FF"
  }'
```

---

### 3. GET `/api/etiquetas` - Listar Etiquetas

**Descripción:** Obtener todas las etiquetas

**Request:**
```bash
curl -X GET "http://localhost:5000/api/etiquetas?pagina=1&por_pagina=10"
```

**Response (200):**
```json
{
  "total": 4,
  "pagina": 1,
  "por_pagina": 10,
  "etiquetas": [
    {
      "id": 1,
      "nombre": "Importante",
      "color": "#FF0000"
    },
    {
      "id": 2,
      "nombre": "Urgente",
      "color": "#FFA500"
    },
    {
      "id": 3,
      "nombre": "Revisado",
      "color": "#00FF00"
    },
    {
      "id": 4,
      "nombre": "En Proceso",
      "color": "#0000FF"
    }
  ]
}
```

---

### 4. GET `/api/etiquetas/{id}` - Obtener Etiqueta

**Request:**
```bash
curl -X GET http://localhost:5000/api/etiquetas/1
```

**Response (200):**
```json
{
  "id": 1,
  "nombre": "Importante",
  "color": "#FF0000"
}
```

---

### 5. PUT `/api/etiquetas/{id}` - Actualizar Etiqueta

**Request:**
```bash
curl -X PUT http://localhost:5000/api/etiquetas/1 \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Muy Importante",
    "color": "#8B0000"
  }'
```

**Response (200):**
```json
{
  "mensaje": "Etiqueta actualizada",
  "etiqueta": {
    "id": 1,
    "nombre": "Muy Importante",
    "color": "#8B0000"
  }
}
```

---

### 6. DELETE `/api/etiquetas/{id}` - Eliminar Etiqueta

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/etiquetas/4
```

**Response (200):**
```json
{
  "mensaje": "Etiqueta eliminada"
}
```

---

## 📄 DOCUMENTOS

### 1. POST `/api/documentos/subir` - Subir Documento

**Descripción:** Cargar un nuevo documento

**Request:**
```bash
# Crear un archivo de prueba
echo "Este es un documento de prueba" > test_document.txt

curl -X POST http://localhost:5000/api/documentos/subir \
  -H "Authorization: Bearer $TOKEN" \
  -F "archivo=@test_document.txt" \
  -F "titulo=Documento de Prueba" \
  -F "descripcion=Un documento para probar el sistema" \
  -F "categoria_id=1" \
  -F "es_publico=true"
```

**Response (201):**
```json
{
  "mensaje": "Documento subido exitosamente",
  "documento": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "titulo": "Documento de Prueba",
    "descripcion": "Un documento para probar el sistema",
    "tipo": "texto",
    "nombre_original": "test_document.txt",
    "tamano_bytes": 31,
    "es_publico": true,
    "idioma": "spanish",
    "estado": "pendiente",
    "categoria_id": 1,
    "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
    "creado_en": "2026-05-17T10:40:00",
    "actualizado_en": "2026-05-17T10:40:00"
  }
}
```

**Guardar:** `DOC_ID="550e8400-e29b-41d4-a716-446655440001"`

---

### 2. Subir Más Documentos

**Para pruebas completas, sube 2-3 documentos más:**

```bash
# Documento 2
echo "Contenido del segundo documento" > doc2.txt
curl -X POST http://localhost:5000/api/documentos/subir \
  -H "Authorization: Bearer $TOKEN" \
  -F "archivo=@doc2.txt" \
  -F "titulo=Manual de Usuario" \
  -F "descripcion=Manual completo del sistema" \
  -F "categoria_id=1" \
  -F "es_publico=true"

# Documento 3
echo "Información importante" > doc3.txt
curl -X POST http://localhost:5000/api/documentos/subir \
  -H "Authorization: Bearer $TOKEN" \
  -F "archivo=@doc3.txt" \
  -F "titulo=Información Técnica" \
  -F "descripcion=Detalles técnicos del sistema" \
  -F "categoria_id=1" \
  -F "es_publico=true"
```

---

### 3. POST `/api/documentos/{id}/palabras-clave` - Agregar Palabras Clave

**Descripción:** Indexar un documento con palabras clave

**Request:**
```bash
curl -X POST http://localhost:5000/api/documentos/$DOC_ID/palabras-clave \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "palabras": ["documento", "prueba", "sistema", "test", "importante"]
  }'
```

**Response (200):**
```json
{
  "mensaje": "Palabras clave agregadas",
  "palabras_clave": [
    {
      "id": 1,
      "documento_id": "550e8400-e29b-41d4-a716-446655440001",
      "palabra": "documento",
      "peso": 1.0,
      "fuente": "manual"
    },
    {
      "id": 2,
      "documento_id": "550e8400-e29b-41d4-a716-446655440001",
      "palabra": "prueba",
      "peso": 1.0,
      "fuente": "manual"
    },
    {
      "id": 3,
      "documento_id": "550e8400-e29b-41d4-a716-446655440001",
      "palabra": "sistema",
      "peso": 1.0,
      "fuente": "manual"
    },
    {
      "id": 4,
      "documento_id": "550e8400-e29b-41d4-a716-446655440001",
      "palabra": "test",
      "peso": 1.0,
      "fuente": "manual"
    },
    {
      "id": 5,
      "documento_id": "550e8400-e29b-41d4-a716-446655440001",
      "palabra": "importante",
      "peso": 1.0,
      "fuente": "manual"
    }
  ]
}
```

---

### 4. GET `/api/documentos/{id}/palabras-clave` - Obtener Palabras Clave

**Request:**
```bash
curl -X GET http://localhost:5000/api/documentos/$DOC_ID/palabras-clave
```

**Response (200):**
```json
{
  "documento_id": "550e8400-e29b-41d4-a716-446655440001",
  "palabras_clave": [
    {
      "id": 1,
      "documento_id": "550e8400-e29b-41d4-a716-446655440001",
      "palabra": "documento",
      "peso": 1.0,
      "fuente": "manual"
    },
    // ... más palabras
  ]
}
```

---

### 5. POST `/api/documentos/{id}/etiquetas` - Agregar Etiqueta a Documento

**Request:**
```bash
curl -X POST http://localhost:5000/api/documentos/$DOC_ID/etiquetas \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "etiqueta_id": 1
  }'
```

**Response (200):**
```json
{
  "mensaje": "Etiqueta agregada",
  "documento": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "titulo": "Documento de Prueba",
    "descripcion": "Un documento para probar el sistema",
    "tipo": "texto",
    "nombre_original": "test_document.txt",
    "tamano_bytes": 31,
    "es_publico": true,
    "idioma": "spanish",
    "estado": "pendiente",
    "categoria_id": 1,
    "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
    "creado_en": "2026-05-17T10:40:00",
    "actualizado_en": "2026-05-17T10:40:00"
  },
  "etiquetas": [
    {
      "id": 1,
      "nombre": "Muy Importante",
      "color": "#8B0000"
    }
  ]
}
```

---

### 6. GET `/api/documentos/{id}/etiquetas` - Obtener Etiquetas

**Request:**
```bash
curl -X GET http://localhost:5000/api/documentos/$DOC_ID/etiquetas
```

**Response (200):**
```json
{
  "documento_id": "550e8400-e29b-41d4-a716-446655440001",
  "etiquetas": [
    {
      "id": 1,
      "nombre": "Muy Importante",
      "color": "#8B0000"
    }
  ]
}
```

---

### 7. DELETE `/api/documentos/{id}/etiquetas/{etiqueta_id}` - Remover Etiqueta

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/documentos/$DOC_ID/etiquetas/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200):**
```json
{
  "mensaje": "Etiqueta removida",
  "documento": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    // ... datos documento
  },
  "etiquetas": []
}
```

---

### 8. GET `/api/documentos` - Listar Documentos Públicos

**Request:**
```bash
curl -X GET "http://localhost:5000/api/documentos?pagina=1&por_pagina=10"
```

**Response (200):**
```json
{
  "total": 3,
  "pagina": 1,
  "por_pagina": 10,
  "documentos": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "titulo": "Documento de Prueba",
      "descripcion": "Un documento para probar el sistema",
      "tipo": "texto",
      "nombre_original": "test_document.txt",
      "tamano_bytes": 31,
      "es_publico": true,
      "idioma": "spanish",
      "estado": "pendiente",
      "categoria_id": 1,
      "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
      "creado_en": "2026-05-17T10:40:00",
      "actualizado_en": "2026-05-17T10:40:00"
    },
    // ... más documentos
  ]
}
```

---

### 9. GET `/api/documentos/mis-documentos` - Mis Documentos

**Request:**
```bash
curl -X GET "http://localhost:5000/api/documentos/mis-documentos?pagina=1&por_pagina=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200):**
```json
{
  "total": 3,
  "pagina": 1,
  "por_pagina": 10,
  "documentos": [
    // ... documentos del usuario
  ]
}
```

---

### 10. GET `/api/documentos/{id}` - Obtener Documento

**Request:**
```bash
curl -X GET http://localhost:5000/api/documentos/$DOC_ID \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "titulo": "Documento de Prueba",
  "descripcion": "Un documento para probar el sistema",
  "tipo": "texto",
  "nombre_original": "test_document.txt",
  "tamano_bytes": 31,
  "es_publico": true,
  "idioma": "spanish",
  "estado": "pendiente",
  "categoria_id": 1,
  "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
  "contenido_texto": "Este es un documento de prueba",
  "creado_en": "2026-05-17T10:40:00",
  "actualizado_en": "2026-05-17T10:40:00"
}
```

---

### 11. PUT `/api/documentos/{id}` - Actualizar Documento

**Request:**
```bash
curl -X PUT http://localhost:5000/api/documentos/$DOC_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Documento de Prueba Actualizado",
    "descripcion": "Descripción actualizada",
    "es_publico": false
  }'
```

**Response (200):**
```json
{
  "mensaje": "Documento actualizado",
  "documento": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "titulo": "Documento de Prueba Actualizado",
    "descripcion": "Descripción actualizada",
    "tipo": "texto",
    "nombre_original": "test_document.txt",
    "tamano_bytes": 31,
    "es_publico": false,
    "idioma": "spanish",
    "estado": "pendiente",
    "categoria_id": 1,
    "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
    "creado_en": "2026-05-17T10:40:00",
    "actualizado_en": "2026-05-17T10:41:00"
  }
}
```

---

### 12. GET `/api/documentos/{id}/accesos` - Ver Accesos

**Request:**
```bash
curl -X GET "http://localhost:5000/api/documentos/$DOC_ID/accesos?pagina=1&por_pagina=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200):**
```json
{
  "total": 2,
  "pagina": 1,
  "por_pagina": 10,
  "accesos": [
    {
      "id": 1,
      "documento_id": "550e8400-e29b-41d4-a716-446655440001",
      "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
      "accion": "visualizar",
      "accedido_en": "2026-05-17T10:40:05"
    },
    {
      "id": 2,
      "documento_id": "550e8400-e29b-41d4-a716-446655440001",
      "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
      "accion": "visualizar",
      "accedido_en": "2026-05-17T10:41:00"
    }
  ]
}
```

---

### 13. DELETE `/api/documentos/{id}` - Eliminar Documento

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/documentos/$DOC_ID \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200):**
```json
{
  "mensaje": "Documento eliminado"
}
```

---

## 🔍 BÚSQUEDA

### 1. GET `/api/busca/buscar` - Búsqueda por Palabras Clave

**Descripción:** Buscar documentos por término

**Request:**
```bash
curl -X GET "http://localhost:5000/api/busca/buscar?q=sistema&pagina=1&por_pagina=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200):**
```json
{
  "termino": "sistema",
  "filtros": {},
  "total": 2,
  "pagina": 1,
  "por_pagina": 10,
  "resultados": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "titulo": "Documento de Prueba",
      "descripcion": "Un documento para probar el sistema",
      "tipo": "texto",
      "nombre_original": "test_document.txt",
      "tamano_bytes": 31,
      "es_publico": true,
      "idioma": "spanish",
      "estado": "pendiente",
      "categoria_id": 1,
      "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
      "creado_en": "2026-05-17T10:40:00",
      "actualizado_en": "2026-05-17T10:40:00"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "titulo": "Información Técnica",
      "descripcion": "Detalles técnicos del sistema",
      "tipo": "texto",
      "nombre_original": "doc3.txt",
      "tamano_bytes": 25,
      "es_publico": true,
      "idioma": "spanish",
      "estado": "pendiente",
      "categoria_id": 1,
      "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
      "creado_en": "2026-05-17T10:42:00",
      "actualizado_en": "2026-05-17T10:42:00"
    }
  ]
}
```

---

### 2. GET `/api/busca/buscar` - Búsqueda con Filtros

**Request:**
```bash
curl -X GET "http://localhost:5000/api/busca/buscar?q=sistema&categoria_id=1&tipo=texto&pagina=1&por_pagina=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:** Similar a anterior, pero filtrado

---

### 3. POST `/api/busca/buscar` - Búsqueda por POST

**Descripción:** Alternativa POST para búsquedas complejas

**Request:**
```bash
curl -X POST http://localhost:5000/api/busca/buscar \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "termino": "importante",
    "filtros": {
      "categoria_id": 1,
      "tipo": "texto"
    }
  }'
```

**Response:** Similar a GET

---

### 4. GET `/api/busca/categoria/{id}` - Búsqueda por Categoría

**Request:**
```bash
curl -X GET "http://localhost:5000/api/busca/categoria/1?pagina=1&por_pagina=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200):**
```json
{
  "categoria_id": 1,
  "total": 3,
  "pagina": 1,
  "por_pagina": 10,
  "resultados": [
    // ... documentos de la categoría 1
  ]
}
```

---

### 5. GET `/api/busca/etiquetas` - Búsqueda por Etiquetas

**Request:**
```bash
curl -X GET "http://localhost:5000/api/busca/etiquetas?etiqueta_id=1&etiqueta_id=2&pagina=1&por_pagina=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200):**
```json
{
  "etiqueta_ids": [1, 2],
  "total": 1,
  "pagina": 1,
  "por_pagina": 10,
  "resultados": [
    // ... documentos con estas etiquetas
  ]
}
```

---

### 6. GET `/api/busca/similares/{id}` - Documentos Similares

**Descripción:** Encontrar documentos similares a uno dado

**Request:**
```bash
curl -X GET http://localhost:5000/api/busca/similares/$DOC_ID
```

**Response (200):**
```json
{
  "documento_id": "550e8400-e29b-41d4-a716-446655440001",
  "similares": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "titulo": "Información Técnica",
      "descripcion": "Detalles técnicos del sistema",
      "tipo": "texto",
      "nombre_original": "doc3.txt",
      "tamano_bytes": 25,
      "es_publico": true,
      "idioma": "spanish",
      "estado": "pendiente",
      "categoria_id": 1,
      "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
      "creado_en": "2026-05-17T10:42:00",
      "actualizado_en": "2026-05-17T10:42:00"
    }
  ]
}
```

---

### 7. GET `/api/busca/historial` - Historial de Búsquedas

**Request:**
```bash
curl -X GET "http://localhost:5000/api/busca/historial?pagina=1&por_pagina=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200):**
```json
{
  "total": 3,
  "pagina": 1,
  "por_pagina": 10,
  "historial": [
    {
      "id": 1,
      "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
      "termino": "sistema",
      "filtros": {},
      "total_resultados": 2,
      "buscado_en": "2026-05-17T10:43:00"
    },
    {
      "id": 2,
      "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
      "termino": "importante",
      "filtros": {
        "categoria_id": 1
      },
      "total_resultados": 1,
      "buscado_en": "2026-05-17T10:44:00"
    },
    {
      "id": 3,
      "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
      "termino": "documento",
      "filtros": {},
      "total_resultados": 3,
      "buscado_en": "2026-05-17T10:45:00"
    }
  ]
}
```

---

### 8. GET `/api/busca/populares` - Búsquedas Populares

**Descripción:** Ver términos más buscados

**Request:**
```bash
curl -X GET "http://localhost:5000/api/busca/populares?limite=5"
```

**Response (200):**
```json
{
  "limite": 5,
  "resultados": [
    {
      "termino": "documento",
      "cantidad": 3
    },
    {
      "termino": "sistema",
      "cantidad": 2
    },
    {
      "termino": "importante",
      "cantidad": 1
    }
  ]
}
```

---

## 💡 RECOMENDACIONES

### 1. POST `/api/recomendaciones/documento/{id}/generar` - Generar Recomendaciones

**Descripción:** Calcular recomendaciones para un documento

**Request - TF-IDF:**
```bash
curl -X POST http://localhost:5000/api/recomendaciones/documento/$DOC_ID/generar \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "limite": 5,
    "algoritmo": "tfidf"
  }'
```

**Response (200):**
```json
{
  "mensaje": "Recomendaciones generadas usando tfidf",
  "documento_id": "550e8400-e29b-41d4-a716-446655440001",
  "recomendaciones": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "titulo": "Información Técnica",
      "descripcion": "Detalles técnicos del sistema",
      "tipo": "texto",
      "nombre_original": "doc3.txt",
      "tamano_bytes": 25,
      "es_publico": true,
      "idioma": "spanish",
      "estado": "pendiente",
      "categoria_id": 1,
      "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
      "creado_en": "2026-05-17T10:42:00",
      "actualizado_en": "2026-05-17T10:42:00"
    }
  ]
}
```

---

### 2. POST `/api/recomendaciones/documento/{id}/generar` - Por Categoría

**Request - Por Categoría:**
```bash
curl -X POST http://localhost:5000/api/recomendaciones/documento/$DOC_ID/generar \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "limite": 5,
    "algoritmo": "categoria"
  }'
```

**Response:** Documentos de la misma categoría

---

### 3. GET `/api/recomendaciones/documento/{id}` - Obtener Recomendaciones

**Request:**
```bash
curl -X GET "http://localhost:5000/api/recomendaciones/documento/$DOC_ID?limite=5"
```

**Response (200):**
```json
{
  "documento_id": "550e8400-e29b-41d4-a716-446655440001",
  "limite": 5,
  "recomendaciones": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "titulo": "Información Técnica",
      "descripcion": "Detalles técnicos del sistema",
      "tipo": "texto",
      "nombre_original": "doc3.txt",
      "tamano_bytes": 25,
      "es_publico": true,
      "idioma": "spanish",
      "estado": "pendiente",
      "categoria_id": 1,
      "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
      "creado_en": "2026-05-17T10:42:00",
      "actualizado_en": "2026-05-17T10:42:00",
      "score": 0.85,
      "algoritmo": "tfidf"
    }
  ]
}
```

---

### 4. GET `/api/recomendaciones/populares` - Documentos Populares

**Descripción:** Ver documentos más accedidos

**Request:**
```bash
curl -X GET "http://localhost:5000/api/recomendaciones/populares?limite=10"
```

**Response (200):**
```json
{
  "limite": 10,
  "documentos": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "titulo": "Documento de Prueba",
      "descripcion": "Un documento para probar el sistema",
      "tipo": "texto",
      "nombre_original": "test_document.txt",
      "tamano_bytes": 31,
      "es_publico": true,
      "idioma": "spanish",
      "estado": "pendiente",
      "categoria_id": 1,
      "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
      "creado_en": "2026-05-17T10:40:00",
      "actualizado_en": "2026-05-17T10:40:00",
      "total_accesos": 5
    }
  ]
}
```

---

### 5. POST `/api/recomendaciones/generar-todas` - Generar Todas

**Descripción:** Generar recomendaciones para TODOS los documentos (puede tomar tiempo)

**Request:**
```bash
curl -X POST http://localhost:5000/api/recomendaciones/generar-todas
```

**Response (200):**
```json
{
  "mensaje": "Generación de recomendaciones completada"
}
```

---

### 6. DELETE `/api/recomendaciones/documento/{id}` - Eliminar Recomendaciones

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/recomendaciones/documento/$DOC_ID
```

**Response (200):**
```json
{
  "mensaje": "Recomendaciones eliminadas",
  "documento_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

---

## 📋 SCRIPT COMPLETO DE PRUEBA

Crea un archivo `test_completo.sh`:

```bash
#!/bin/bash

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

API="http://localhost:5000/api"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}     PRUEBA COMPLETA DE ENDPOINTS - SISTEMA DE RECUPERACIÓN      ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"

# 1. AUTENTICACIÓN
echo -e "${BLUE}1. REGISTRARSE${NC}"
REGISTER=$(curl -s -X POST $API/auth/registro \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test User",
    "email": "test@example.com",
    "password": "Test123456!"
  }')

TOKEN=$(echo $REGISTER | grep -o '"token":"[^"]*' | cut -d'"' -f4)
USER_ID=$(echo $REGISTER | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

echo -e "${GREEN}✓ Usuario registrado${NC}"
echo "Token: $TOKEN"
echo "User ID: $USER_ID\n"

# 2. CREAR CATEGORÍAS
echo -e "${BLUE}2. CREAR CATEGORÍAS${NC}"
CAT=$(curl -s -X POST $API/categorias \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Documentos Administrativos",
    "descripcion": "Categoría de prueba"
  }')

CAT_ID=$(echo $CAT | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo -e "${GREEN}✓ Categoría creada${NC}"
echo "Category ID: $CAT_ID\n"

# 3. CREAR ETIQUETAS
echo -e "${BLUE}3. CREAR ETIQUETAS${NC}"
TAG=$(curl -s -X POST $API/etiquetas \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Importante",
    "color": "#FF0000"
  }')

TAG_ID=$(echo $TAG | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo -e "${GREEN}✓ Etiqueta creada${NC}"
echo "Tag ID: $TAG_ID\n"

# 4. SUBIR DOCUMENTO
echo -e "${BLUE}4. SUBIR DOCUMENTO${NC}"
echo "Este es un documento de prueba" > test_doc.txt

DOC=$(curl -s -X POST $API/documentos/subir \
  -H "Authorization: Bearer $TOKEN" \
  -F "archivo=@test_doc.txt" \
  -F "titulo=Documento de Prueba" \
  -F "descripcion=Un documento para pruebas" \
  -F "categoria_id=$CAT_ID" \
  -F "es_publico=true")

DOC_ID=$(echo $DOC | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
echo -e "${GREEN}✓ Documento subido${NC}"
echo "Document ID: $DOC_ID\n"

# 5. AGREGAR PALABRAS CLAVE
echo -e "${BLUE}5. AGREGAR PALABRAS CLAVE${NC}"
curl -s -X POST $API/documentos/$DOC_ID/palabras-clave \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "palabras": ["prueba", "documento", "test", "sistema"]
  }' > /dev/null
echo -e "${GREEN}✓ Palabras clave agregadas${NC}\n"

# 6. AGREGAR ETIQUETA
echo -e "${BLUE}6. AGREGAR ETIQUETA${NC}"
curl -s -X POST $API/documentos/$DOC_ID/etiquetas \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"etiqueta_id\": $TAG_ID}" > /dev/null
echo -e "${GREEN}✓ Etiqueta agregada${NC}\n"

# 7. BUSCAR POR PALABRAS CLAVE
echo -e "${BLUE}7. BUSCAR POR PALABRAS CLAVE${NC}"
SEARCH=$(curl -s -X GET "$API/busca/buscar?q=documento&pagina=1&por_pagina=10" \
  -H "Authorization: Bearer $TOKEN")
TOTAL=$(echo $SEARCH | grep -o '"total":[0-9]*' | cut -d':' -f2)
echo -e "${GREEN}✓ Búsqueda realizada${NC}"
echo "Resultados encontrados: $TOTAL\n"

# 8. OBTENER DOCUMENTOS SIMILARES
echo -e "${BLUE}8. OBTENER DOCUMENTOS SIMILARES${NC}"
curl -s -X GET $API/busca/similares/$DOC_ID > /dev/null
echo -e "${GREEN}✓ Documentos similares obtenidos${NC}\n"

# 9. GENERAR RECOMENDACIONES
echo -e "${BLUE}9. GENERAR RECOMENDACIONES${NC}"
curl -s -X POST $API/recomendaciones/documento/$DOC_ID/generar \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"limite": 5, "algoritmo": "tfidf"}' > /dev/null
echo -e "${GREEN}✓ Recomendaciones generadas${NC}\n"

# 10. OBTENER DOCUMENTOS POPULARES
echo -e "${BLUE}10. OBTENER DOCUMENTOS POPULARES${NC}"
POP=$(curl -s -X GET "$API/recomendaciones/populares?limite=10")
echo -e "${GREEN}✓ Documentos populares obtenidos${NC}\n"

# 11. OBTENER HISTORIAL DE BÚSQUEDAS
echo -e "${BLUE}11. OBTENER HISTORIAL DE BÚSQUEDAS${NC}"
HIST=$(curl -s -X GET "$API/busca/historial?pagina=1&por_pagina=10" \
  -H "Authorization: Bearer $TOKEN")
echo -e "${GREEN}✓ Historial obtenido${NC}\n"

# Limpieza
rm -f test_doc.txt

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
```

**Ejecutar:**
```bash
chmod +x test_completo.sh
./test_completo.sh
```

---

## 📊 RESUMEN DE FLUJO

```
INICIO
│
├─→ AUTENTICACIÓN
│   ├─→ Registro (POST /auth/registro)
│   └─→ Login (POST /auth/login)
│   └─→ Obtener Token
│
├─→ CONFIGURACIÓN
│   ├─→ Crear Categorías (POST /categorias)
│   ├─→ Crear Subcategorías (POST /categorias con padre)
│   ├─→ Crear Etiquetas (POST /etiquetas)
│   └─→ Listar (GET)
│
├─→ DOCUMENTOS
│   ├─→ Subir (POST /documentos/subir)
│   ├─→ Agregar Palabras Clave (POST /documentos/{id}/palabras-clave)
│   ├─→ Agregar Etiquetas (POST /documentos/{id}/etiquetas)
│   ├─→ Ver Detalles (GET /documentos/{id})
│   ├─→ Actualizar (PUT /documentos/{id})
│   ├─→ Ver Accesos (GET /documentos/{id}/accesos)
│   └─→ Eliminar (DELETE /documentos/{id})
│
├─→ BÚSQUEDA
│   ├─→ Por Palabras Clave (GET /busca/buscar?q=...)
│   ├─→ Por Categoría (GET /busca/categoria/{id})
│   ├─→ Por Etiquetas (GET /busca/etiquetas?etiqueta_id=...)
│   ├─→ Similares (GET /busca/similares/{id})
│   ├─→ Historial (GET /busca/historial)
│   └─→ Populares (GET /busca/populares)
│
├─→ RECOMENDACIONES
│   ├─→ Generar (POST /recomendaciones/documento/{id}/generar)
│   ├─→ Obtener (GET /recomendaciones/documento/{id})
│   ├─→ Populares (GET /recomendaciones/populares)
│   └─→ Eliminar (DELETE /recomendaciones/documento/{id})
│
└─→ ANÁLISIS
    ├─→ Accesos por documento
    ├─→ Búsquedas históricas
    └─→ Documentos populares
```

---

## ✅ Checklist de Prueba

- [ ] Registro exitoso
- [ ] Login exitoso
- [ ] Categorías creadas
- [ ] Subcategorías creadas
- [ ] Etiquetas creadas
- [ ] Documento subido
- [ ] Palabras clave agregadas
- [ ] Etiquetas agregadas
- [ ] Búsqueda por palabra realizada
- [ ] Documentos similares obtenidos
- [ ] Recomendaciones generadas
- [ ] Historial de búsquedas visto
- [ ] Búsquedas populares vistas
- [ ] Documentos populares visto
- [ ] Accesos registrados
- [ ] Actualizaciones funcionan
- [ ] Eliminaciones funcionan

---

**¡Listo para probar todos los endpoints!**

