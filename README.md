# FlaskRecuperacionInformacion

Estructura inicial de backend Flask con `create_app()` y `blueprints`.

## Estructura

```text
FlaskRecuperacionInformacion/
├── app.py
├── backend/
│   ├── __init__.py
│   ├── config.py
│   └── blueprints/
│       └── main/
│           ├── __init__.py
│           └── routes.py
├── static/
├── templates/
├── tests/
│   └── test_main.py
├── requirements.txt
└── README.md
```

## Endpoints

- `GET /` → mensaje inicial en JSON
- `GET /health` → estado de salud

## Ejecutar

Instala dependencias:

```bash
pip install -r requirements.txt
```

Arranca la aplicación:

```bash
python app.py
```

## Probar

```bash
python -m unittest discover -s tests
```
