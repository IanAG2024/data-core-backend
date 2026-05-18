#!/usr/bin/env python3
"""
Script de prueba para la API de Recuperación de Información
Prueba los endpoints principales
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

# Colores para output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")

def print_request(method, endpoint):
    print(f"{Colors.YELLOW}{method} {endpoint}{Colors.ENDC}")

# Datos de prueba
TEST_EMAIL = f"test_{datetime.now().timestamp()}@example.com"
TOKEN = None
CATEGORIA_ID = None
DOCUMENTO_ID = None

def test_auth():
    """Probar endpoints de autenticación"""
    global TOKEN
    
    print_header("1️⃣  PRUEBAS DE AUTENTICACIÓN")
    
    # Registro
    print_request("POST", "/api/auth/registro")
    resp = requests.post(f"{BASE_URL}/auth/registro", json={
        "nombre": "Usuario Prueba",
        "email": TEST_EMAIL,
        "password": "test123456"
    })
    
    if resp.status_code == 201:
        data = resp.json()
        TOKEN = data["token"]
        print_success(f"Usuario registrado: {TEST_EMAIL}")
        print_info(f"Token: {TOKEN[:50]}...")
    else:
        print_error(f"Error en registro: {resp.text}")
        return False
    
    # Obtener perfil
    print_request("GET", "/api/auth/perfil")
    resp = requests.get(
        f"{BASE_URL}/auth/perfil",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    if resp.status_code == 200:
        perfil = resp.json()
        print_success(f"Perfil obtenido: {perfil['nombre']}")
    else:
        print_error(f"Error obteniendo perfil: {resp.text}")
    
    # Verificar token
    print_request("POST", "/api/auth/verificar-token")
    resp = requests.post(
        f"{BASE_URL}/auth/verificar-token",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    if resp.status_code == 200:
        data = resp.json()
        if data["valido"]:
            print_success("Token válido")
        else:
            print_error("Token inválido")
    else:
        print_error(f"Error verificando token: {resp.text}")
    
    return True


def test_categories():
    """Probar endpoints de categorías"""
    global CATEGORIA_ID
    
    print_header("2️⃣  PRUEBAS DE CATEGORÍAS")
    
    # Crear categoría
    print_request("POST", "/api/categorias")
    resp = requests.post(f"{BASE_URL}/categorias", json={
        "nombre": "Prueba Categoría",
        "descripcion": "Categoría de prueba"
    })
    
    if resp.status_code == 201:
        data = resp.json()
        CATEGORIA_ID = data["categoria"]["id"]
        print_success(f"Categoría creada: {data['categoria']['nombre']} (ID: {CATEGORIA_ID})")
    else:
        print_error(f"Error creando categoría: {resp.text}")
        return False
    
    # Listar categorías
    print_request("GET", "/api/categorias")
    resp = requests.get(f"{BASE_URL}/categorias?por_pagina=5")
    
    if resp.status_code == 200:
        data = resp.json()
        print_success(f"Categorías listadas: {data['total']} total")
    else:
        print_error(f"Error listando categorías: {resp.text}")
    
    # Obtener árbol
    print_request("GET", "/api/categorias/arbol")
    resp = requests.get(f"{BASE_URL}/categorias/arbol")
    
    if resp.status_code == 200:
        print_success("Árbol de categorías obtenido")
    else:
        print_error(f"Error obteniendo árbol: {resp.text}")
    
    return True


def test_tags():
    """Probar endpoints de etiquetas"""
    
    print_header("3️⃣  PRUEBAS DE ETIQUETAS")
    
    # Crear etiqueta
    print_request("POST", "/api/etiquetas")
    resp = requests.post(f"{BASE_URL}/etiquetas", json={
        "nombre": "Prueba Etiqueta",
        "color": "#FF5733"
    })
    
    if resp.status_code == 201:
        data = resp.json()
        print_success(f"Etiqueta creada: {data['etiqueta']['nombre']}")
    else:
        print_error(f"Error creando etiqueta: {resp.text}")
    
    # Listar etiquetas
    print_request("GET", "/api/etiquetas")
    resp = requests.get(f"{BASE_URL}/etiquetas?por_pagina=5")
    
    if resp.status_code == 200:
        data = resp.json()
        print_success(f"Etiquetas listadas: {data['total']} total")
    else:
        print_error(f"Error listando etiquetas: {resp.text}")
    
    return True


def test_documents():
    """Probar endpoints de documentos (sin subir archivo real)"""
    global DOCUMENTO_ID
    
    print_header("4️⃣  PRUEBAS DE DOCUMENTOS")
    
    # Listar documentos públicos
    print_request("GET", "/api/documentos")
    resp = requests.get(f"{BASE_URL}/documentos?por_pagina=5")
    
    if resp.status_code == 200:
        data = resp.json()
        print_success(f"Documentos públicos: {data['total']} total")
        if data["documentos"]:
            DOCUMENTO_ID = data["documentos"][0]["id"]
            print_info(f"Primer documento: {data['documentos'][0]['titulo']}")
    else:
        print_error(f"Error listando documentos: {resp.text}")
    
    # Mis documentos (usuario autenticado)
    print_request("GET", "/api/documentos/mis-documentos")
    resp = requests.get(
        f"{BASE_URL}/documentos/mis-documentos",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    if resp.status_code == 200:
        data = resp.json()
        print_success(f"Mis documentos: {data['total']} total")
    else:
        print_error(f"Error obteniendo mis documentos: {resp.text}")
    
    return True


def test_search():
    """Probar endpoints de búsqueda"""
    
    print_header("5️⃣  PRUEBAS DE BÚSQUEDA")
    
    # Búsqueda general
    print_request("GET", "/api/busca/buscar")
    resp = requests.get(
        f"{BASE_URL}/busca/buscar?q=test",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    if resp.status_code == 200:
        data = resp.json()
        print_success(f"Búsqueda completada: {data['total']} resultados para '{data['termino']}'")
    else:
        print_error(f"Error en búsqueda: {resp.text}")
    
    if CATEGORIA_ID:
        # Búsqueda por categoría
        print_request("GET", f"/api/busca/categoria/{CATEGORIA_ID}")
        resp = requests.get(
            f"{BASE_URL}/busca/categoria/{CATEGORIA_ID}",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print_success(f"Búsqueda por categoría: {data['total']} resultados")
        else:
            print_error(f"Error en búsqueda por categoría: {resp.text}")
    
    # Búsquedas populares
    print_request("GET", "/api/busca/populares")
    resp = requests.get(f"{BASE_URL}/busca/populares?limite=5")
    
    if resp.status_code == 200:
        data = resp.json()
        print_success(f"Búsquedas populares: {len(data['resultados'])} términos")
    else:
        print_error(f"Error obteniendo búsquedas populares: {resp.text}")
    
    # Historial de búsquedas
    print_request("GET", "/api/busca/historial")
    resp = requests.get(
        f"{BASE_URL}/busca/historial",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    if resp.status_code == 200:
        data = resp.json()
        print_success(f"Historial de búsquedas: {data['total']} búsquedas")
    else:
        print_error(f"Error obteniendo historial: {resp.text}")
    
    return True


def test_recommendations():
    """Probar endpoints de recomendaciones"""
    
    print_header("6️⃣  PRUEBAS DE RECOMENDACIONES")
    
    if not DOCUMENTO_ID:
        print_info("No hay documentos para probar recomendaciones")
        return True
    
    # Obtener recomendaciones
    print_request("GET", f"/api/recomendaciones/documento/{DOCUMENTO_ID}")
    resp = requests.get(
        f"{BASE_URL}/recomendaciones/documento/{DOCUMENTO_ID}?limite=5"
    )
    
    if resp.status_code == 200:
        data = resp.json()
        print_success(f"Recomendaciones: {len(data['recomendaciones'])} documentos")
    else:
        print_error(f"Error obteniendo recomendaciones: {resp.text}")
    
    # Documentos populares
    print_request("GET", "/api/recomendaciones/populares")
    resp = requests.get(f"{BASE_URL}/recomendaciones/populares?limite=10")
    
    if resp.status_code == 200:
        data = resp.json()
        print_success(f"Documentos populares: {len(data['documentos'])} documentos")
    else:
        print_error(f"Error obteniendo documentos populares: {resp.text}")
    
    return True


def test_errors():
    """Probar manejo de errores"""
    
    print_header("🔴 PRUEBAS DE MANEJO DE ERRORES")
    
    # Token inválido
    print_request("GET", "/api/auth/perfil (sin token)")
    resp = requests.get(f"{BASE_URL}/auth/perfil")
    
    if resp.status_code == 401:
        print_success("Rechazado correctamente: sin token")
    else:
        print_error(f"Error esperado: 401, obtenido: {resp.status_code}")
    
    # Endpoint no existe
    print_request("GET", "/api/no-existe")
    resp = requests.get(f"{BASE_URL}/no-existe")
    
    if resp.status_code == 404:
        print_success("Rechazado correctamente: endpoint no existe")
    else:
        print_error(f"Error esperado: 404, obtenido: {resp.status_code}")
    
    # Método no permitido
    print_request("DELETE", "/api/categorias (no permitido)")
    resp = requests.delete(f"{BASE_URL}/categorias")
    
    if resp.status_code == 405:
        print_success("Rechazado correctamente: método no permitido")
    else:
        print_info(f"Respuesta: {resp.status_code}")
    
    return True


def main():
    """Ejecutar todas las pruebas"""
    
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔" + "═"*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  🧪 PRUEBAS DE API - RECUPERACIÓN DE INFORMACIÓN  ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "═"*58 + "╝")
    print(Colors.ENDC)
    
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Asegúrate de que la aplicación esté corriendo en {BASE_URL}")
    print_info(f"Usuario de prueba: {TEST_EMAIL}")
    
    try:
        # Ejecutar todas las pruebas
        tests = [
            ("Autenticación", test_auth),
            ("Categorías", test_categories),
            ("Etiquetas", test_tags),
            ("Documentos", test_documents),
            ("Búsqueda", test_search),
            ("Recomendaciones", test_recommendations),
            ("Manejo de Errores", test_errors),
        ]
        
        results = {}
        for nombre, test_func in tests:
            try:
                result = test_func()
                results[nombre] = "✓" if result else "✗"
            except Exception as e:
                print_error(f"Excepción en {nombre}: {str(e)}")
                results[nombre] = "✗"
        
        # Resumen
        print_header("📊 RESUMEN DE PRUEBAS")
        
        for nombre, resultado in results.items():
            symbol = f"{Colors.GREEN}✓{Colors.ENDC}" if resultado == "✓" else f"{Colors.RED}✗{Colors.ENDC}"
            print(f"{symbol} {nombre}")
        
        total = len(results)
        pasadas = sum(1 for r in results.values() if r == "✓")
        
        print(f"\n{Colors.BOLD}Total: {pasadas}/{total} pruebas pasadas{Colors.ENDC}\n")
        
    except Exception as e:
        print_error(f"Error conectando a la API: {str(e)}")
        print_info("Asegúrate de que la aplicación está corriendo")
        print_info("Ejecuta: python app.py")


if __name__ == "__main__":
    main()
