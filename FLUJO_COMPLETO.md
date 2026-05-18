# 🔄 FLUJO COMPLETO DEL SISTEMA

## 📊 Diagrama de Flujo General

```
┌──────────────────────────────────────────────────────────────────────┐
│                     INICIO DE LA APLICACIÓN                           │
└──────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Verificar Servidor    │
                    │ (http://localhost:5000)│
                    └────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
         ┌──────────▼────────────┐  ┌────────▼──────────┐
         │   Servidor Disponible  │  │ Servidor No Disponible
         │   (continuar)          │  │ (error)
         └──────────┬────────────┘  └────────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  AUTENTICACIÓN       │
         │  (/api/auth/*)       │
         └──────┬───────────────┘
                │
         ┌──────┴──────────┐
         │                 │
    ┌────▼────┐      ┌────▼────┐
    │Registro │      │  Login   │
    └────┬────┘      └────┬────┘
         │                │
         └────────┬───────┘
                  │
                  ▼
        ┌─────────────────────┐
        │ Obtener JWT Token   │
        │ (válido por 24h)    │
        └──────────┬──────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │  CONFIGURACIÓN INICIAL           │
    │  (Crear estructura del sistema)  │
    └─────────┬────────────────────────┘
              │
       ┌──────┴──────┐
       │              │
   ┌───▼────┐    ┌───▼────┐
   │Categorías│   │Etiquetas│
   └───┬────┘    └───┬────┘
       │              │
       └──────┬───────┘
              │
              ▼
    ┌─────────────────────┐
    │ SUBIR DOCUMENTOS    │
    │ /documentos/subir   │
    └──────────┬──────────┘
               │
         ┌─────┴─────┐
         │            │
    ┌────▼────┐  ┌───▼────┐
    │Palabras  │  │Etiquetas│
    │Clave     │  │         │
    └────┬────┘  └───┬────┘
         │            │
         └─────┬──────┘
               │
               ▼
    ┌──────────────────────────┐
    │ BÚSQUEDA DE DOCUMENTOS   │
    │ /api/busca/*             │
    └────┬─────────────────────┘
         │
    ┌────┴──────────────────────────┐
    │                               │
┌───▼────┐  ┌────────┐  ┌────────┐ │  ┌──────────┐
│Palabras │  │Categoría│ │Etiquetas  │  │Similares │
│Clave    │  │         │ │           │  │          │
└────┬────┘  └────────┘ └────────┘   └──────────┘
     │         │          │           │
     └─────────┬──────────┴───────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ ANÁLISIS DE RESULTADOS   │
    └────┬─────────────────────┘
         │
    ┌────┴────────────────────┐
    │                          │
┌───▼──────┐  ┌────────────┐  │
│Historial  │  │Populares   │  │
│Búsquedas  │  │            │  │
└───┬──────┘  └────┬───────┘  │
    │              │           │
    └──────┬───────┘           │
           │                   │
           ▼                   │
  ┌─────────────────┐          │
  │ Documentos      │          │
  │ Más Accedidos   │          │
  └─────────────────┘          │
                               │
    ┌──────────────────────────┘
    │
    ▼
  ┌─────────────────────────────┐
  │ RECOMENDACIONES             │
  │ /api/recomendaciones/*      │
  └─────┬───────────────────────┘
        │
   ┌────┴──────────┐
   │               │
┌──▼───┐    ┌─────▼──┐
│TF-IDF│    │Categoría│
└──┬───┘    └─────┬──┘
   │              │
   └────┬─────────┘
        │
        ▼
  ┌────────────────┐
  │Documentos      │
  │Recomendados    │
  │(ordenados)     │
  └────────────────┘
```

---

## 🔐 Fase 1: AUTENTICACIÓN

### Paso 1.1: Registrarse
```
POST /api/auth/registro
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "password": "Password123!"
}

↓
RESPONSE (201)
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre": "Juan Pérez",
    "email": "juan@example.com"
  }
}

✓ Guardar TOKEN
```

### Paso 1.2: Usar Token en Próximas Solicitudes
```
Todas las solicitudes autenticadas requieren:
Header: Authorization: Bearer <TOKEN>

Ej:
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 📂 Fase 2: CREAR ESTRUCTURA

### Paso 2.1: Crear Categorías
```
POST /api/categorias
{
  "nombre": "Documentos Administrativos",
  "descripcion": "Categoría para documentos administrativos"
}

↓
RESPONSE (201)
{
  "categoria": {
    "id": 1,
    "nombre": "Documentos Administrativos"
  }
}

✓ Guardar CATEGORIA_ID = 1
```

### Paso 2.2: Crear Subcategorías (Opcional)
```
POST /api/categorias
{
  "nombre": "Contratos",
  "categoria_padre": 1
}

↓
Estructura:
  Documentos Administrativos (id: 1)
  └─ Contratos (id: 2)
```

### Paso 2.3: Crear Etiquetas
```
POST /api/etiquetas (múltiples llamadas)
{
  "nombre": "Importante",
  "color": "#FF0000"
}

