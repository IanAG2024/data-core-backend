#!/bin/bash

# Script para instalar y ejecutar la aplicación

echo "🚀 Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "✓ Dependencias instaladas"
echo ""
echo "📦 Inicializando base de datos..."
python -m flask --app cli init-db

echo ""
echo "🌱 Cargando datos iniciales..."
python -m flask --app cli seed-db

echo ""
echo "✅ ¡Listo! Iniciando aplicación..."
echo ""
echo "🌐 La aplicación estará disponible en http://localhost:5000"
echo ""

python app.py
