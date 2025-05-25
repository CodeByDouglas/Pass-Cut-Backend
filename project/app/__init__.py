import os
from flask import Flask
from dotenv import load_dotenv
from .config import Config
from .extensions import db, migrate, jwt, cors
from .controllers.Endpoints.Cliente.redirecionamento_inicial import redirecionamento_bp
from .controllers.Endpoints.Cliente.autenticar_user import autenticar_user_bp
from .controllers.Endpoints.Cliente.consultar_agendamentos import consultar_agendamentos_bp
from .controllers.Endpoints.Cliente.consultar_servicos import consultar_servicos_bp
from .controllers.Endpoints.Cliente.consultar_colaborador import consultar_colaborador_bp
from .controllers.Endpoints.Cliente.consultar_horarios import consultar_horarios_bp
from .controllers.Endpoints.Cliente.cancelar_agendamento import cancelar_agendamento_bp
from .controllers.Endpoints.Cliente.criar_agendamento import criar_agendamento_bp


def create_app(config_class=Config):
    # carrega .env
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config_class)

    # inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    cors.init_app(app,
        supports_credentials=True,
        origins=[
            "https://7dcc-74-249-85-196.ngrok-free.app"  # URL pública do Ngrok para o frontend
        ]
    )
   
    # importa os models para que o SQLAlchemy os registre
    from .models import models

    app.register_blueprint(redirecionamento_bp)
    app.register_blueprint(autenticar_user_bp)
    app.register_blueprint(consultar_agendamentos_bp)
    app.register_blueprint(consultar_servicos_bp)
    app.register_blueprint(consultar_colaborador_bp)
    app.register_blueprint(consultar_horarios_bp)
    app.register_blueprint(cancelar_agendamento_bp)
    app.register_blueprint(criar_agendamento_bp)

    return app