RESPUESTA:
{
  "etiqueta": {
    "id": 1,
    "nombre": "Importante"
  }
}

✓ Guardar ETIQUETA_IDS = [1, 2, 3, ...]
```

---

## 📄 Fase 3: SUBIR DOCUMENTOS

### Paso 3.1: Subir un Documento
```
POST /api/documentos/subir
Content-Type: multipart/form-data

Headers:
Authorization: Bearer <TOKEN>

Form Data:
- archivo: <archivo.txt>
- titulo: "Documento de Prueba"
- descripcion: "Descripción del documento"
- categoria_id: 1
- es_publico: true

↓
RESPONSE (201)
{
  "documento": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "titulo": "Documento de Prueba",
    "tipo": "texto",
    "estado": "pendiente"
  }
}

✓ Guardar DOCUMENTO_ID = "550e8400-..."
```

### Paso 3.2: Agregar Palabras Clave
```
POST /api/documentos/{DOCUMENTO_ID}/palabras-clave
Headers:
Authorization: Bearer <TOKEN>

Body:
{
  "palabras": [
    "prueba",
    "documento",
    "sistema",
    "búsqueda"
  ]
}

↓
RESPONSE (200)
{
  "palabras_clave": [
    {
      "palabra": "prueba",
      "peso": 1.0,
      "fuente": "manual"
    },
    ...
  ]
}

✓ Documento indexado
```

### Paso 3.3: Agregar Etiquetas
```
POST /api/documentos/{DOCUMENTO_ID}/etiquetas
Headers:
Authorization: Bearer <TOKEN>

Body:
{
  "etiqueta_id": 1
}

↓
RESPONSE (200)
{
  "etiquetas": [
    {
      "id": 1,
      "nombre": "Importante"
    }
  ]
}

✓ Etiqueta asignada
```

---

## 🔍 Fase 4: BÚSQUEDA DE DOCUMENTOS

### Paso 4.1: Búsqueda Simple
```
GET /api/busca/buscar?q=sistema&pagina=1&por_pagina=10
Headers:
Authorization: Bearer <TOKEN>

↓
RESPONSE (200)
{
  "termino": "sistema",
  "total": 3,
  "pagina": 1,
  "resultados": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "titulo": "Documento de Prueba",
      "descripcion": "..."
    },
    ...
  ]
}

✓ Resultados encontrados
✓ Búsqueda registrada en historial
```

### Paso 4.2: Búsqueda Avanzada con Filtros
```
GET /api/busca/buscar?q=sistema&categoria_id=1&tipo=texto&pagina=1
Headers:
Authorization: Bearer <TOKEN>

Parámetros:
- q: término de búsqueda
- categoria_id: filtro por categoría
- tipo: filtro por tipo (texto, imagen, video, audio, documento)
- pagina: número de página
- por_pagina: resultados por página

↓
Resultados filtrados y paginados
```

### Paso 4.3: Búsqueda por Categoría
```
GET /api/busca/categoria/1?pagina=1&por_pagina=10
Headers:
Authorization: Bearer <TOKEN>

↓
RESPONSE
{
  "categoria_id": 1,
  "total": 5,
  "resultados": [...]
}
```

### Paso 4.4: Búsqueda por Etiquetas
```
GET /api/busca/etiquetas?etiqueta_id=1&etiqueta_id=2&pagina=1
Headers:
Authorization: Bearer <TOKEN>

↓
Documentos con estas etiquetas
```

### Paso 4.5: Documentos Similares
```
GET /api/busca/similares/{DOCUMENTO_ID}

↓
RESPONSE
{
  "documento_id": "550e8400-...",
  "similares": [
    {
      "id": "550e8400-...",
      "titulo": "Documento Similar",
      "descripcion": "..."
    }
  ]
}

✓ Basado en palabras clave coincidentes
```

---

## 📊 Fase 5: ANÁLISIS Y ESTADÍSTICAS

### Paso 5.1: Ver Historial de Búsquedas
```
GET /api/busca/historial?pagina=1&por_pagina=10
Headers:
Authorization: Bearer <TOKEN>

↓
RESPONSE
{
  "total": 5,
  "historial": [
    {
      "termino": "sistema",
      "total_resultados": 3,
      "buscado_en": "2026-05-17T10:43:00"
    },
    ...
  ]
}
```

### Paso 5.2: Ver Búsquedas Populares
```
GET /api/busca/populares?limite=10

↓
RESPONSE
{
  "resultados": [
    {
      "termino": "documento",
      "cantidad": 5
    },
    {
      "termino": "sistema",
      "cantidad": 3
    },
    ...
  ]
}

✓ Términos más buscados por todos los usuarios
```

### Paso 5.3: Ver Accesos a Documento
```
GET /api/documentos/{DOCUMENTO_ID}/accesos?pagina=1&por_pagina=10
Headers:
Authorization: Bearer <TOKEN>

