import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import Time
from app.extensions import db

# Associação muitos-para-muitos entre Agendamento e Serviço
agendamento_servico = db.Table(
    'agendamento_servico',
    db.Column('agendamento_id', UUID(as_uuid=True), db.ForeignKey('agendamentos.id'), primary_key=True),
    db.Column('servico_id', UUID(as_uuid=True), db.ForeignKey('servicos.id'), primary_key=True)
)

default_datetime = datetime.utcnow


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        unique=True,
        index=True
    )
    created_at = db.Column(db.DateTime, default=default_datetime, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=default_datetime,
        onupdate=default_datetime,
        nullable=False
    )
    deleted = db.Column(db.Boolean, default=False, nullable=False)


# Funcionamento do estabelecimento
class Funcionamento(BaseModel):
    __tablename__ = 'funcionamentos'

    estabelecimento_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('estabelecimentos.id'),
        nullable=False,
        index=True
    )
    menor_time = db.Column(db.Integer, default=10, nullable=False)

    seg_inicio = db.Column(Time, nullable=True)
    seg_fim    = db.Column(Time, nullable=True)
    ter_inicio = db.Column(Time, nullable=True)
    ter_fim    = db.Column(Time, nullable=True)
    qua_inicio = db.Column(Time, nullable=True)
    qua_fim    = db.Column(Time, nullable=True)
    qui_inicio = db.Column(Time, nullable=True)
    qui_fim    = db.Column(Time, nullable=True)
    sex_inicio = db.Column(Time, nullable=True)
    sex_fim    = db.Column(Time, nullable=True)
    sab_inicio = db.Column(Time, nullable=True)
    sab_fim    = db.Column(Time, nullable=True)
    dom_inicio = db.Column(Time, nullable=True)
    dom_fim    = db.Column(Time, nullable=True)

    estabelecimento = db.relationship(
        'Estabelecimento', backref='funcionamento', lazy=True
    )


# Horários disponíveis
class Horario(BaseModel):
    __tablename__ = 'horarios'

    estabelecimento_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('estabelecimentos.id'), nullable=False, index=True
    )
    colaborador_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('colaboradores.id'), nullable=False, index=True
    )
    data = db.Column(db.Date, nullable=False)
    horarios = db.Column(ARRAY(Time), nullable=False)

    # Relacionamento: um Horario → muitos Agendamentos
    agendamentos = db.relationship(
        'Agendamento', back_populates='horario', lazy=True
    )

    horario_inicial = db.Column(Time, nullable=True)
    horario_final = db.Column(Time, nullable=True)
    menor_time = db.Column(
        db.Integer,        # importa e usa o tipo Integer
        default=10,        # valor padrão (opcional)
        nullable=False     # força valor não-nulo
    )

    estabelecimento = db.relationship(
        'Estabelecimento', backref='horarios', lazy=True
    )
    colaborador = db.relationship(
        'Colaborador', backref='horarios', lazy=True
    )


# Estabelecimento
class Estabelecimento(BaseModel):
    __tablename__ = 'estabelecimentos'

    identificador_base = db.Column(db.String(10), nullable=False, unique=True, index=True)
    email_login = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(128), nullable=False)
    nome_fantasia = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(20), nullable=True, unique=True)
    telefone = db.Column(db.String(20), nullable=True)
    pagarme_recipient_id = db.Column(db.String(50), nullable=True, unique=True)

    colaboradores = db.relationship('Colaborador', backref='estabelecimento', lazy=True)
    planos = db.relationship('Plano', backref='estabelecimento', lazy=True)
    clientes = db.relationship('Cliente', backref='estabelecimento', lazy=True)
    agendamentos = db.relationship('Agendamento', backref='estabelecimento', lazy=True)


# Cliente
class Cliente(BaseModel):
    __tablename__ = 'clientes'

    email_login = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(128), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=True, unique=True)
    telefone = db.Column(db.String(20), nullable=True)

    pagarme_customer_id = db.Column(db.String(50), nullable=True, unique=True)
    card_token = db.Column(db.String(100), nullable=True)
    card_last_digits = db.Column(db.String(4), nullable=True)
    card_brand = db.Column(db.String(20), nullable=True)

    estabelecimento_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('estabelecimentos.id'), nullable=False
    )
    assinaturas = db.relationship('Assinatura', backref='cliente', lazy=True)
    agendamentos = db.relationship('Agendamento', backref='cliente', lazy=True)


# Colaborador
class Colaborador(BaseModel):
    __tablename__ = 'colaboradores'

    nome = db.Column(db.String(100), nullable=False)
    estabelecimento_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('estabelecimentos.id'), nullable=False
    )
    agendamentos = db.relationship('Agendamento', backref='colaborador', lazy=True)


# Serviço
default_numeric = db.Numeric(10, 2)

class Servico(BaseModel):
    __tablename__ = 'servicos'

    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    duracao = db.Column(db.Integer, nullable=False)
    preco = db.Column(default_numeric, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    estabelecimento_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('estabelecimentos.id'), nullable=False
    )
    agendamentos = db.relationship(
        'Agendamento', secondary=agendamento_servico, back_populates='servicos', lazy=True
    )


# Plano
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


# Assinatura
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

    agendamentos = db.relationship('Agendamento', backref='assinatura', lazy=True)


# Agendamento
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

    # FK: referência ao Horario
    horario_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('horarios.id'), nullable=True, index=True
    )
    horario = db.relationship('Horario', back_populates='agendamentos', lazy=True)

    # Separação de data e hora: data e múltiplos horários
    data = db.Column(db.Date, nullable=False)
    horas = db.Column(ARRAY(Time), nullable=False)

    duracao = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pendente', nullable=False)

    servicos = db.relationship(
        'Servico', secondary=agendamento_servico, back_populates='agendamentos', lazy=True
    )
