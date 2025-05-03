import os
from flask import Flask
from dotenv import load_dotenv
from .config import Config
from .extensions import db, migrate, jwt, cors
from .controllers.API_Agendamentos.redirecionamento_inicial import redirecionamento_bp
from .controllers.API_Agendamentos.autenticar_user import autenticar_user_bp
from .controllers.API_Agendamentos.consultar_agendamentos import consultar_agendamentos_bp

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

    app.register_blueprint(redirecionamento_bp)
    app.register_blueprint(autenticar_user_bp)
    app.register_blueprint(consultar_agendamentos_bp)
    return app
