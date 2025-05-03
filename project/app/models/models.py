import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.extensions import db

# Tabela de associação para muitos-para-muitos entre Agendamento e Serviço
agendamento_servico = db.Table(
    'agendamento_servico',
    db.Column('agendamento_id', UUID(as_uuid=True), db.ForeignKey('agendamentos.id'), primary_key=True),
    db.Column('servico_id', UUID(as_uuid=True), db.ForeignKey('servicos.id'), primary_key=True)
)

# BaseModel com UUID, timestamps e soft-delete
default_datetime = datetime.utcnow

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(
        UUID(as_uuid=True), primary_key=True,
        default=uuid.uuid4, nullable=False, unique=True, index=True
    )
    created_at = db.Column(db.DateTime, default=default_datetime, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=default_datetime,
        onupdate=default_datetime, nullable=False
    )
    deleted = db.Column(db.Boolean, default=False, nullable=False)


# Estabelecimento (com login e senha)
class Estabelecimento(BaseModel):
    __tablename__ = 'estabelecimentos'

    #Número da Base para redirecionamento inicial
    identificador_base = db.Column(db.String(10), nullable=False,  unique=True, index=True)
    # credenciais de acesso
    email_login = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(128), nullable=False)

    # dados cadastrais e Pagar.me
    nome_fantasia = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(20), nullable=True, unique=True)
    telefone = db.Column(db.String(20), nullable=True)
    pagarme_recipient_id = db.Column(db.String(50), nullable=True, unique=True)

    # relacionamentos
    colaboradores = db.relationship('Colaborador', backref='estabelecimento', lazy=True)
    planos = db.relationship('Plano', backref='estabelecimento', lazy=True)
    clientes = db.relationship('Cliente', backref='estabelecimento', lazy=True)
    agendamentos = db.relationship('Agendamento', backref='estabelecimento', lazy=True)


# Cliente (com login e senha)
class Cliente(BaseModel):
    __tablename__ = 'clientes'

    # credenciais de acesso
    email_login = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(128), nullable=False)

    # dados pessoais
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=True, unique=True)
    telefone = db.Column(db.String(20), nullable=True)

    # integração Pagar.me
    pagarme_customer_id = db.Column(db.String(50), nullable=True, unique=True)
    card_token = db.Column(db.String(100), nullable=True)
    card_last_digits = db.Column(db.String(4), nullable=True)
    card_brand = db.Column(db.String(20), nullable=True)

    # relacionamento com estabelecimento (tenant)
    estabelecimento_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('estabelecimentos.id'), nullable=False
    )

    # relacionamentos
    assinaturas = db.relationship('Assinatura', backref='cliente', lazy=True)
    agendamentos = db.relationship('Agendamento', backref='cliente', lazy=True)


# Colaborador mínimo
class Colaborador(BaseModel):
    __tablename__ = 'colaboradores'

    nome = db.Column(db.String(100), nullable=False)
    estabelecimento_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('estabelecimentos.id'), nullable=False
    )

    # relacionamento de agendamentos
    agendamentos = db.relationship('Agendamento', backref='colaborador', lazy=True)


# Serviço
default_numeric = db.Numeric(10, 2)

class Servico(BaseModel):
    __tablename__ = 'servicos'

    nome = db.Column(db.String(100), nullable=False)
    duracao = db.Column(db.Integer, nullable=False)  # em minutos
    preco = db.Column(default_numeric, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    estabelecimento_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('estabelecimentos.id'), nullable=False
    )

    # Relacionamento muitos-para-muitos com Agendamento
    agendamentos = db.relationship('Agendamento', secondary=agendamento_servico, back_populates='servicos', lazy=True)


# Plano de assinatura
class Plano(BaseModel):
    __tablename__ = 'planos'

    estabelecimento_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('estabelecimentos.id'), nullable=False
    )
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    valor = db.Column(default_numeric, nullable=False)
    ciclo_dias = db.Column(db.Integer, default=30, nullable=False)
    pagarme_plan_id = db.Column(db.String(50), nullable=True, unique=True)

    assinaturas = db.relationship('Assinatura', backref='plano', lazy=True)


# Assinatura de plano por cliente
class Assinatura(BaseModel):
    __tablename__ = 'assinaturas'

    cliente_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('clientes.id'), nullable=False
    )
    plano_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('planos.id'), nullable=False
    )
    data_inicio = db.Column(db.DateTime, default=default_datetime, nullable=False)
    status = db.Column(db.String(20), default='ativa', nullable=False)
    pagarme_subscription_id = db.Column(db.String(50), nullable=True, unique=True)

    # relacionamento com agendamentos (opcional)
    agendamentos = db.relationship('Agendamento', backref='assinatura', lazy=True)


# Agendamento (reserva de horário)
class Agendamento(BaseModel):
    __tablename__ = 'agendamentos'

    cliente_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('clientes.id'), nullable=False
    )
    colaborador_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('colaboradores.id'), nullable=False
    )
    estabelecimento_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('estabelecimentos.id'), nullable=False
    )
    assinatura_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('assinaturas.id'), nullable=True
    )

    duracao = db.Column(db.Integer, nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pendente', nullable=False)

    # Relacionamento muitos-para-muitos com Servico
    servicos = db.relationship('Servico', secondary=agendamento_servico, back_populates='agendamentos', lazy=True)
