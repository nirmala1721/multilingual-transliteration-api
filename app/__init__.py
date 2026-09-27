from flask import Flask
from flask_cors import CORS

from app.api import api
from app.config import MAX_FILE_SIZE
from app.extensions import limiter


def create_app():

    app = Flask(__name__)

    app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "https://multilingual-transliteration-api.vercel.app",
                    "http://localhost:5173",
                ]
            }
        }
    )

    limiter.init_app(app)

    api.init_app(
        app,
        add_specs=True,
        spec_kwargs={
            "servers": [
                {
                    "url": "/"
                }
            ]
        }
    )

    return app