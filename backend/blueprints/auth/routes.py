"""
Blueprint para autenticación y gestión de usuarios.
"""
from flask import Blueprint, request, jsonify
from backend.services.auth import UsuarioService, TokenService
from backend.models import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/registro', methods=['POST'])
def registro():
    """Registrar nuevo usuario"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data or not all([data.get('nombre'), data.get('email'), data.get('password')]):
            return jsonify({'error': 'Campos requeridos: nombre, email, password'}), 400
        
        # Crear usuario
        usuario = UsuarioService.crear_usuario(
            nombre=data['nombre'],
            email=data['email'],
            password=data['password']
        )
        
        # Generar token
        token = TokenService.generar_token(usuario.id)
        
        return jsonify({
            'mensaje': 'Usuario registrado exitosamente',
            'usuario': usuario.to_dict(),
            'token': token
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error al registrar: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Autenticar usuario"""
    try:
        data = request.get_json()
        
        if not data or not all([data.get('email'), data.get('password')]):
            return jsonify({'error': 'Email y password requeridos'}), 400
        
        # Autenticar usuario
        usuario = UsuarioService.autenticar(
            email=data['email'],
            password=data['password']
        )
        
        if not usuario:
            return jsonify({'error': 'Email o password incorrecto'}), 401
        
        # Generar token
        token = TokenService.generar_token(usuario.id)
        
        return jsonify({
            'mensaje': 'Autenticación exitosa',
            'usuario': usuario.to_dict(),
            'token': token
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error al autenticar: {str(e)}'}), 500


@auth_bp.route('/perfil', methods=['GET'])
def obtener_perfil():
    """Obtener perfil del usuario autenticado"""
    try:
        # Obtener token del header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token requerido'}), 401
        
        token = auth_header.split(' ')[1]
        usuario_id = TokenService.obtener_usuario_id_del_token(token)
        
        if not usuario_id:
            return jsonify({'error': 'Token inválido'}), 401
        
        usuario = UsuarioService.obtener_usuario(usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify(usuario.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@auth_bp.route('/perfil', methods=['PUT'])
def actualizar_perfil():
    """Actualizar perfil del usuario autenticado"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token requerido'}), 401
        
        token = auth_header.split(' ')[1]
        usuario_id = TokenService.obtener_usuario_id_del_token(token)
        
        if not usuario_id:
            return jsonify({'error': 'Token inválido'}), 401
        
        data = request.get_json()
        usuario = UsuarioService.actualizar_usuario(usuario_id, **data)
        
        return jsonify({
            'mensaje': 'Perfil actualizado',
            'usuario': usuario.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@auth_bp.route('/cambiar-password', methods=['POST'])
def cambiar_password():
    """Cambiar contraseña del usuario"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token requerido'}), 401
        
        token = auth_header.split(' ')[1]
        usuario_id = TokenService.obtener_usuario_id_del_token(token)
        
        if not usuario_id:
            return jsonify({'error': 'Token inválido'}), 401
        
        data = request.get_json()
        
        if not all([data.get('password_antigua'), data.get('password_nueva')]):
            return jsonify({'error': 'Se requieren ambas contraseñas'}), 400
        
        UsuarioService.cambiar_password(
            usuario_id,
            data['password_antigua'],
            data['password_nueva']
        )
        
        return jsonify({'mensaje': 'Contraseña cambiada exitosamente'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@auth_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    """Listar todos los usuarios (solo admin)"""
    try:
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)
        
        usuarios_paginados = UsuarioService.listar_usuarios(pagina, por_pagina)
        
        return jsonify({
            'total': usuarios_paginados.total,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'usuarios': [u.to_dict() for u in usuarios_paginados.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@auth_bp.route('/verificar-token', methods=['POST'])
def verificar_token():
    """Verificar si un token es válido"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'valido': False}), 200
        
        token = auth_header.split(' ')[1]
        payload = TokenService.verificar_token(token)
        
        return jsonify({'valido': payload is not None}), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500
