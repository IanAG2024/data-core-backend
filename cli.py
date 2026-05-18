"""
Comandos CLI para la aplicación.
"""
import click
from flask import current_app
from backend import create_app
from backend.models import db, Categorias, Etiquetas
from backend.services.auth import UsuarioService


app = create_app()


@app.cli.command()
def init_db():
    """Inicializar base de datos"""
    with app.app_context():
        print("Creando tablas...")
        db.create_all()
        print("✓ Base de datos inicializada")


@app.cli.command()
def seed_db():
    """Llenar BD con datos iniciales"""
    with app.app_context():
        print("Creando datos iniciales...")
        
        # Crear categorías
        categorias = [
            {'nombre': 'Textos', 'descripcion': 'Documentos de texto'},
            {'nombre': 'Imágenes', 'descripcion': 'Archivos de imagen'},
            {'nombre': 'Videos', 'descripcion': 'Archivos de video'},
            {'nombre': 'Documentos', 'descripcion': 'Documentos ofimáticos'},
            {'nombre': 'Audio', 'descripcion': 'Archivos de audio'},
        ]
        
        for cat_data in categorias:
            if not Categorias.query.filter_by(nombre=cat_data['nombre']).first():
                cat = Categorias(**cat_data)
                db.session.add(cat)
                print(f"  ✓ Categoría creada: {cat_data['nombre']}")
        
        # Crear etiquetas
        etiquetas = [
            {'nombre': 'Importante', 'color': '#FF0000'},
            {'nombre': 'Urgente', 'color': '#FFA500'},
            {'nombre': 'Revisado', 'color': '#00FF00'},
            {'nombre': 'En proceso', 'color': '#0000FF'},
            {'nombre': 'Archivado', 'color': '#808080'},
        ]
        
        for etiq_data in etiquetas:
            if not Etiquetas.query.filter_by(nombre=etiq_data['nombre']).first():
                etiq = Etiquetas(**etiq_data)
                db.session.add(etiq)
                print(f"  ✓ Etiqueta creada: {etiq_data['nombre']}")
        
        # Crear usuario de prueba
        if not UsuarioService.obtener_usuario_por_email('test@example.com'):
            usuario = UsuarioService.crear_usuario(
                nombre='Usuario Prueba',
                email='test@example.com',
                password='password123'
            )
            print(f"  ✓ Usuario de prueba creado: {usuario.email}")
        
        db.session.commit()
        print("\n✓ Datos iniciales cargados")


@app.cli.command()
def drop_db():
    """Eliminar todas las tablas"""
    if click.confirm('¿Estás seguro de que deseas eliminar todas las tablas?'):
        with app.app_context():
            print("Eliminando tablas...")
            db.drop_all()
            print("✓ Base de datos limpiada")
    else:
        print("Operación cancelada")


if __name__ == '__main__':
    app.cli()
