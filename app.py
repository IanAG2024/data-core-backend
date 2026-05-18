from dotenv import load_dotenv
from backend import create_app

# Cargar variables de entorno desde .env
load_dotenv()

app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
