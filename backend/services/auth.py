"""
Servicio de autenticación y gestión de usuarios.
"""
from uuid import UUID
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from flask import current_app
from backend.models import db, Usuarios


class UsuarioService:
    """Servicio para gestionar usuarios"""

    @staticmethod
    def crear_usuario(nombre: str, email: str, password: str) -> Usuarios:
        """Crear nuevo usuario"""
        if Usuarios.query.filter_by(email=email).first():
            raise ValueError(f"El email {email} ya está registrado")
        
        usuario = Usuarios(
            nombre=nombre,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(usuario)
        db.session.commit()
        return usuario

    @staticmethod
    def autenticar(email: str, password: str) -> Usuarios | None:
        """Autenticar usuario con email y contraseña"""
        usuario = Usuarios.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.password_hash, password):
            return usuario
        return None

    @staticmethod
    def obtener_usuario(usuario_id: UUID) -> Usuarios | None:
        """Obtener usuario por ID"""
        return Usuarios.query.get(usuario_id)

    @staticmethod
    def obtener_usuario_por_email(email: str) -> Usuarios | None:
        """Obtener usuario por email"""
        return Usuarios.query.filter_by(email=email).first()

    @staticmethod
    def actualizar_usuario(usuario_id: UUID, **kwargs) -> Usuarios:
        """Actualizar datos de usuario"""
        usuario = Usuarios.query.get(usuario_id)
        if not usuario:
            raise ValueError(f"Usuario con ID {usuario_id} no encontrado")
        
        # Campos permitidos para actualizar
        campos_permitidos = ['nombre', 'email', 'activo']
        for campo, valor in kwargs.items():
            if campo in campos_permitidos and valor is not None:
                setattr(usuario, campo, valor)
        
        usuario.actualizado_en = datetime.utcnow()
        db.session.commit()
        return usuario

    @staticmethod
    def cambiar_password(usuario_id: UUID, password_antigua: str, password_nueva: str) -> bool:
        """Cambiar contraseña de usuario"""
        usuario = Usuarios.query.get(usuario_id)
        if not usuario:
            raise ValueError(f"Usuario con ID {usuario_id} no encontrado")
        
        if not check_password_hash(usuario.password_hash, password_antigua):
            raise ValueError("Contraseña antigua incorrecta")
        
        usuario.password_hash = generate_password_hash(password_nueva)
        db.session.commit()
        return True

    @staticmethod
    def listar_usuarios(pagina: int = 1, por_pagina: int = 10):
        """Listar todos los usuarios con paginación"""
        return Usuarios.query.paginate(page=pagina, per_page=por_pagina)

    @staticmethod
    def eliminar_usuario(usuario_id: UUID) -> bool:
        """Eliminar usuario"""
        usuario = Usuarios.query.get(usuario_id)
        if not usuario:
            raise ValueError(f"Usuario con ID {usuario_id} no encontrado")
        
        db.session.delete(usuario)
        db.session.commit()
        return True


class TokenService:
    """Servicio para gestionar JWT tokens"""

    @staticmethod
    def generar_token(usuario_id: UUID, expiracion_horas: int = 24) -> str:
        """Generar JWT token"""
        payload = {
            'usuario_id': str(usuario_id),
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=expiracion_horas)
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verificar_token(token: str) -> dict | None:
        """Verificar JWT token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def obtener_usuario_id_del_token(token: str) -> UUID | None:
        """Extraer usuario_id del token"""
        payload = TokenService.verificar_token(token)
        if payload:
            return UUID(payload['usuario_id'])
        return None
