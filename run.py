import logging
from dotenv import load_dotenv
from app import create_app

load_dotenv()

logging.basicConfig(level=logging.INFO)

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

