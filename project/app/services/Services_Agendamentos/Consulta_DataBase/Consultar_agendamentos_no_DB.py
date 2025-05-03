from app.models.models import Agendamento  # see [`Agendamento`](project/app/models/models.py)
from app.extensions import db

def consultar_agendamentos_por_estabelecimento_cliente_status(estabelecimento_id: str, cliente_id: str, status: str):
    """
    Busca os agendamentos que correspondem ao estabelecimento, cliente e status informados.
    
    Caso o status informado seja "ativos", retorna os agendamentos com status "Confirmado" ou "pendente".
    Caso seja "historico", retorna os agendamentos com status "cancelado" ou "concluído".
    Para outros valores, faz a busca usando o status recebido.
    
    Para cada agendamento encontrado, extrai:
      - Data e hora (campo data_hora)
      - Duração (campo duracao)
      - Nome do colaborador responsável (através do relacionamento 'colaborador')
      - Nome dos serviços relacionados (através do relacionamento 'servicos')
      - Nome do estabelecimento (através do relacionamento 'estabelecimento', campo nome_fantasia)
    
    Returns:
        list: Lista de dicionários com os dados extraídos dos agendamentos.
        None: Caso nenhum agendamento seja encontrado.
    """
    if status == "ativos":
        agendamentos = db.session.query(Agendamento).filter(
            Agendamento.estabelecimento_id == estabelecimento_id,
            Agendamento.cliente_id == cliente_id,
            Agendamento.status.in_(["Confirmado", "pendente"])
        ).all()
    elif status == "historico":
        agendamentos = db.session.query(Agendamento).filter(
            Agendamento.estabelecimento_id == estabelecimento_id,
            Agendamento.cliente_id == cliente_id,
            Agendamento.status.in_(["cancelado", "concluído"])
        ).all()
    else:
        agendamentos = db.session.query(Agendamento).filter(
            Agendamento.estabelecimento_id == estabelecimento_id,
            Agendamento.cliente_id == cliente_id,
            Agendamento.status == status
        ).all()
    
    if not agendamentos:
        return None
    
    resultados = []
    for ag in agendamentos:
        dados = {
            "data_hora": ag.data_hora.isoformat() if ag.data_hora else None,
            "duracao": ag.duracao,
            "colaborador": ag.colaborador.nome if ag.colaborador and hasattr(ag.colaborador, 'nome') else None,
            "servicos": [servico.nome for servico in ag.servicos if hasattr(servico, 'nome')],
            "estabelecimento": ag.estabelecimento.nome_fantasia if ag.estabelecimento and hasattr(ag.estabelecimento, 'nome_fantasia') else None
        }
        resultados.append(dados)
    
    return resultados