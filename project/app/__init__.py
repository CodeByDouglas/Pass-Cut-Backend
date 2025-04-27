import os
from flask import Flask
from dotenv import load_dotenv
from .config import Config
from .extensions import db, migrate, jwt, cors

def create_app(config_class=Config):
    # carrega .env
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config_class)

    # inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    # importa os models para que o SQLAlchemy os registre
    from .models import models

    # registra um healthcheck simples
    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    # importar e registrar blueprints (mais à frente)
    # from .controllers.admin import admin_bp
    # from .controllers.client import client_bp
    # app.register_blueprint(admin_bp)
    # app.register_blueprint(client_bp)

    return app