↓
RESPONSE
{
  "total": 3,
  "accesos": [
    {
      "usuario_id": "550e8400-...",
      "accion": "visualizar",
      "accedido_en": "2026-05-17T10:40:05"
    },
    ...
  ]
}
```

---

## 💡 Fase 6: RECOMENDACIONES

### Paso 6.1: Generar Recomendaciones (TF-IDF)
```
POST /api/recomendaciones/documento/{DOCUMENTO_ID}/generar
Headers:
Authorization: Bearer <TOKEN>

Body:
{
  "limite": 5,
  "algoritmo": "tfidf"
}

↓
RESPONSE
{
  "mensaje": "Recomendaciones generadas usando tfidf",
  "recomendaciones": [
    {
      "id": "550e8400-...",
      "titulo": "Documento Similar",
      "score": 0.85
    },
    ...
  ]
}

✓ Basado en similitud de palabras clave
```

### Paso 6.2: Generar por Categoría
```
POST /api/recomendaciones/documento/{DOCUMENTO_ID}/generar
Headers:
Authorization: Bearer <TOKEN>

Body:
{
  "limite": 5,
  "algoritmo": "categoria"
}

↓
RESPONSE
{
  "recomendaciones": [
    Documentos de la misma categoría
  ]
}
```

### Paso 6.3: Obtener Recomendaciones
```
GET /api/recomendaciones/documento/{DOCUMENTO_ID}?limite=5

↓
RESPONSE
{
  "recomendaciones": [
    {
      "id": "550e8400-...",
      "titulo": "...",
      "score": 0.85,
      "algoritmo": "tfidf"
    },
    ...
  ]
}
```

### Paso 6.4: Ver Documentos Populares
```
GET /api/recomendaciones/populares?limite=10

↓
RESPONSE
{
  "documentos": [
    {
      "id": "550e8400-...",
      "titulo": "Documento Muy Visitado",
      "total_accesos": 25
    },
    ...
  ]
}

✓ Ordenado por número de accesos
```

---

## 🔄 Fase 7: GESTIÓN COMPLETA

### Actualizar Documento
```
PUT /api/documentos/{DOCUMENTO_ID}
Headers:
Authorization: Bearer <TOKEN>

Body:
{
  "titulo": "Nuevo Título",
  "descripcion": "Nueva Descripción",
  "es_publico": false
}

↓
Documento actualizado
```

### Eliminar Documento
```
DELETE /api/documentos/{DOCUMENTO_ID}
Headers:
Authorization: Bearer <TOKEN>

↓
Documento eliminado (incluyendo archivo)
```

### Actualizar Categoría
```
PUT /api/categorias/{CATEGORIA_ID}

Body:
{
  "nombre": "Nuevo Nombre",
  "descripcion": "Nueva descripción"
}

↓
Categoría actualizada
```

---

## 📋 Checklist del Flujo Completo

```
FASE 1: AUTENTICACIÓN
☐ POST /auth/registro
☐ Obtener TOKEN
☐ POST /auth/login (alternativo)

FASE 2: ESTRUCTURA
☐ POST /categorias (crear categorías)
☐ POST /categorias (crear subcategorías)
☐ POST /etiquetas (crear etiquetas)
☐ GET /categorias/arbol (verificar estructura)

FASE 3: DOCUMENTOS
☐ POST /documentos/subir (subir documento)
☐ POST /documentos/{id}/palabras-clave (indexar)
☐ POST /documentos/{id}/etiquetas (etiquetar)
☐ GET /documentos (listar)
☐ GET /documentos/{id} (obtener detalles)

FASE 4: BÚSQUEDA
☐ GET /busca/buscar?q=... (búsqueda simple)
☐ GET /busca/buscar?q=...&categoria_id=... (búsqueda filtrada)
☐ GET /busca/categoria/{id} (por categoría)
☐ GET /busca/etiquetas (por etiquetas)
☐ GET /busca/similares/{id} (similares)

FASE 5: ANÁLISIS
☐ GET /busca/historial (historial)
☐ GET /busca/populares (populares)
☐ GET /documentos/{id}/accesos (accesos)

FASE 6: RECOMENDACIONES
☐ POST /recomendaciones/documento/{id}/generar (generar)
☐ GET /recomendaciones/documento/{id} (obtener)
☐ GET /recomendaciones/populares (populares)

FASE 7: GESTIÓN
☐ PUT /documentos/{id} (actualizar)
☐ DELETE /documentos/{id} (eliminar)
☐ PUT /categorias/{id} (actualizar)
☐ PUT /etiquetas/{id} (actualizar)
```

---

## 🎯 Respuestas HTTP Esperadas

| Operación | Método | Status | Significado |
|-----------|--------|--------|-------------|
| Crear | POST | 201 | Creado exitosamente |
| Leer | GET | 200 | OK |
| Actualizar | PUT | 200 | Actualizado |
| Eliminar | DELETE | 200 | Eliminado |
| Error | * | 400 | Solicitud inválida |
| No Autorizado | * | 401 | Token requerido/inválido |
| No Encontrado | * | 404 | Recurso no existe |
| Error Servidor | * | 500 | Error interno |

---

¡Listo para ejecutar el flujo completo! 🚀

