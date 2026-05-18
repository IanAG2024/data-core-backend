#!/usr/bin/env python3
"""
Script interactivo para probar todos los endpoints del sistema
"""

import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000/api"
HEADERS = {"Content-Type": "application/json"}

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Variables globales para almacenar IDs
TOKEN = None
USER_ID = None
CATEGORIA_ID = None
ETIQUETA_ID = None
DOCUMENTO_ID = None

def print_section(title):
    """Imprimir sección con título"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Imprimir mensaje de error"""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def print_info(message):
    """Imprimir mensaje informativo"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.ENDC}")

def print_request(method, endpoint):
    """Imprimir solicitud"""
    print(f"{Colors.YELLOW}{method:6} {endpoint}{Colors.ENDC}")

def print_json(data, indent=2):
    """Imprimir JSON formateado"""
    print(json.dumps(data, indent=indent, ensure_ascii=False))

def request_handler(method, endpoint, data=None, headers=None, show_response=True):
    """Manejo centralizado de solicitudes"""
    url = f"{BASE_URL}{endpoint}"
    if headers is None:
        headers = HEADERS.copy()
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"
    
    print_request(method, endpoint)
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 201]:
            if show_response:
                print_json(response.json())
            return response.json()
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

# ============================================================================
# AUTENTICACIÓN
# ============================================================================

def test_autenticacion():
    """Probar endpoints de autenticación"""
    global TOKEN, USER_ID
    
    print_section("1️⃣  AUTENTICACIÓN")
    
    # Registro
    print_info("Registrando usuario...")
    data = {
        "nombre": f"Test User {datetime.now().timestamp()}",
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "TestPassword123!"
    }
    
    result = request_handler("POST", "/auth/registro", data)
    if result:
        TOKEN = result.get("token")
        USER_ID = result.get("usuario", {}).get("id")
        print_success(f"Usuario registrado con ID: {USER_ID}")
        print_info(f"Token: {TOKEN[:50]}...")
    
    # Obtener perfil
    print_info("Obteniendo perfil...")
    request_handler("GET", "/auth/perfil")
    print_success("Perfil obtenido")
    
    # Actualizar perfil
    print_info("Actualizando perfil...")
    data = {"nombre": "Test User Actualizado"}
    request_handler("PUT", "/auth/perfil", data, show_response=False)
    print_success("Perfil actualizado")
    
    # Verificar token
    print_info("Verificando token...")
    result = request_handler("POST", "/auth/verificar-token", show_response=False)
    if result and result.get("valido"):
        print_success("Token válido")
    else:
        print_error("Token no válido")

# ============================================================================
# CATEGORÍAS
# ============================================================================

def test_categorias():
    """Probar endpoints de categorías"""
    global CATEGORIA_ID
    
    print_section("2️⃣  CATEGORÍAS")
    
    # Crear categoría
    print_info("Creando categoría...")
    data = {
        "nombre": f"Categoría Test {datetime.now().timestamp()}",
        "descripcion": "Categoría de prueba"
    }
    
    result = request_handler("POST", "/categorias", data)
    if result:
        CATEGORIA_ID = result.get("categoria", {}).get("id")
        print_success(f"Categoría creada con ID: {CATEGORIA_ID}")
    
    # Listar categorías
    print_info("Listando categorías...")
    request_handler("GET", "/categorias?pagina=1&por_pagina=5")
    print_success("Categorías listadas")
    
    # Obtener árbol
    print_info("Obteniendo árbol de categorías...")
    request_handler("GET", "/categorias/arbol")
    print_success("Árbol obtenido")
    
    # Obtener categoría específica
    if CATEGORIA_ID:
        print_info(f"Obteniendo categoría {CATEGORIA_ID}...")
        request_handler("GET", f"/categorias/{CATEGORIA_ID}")
        print_success("Categoría obtenida")

# ============================================================================
# ETIQUETAS
# ============================================================================

def test_etiquetas():
    """Probar endpoints de etiquetas"""
    global ETIQUETA_ID
    
    print_section("3️⃣  ETIQUETAS")
    
    # Crear etiquetas
    etiquetas_data = [
        {"nombre": "Importante", "color": "#FF0000"},
        {"nombre": "Urgente", "color": "#FFA500"},
        {"nombre": "Revisado", "color": "#00FF00"},
    ]
    
    for etiq_data in etiquetas_data:
        print_info(f"Creando etiqueta: {etiq_data['nombre']}...")
        result = request_handler("POST", "/etiquetas", etiq_data, show_response=False)
        if result and ETIQUETA_ID is None:
            ETIQUETA_ID = result.get("etiqueta", {}).get("id")
            print_success(f"Etiqueta creada con ID: {ETIQUETA_ID}")
        else:
            print_success(f"Etiqueta '{etiq_data['nombre']}' creada")
    
    # Listar etiquetas
    print_info("Listando etiquetas...")
    request_handler("GET", "/etiquetas?pagina=1&por_pagina=10")
    print_success("Etiquetas listadas")

# ============================================================================
# DOCUMENTOS
# ============================================================================

def test_documentos():
    """Probar endpoints de documentos"""
    global DOCUMENTO_ID
    
    print_section("4️⃣  DOCUMENTOS")
    
    # Crear archivo de prueba
    print_info("Creando archivo de prueba...")
    with open("test_document.txt", "w") as f:
        f.write("Este es un documento de prueba para el sistema de recuperación de información.\n")
        f.write("Contiene palabras clave como: sistema, prueba, documento, búsqueda, recuperación.\n")
        f.write("Ideal para probar todos los endpoints del sistema.")
    print_success("Archivo creado")
    
    # Subir documento
    print_info("Subiendo documento...")
    url = f"{BASE_URL}/documentos/subir"
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    
    with open("test_document.txt", "rb") as f:
        files = {"archivo": f}
        data = {
            "titulo": "Documento de Prueba",
            "descripcion": "Un documento para probar el sistema",
            "categoria_id": CATEGORIA_ID if CATEGORIA_ID else 1,
            "es_publico": "true"
        }
        
        try:
            response = requests.post(url, files=files, data=data, headers=headers)
            if response.status_code == 201:
                result = response.json()
                DOCUMENTO_ID = result.get("documento", {}).get("id")
                print_success(f"Documento subido con ID: {DOCUMENTO_ID}")
                print_json(result.get("documento", {}))
            else:
                print_error(f"Error al subir: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {str(e)}")
    
    # Listar documentos públicos
    print_info("Listando documentos públicos...")
    request_handler("GET", "/documentos?pagina=1&por_pagina=10")
    print_success("Documentos listados")
    
    # Mis documentos
    print_info("Obtiendo mis documentos...")
    request_handler("GET", "/documentos/mis-documentos?pagina=1&por_pagina=10")
    print_success("Mis documentos obtenidos")

# ============================================================================
# PALABRAS CLAVE
# ============================================================================

def test_palabras_clave():
    """Probar endpoints de palabras clave"""
    
    print_section("5️⃣  PALABRAS CLAVE")
    
    if not DOCUMENTO_ID:
        print_error("No hay documento para probar")
        return
    
    # Agregar palabras clave
    print_info("Agregando palabras clave...")
    data = {
        "palabras": ["sistema", "documento", "prueba", "recuperación", "búsqueda", "información"]
    }
    
    request_handler("POST", f"/documentos/{DOCUMENTO_ID}/palabras-clave", data)
    print_success("Palabras clave agregadas")
    
    # Obtener palabras clave
    print_info("Obteniendo palabras clave...")
    request_handler("GET", f"/documentos/{DOCUMENTO_ID}/palabras-clave")
    print_success("Palabras clave obtenidas")

# ============================================================================
# ETIQUETAS EN DOCUMENTOS
# ============================================================================

def test_etiquetas_documentos():
    """Probar endpoints de etiquetas en documentos"""
    
    print_section("6️⃣  ETIQUETAS EN DOCUMENTOS")
    
    if not DOCUMENTO_ID or not ETIQUETA_ID:
        print_error("No hay documento o etiqueta para probar")
        return
    
    # Agregar etiqueta
    print_info("Agregando etiqueta a documento...")
    data = {"etiqueta_id": ETIQUETA_ID}
    
    request_handler("POST", f"/documentos/{DOCUMENTO_ID}/etiquetas", data)
    print_success("Etiqueta agregada")
    
    # Obtener etiquetas
    print_info("Obteniendo etiquetas del documento...")
    request_handler("GET", f"/documentos/{DOCUMENTO_ID}/etiquetas")
    print_success("Etiquetas obtenidas")

# ============================================================================
# BÚSQUEDA
# ============================================================================

def test_busqueda():
    """Probar endpoints de búsqueda"""
    
    print_section("7️⃣  BÚSQUEDA")
    
    # Búsqueda por palabras clave
    print_info("Buscando por palabras clave...")
    request_handler("GET", "/busca/buscar?q=sistema&pagina=1&por_pagina=10")
    print_success("Búsqueda completada")
    
    # Búsqueda por categoría
    if CATEGORIA_ID:
        print_info(f"Buscando en categoría {CATEGORIA_ID}...")
        request_handler("GET", f"/busca/categoria/{CATEGORIA_ID}?pagina=1&por_pagina=10")
        print_success("Búsqueda por categoría completada")
    
    # Búsquedas populares
    print_info("Obteniendo búsquedas populares...")
    request_handler("GET", "/busca/populares?limite=10")
    print_success("Búsquedas populares obtenidas")
    
    # Historial de búsquedas
    print_info("Obteniendo historial de búsquedas...")
    request_handler("GET", "/busca/historial?pagina=1&por_pagina=10")
    print_success("Historial obtenido")

# ============================================================================
# DOCUMENTOS SIMILARES
# ============================================================================

def test_similares():
    """Probar endpoint de documentos similares"""
    
    print_section("8️⃣  DOCUMENTOS SIMILARES")
    
    if not DOCUMENTO_ID:
        print_error("No hay documento para probar")
        return
    
    print_info(f"Buscando documentos similares a {DOCUMENTO_ID}...")
    request_handler("GET", f"/busca/similares/{DOCUMENTO_ID}")
    print_success("Búsqueda de similares completada")

# ============================================================================
# RECOMENDACIONES
# ============================================================================

def test_recomendaciones():
    """Probar endpoints de recomendaciones"""
    
    print_section("9️⃣  RECOMENDACIONES")
    
    if not DOCUMENTO_ID:
        print_error("No hay documento para probar")
        return
    
    # Generar recomendaciones TF-IDF
    print_info("Generando recomendaciones (TF-IDF)...")
    data = {"limite": 5, "algoritmo": "tfidf"}
    request_handler("POST", f"/recomendaciones/documento/{DOCUMENTO_ID}/generar", data, show_response=False)
    print_success("Recomendaciones generadas")
    
    # Obtener recomendaciones
    print_info("Obteniendo recomendaciones...")
    request_handler("GET", f"/recomendaciones/documento/{DOCUMENTO_ID}?limite=5")
    print_success("Recomendaciones obtenidas")
    
    # Documentos populares
    print_info("Obteniendo documentos populares...")
    request_handler("GET", "/recomendaciones/populares?limite=10")
    print_success("Documentos populares obtenidos")

# ============================================================================
# ACCESOS
# ============================================================================

def test_accesos():
    """Probar endpoint de accesos"""
    
    print_section("🔟 ACCESOS A DOCUMENTOS")
    
    if not DOCUMENTO_ID:
        print_error("No hay documento para probar")
        return
    
    print_info("Obteniendo historial de accesos...")
    request_handler("GET", f"/documentos/{DOCUMENTO_ID}/accesos?pagina=1&por_pagina=10")
    print_success("Accesos obtenidos")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal"""
    
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🧪 PRUEBA INTERACTIVA DE TODOS LOS ENDPOINTS  ".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    print(Colors.ENDC)
    
    print_info(f"Base URL: {BASE_URL}")
    print_info("Iniciando pruebas...\n")
    
    try:
        # Ejecutar todas las pruebas
        test_autenticacion()
        time.sleep(1)
        
        test_categorias()
        time.sleep(1)
        
        test_etiquetas()
        time.sleep(1)
        
        test_documentos()
        time.sleep(1)
        
        test_palabras_clave()
        time.sleep(1)
        
        test_etiquetas_documentos()
        time.sleep(1)
        
        test_busqueda()
        time.sleep(1)
        
        test_similares()
        time.sleep(1)
        
        test_recomendaciones()
        time.sleep(1)
        
        test_accesos()
        
        # Resumen
        print_section("✅ RESUMEN DE PRUEBAS")
        print_success("Todas las pruebas completadas")
        print_info(f"Usuario ID: {USER_ID}")
        print_info(f"Categoría ID: {CATEGORIA_ID}")
        print_info(f"Etiqueta ID: {ETIQUETA_ID}")
        print_info(f"Documento ID: {DOCUMENTO_ID}")
        
    except Exception as e:
        print_error(f"Error durante las pruebas: {str(e)}")
    finally:
        # Limpieza
        try:
            import os
            if os.path.exists("test_document.txt"):
                os.remove("test_document.txt")
        except:
            pass

if __name__ == "__main__":
    main()

