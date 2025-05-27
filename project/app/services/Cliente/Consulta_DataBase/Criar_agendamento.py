from app.models.models import Servico, Horario, Agendamento, Assinatura
from datetime import datetime, timedelta, time
from app.extensions import db
import math

def agendar(estabelecimento_id: str, cliente_id: str, servico_ids: list, colaborador_id: str, data: str, horario: str):
    """
    Recebe os parâmetros necessários para criar um agendamento.
    1. Busca os serviços pelo ID do estabelecimento e pelos IDs do array,
       e soma o valor do campo 'duracao' de cada serviço encontrado.
    2. Busca o registro de Horario pelo estabelecimento, colaborador e data.
    3. Calcula a quantidade de slots necessários para o agendamento.
    4. Gera um array apenas com os horários ocupados no formato [HH:MM:SS, ...].
    5. Verifica se a sequência de horários está disponível no array de horários da tabela Horario.
       Se estiver, bloqueia os horários (substitui por 00:00:00) e atualiza o registro.
       Se não estiver, retorna False e mensagem de horário indisponível.

    Retorna:
        tuple: (True, duração_total, quantidade_de_slot, horarios_ocupados) em caso de sucesso,
               (False, "Horário indisponível") em caso de conflito.
    """
    # 1. Busca todos os serviços do estabelecimento cujos IDs estão no array
    servicos = db.session.query(Servico).filter(
        Servico.estabelecimento_id == estabelecimento_id,
        Servico.id.in_(servico_ids)
    ).all()

    # Soma a duração de todos os serviços encontrados
    duracao_total = sum(servico.duracao for servico in servicos)

    # 2. Busca o registro de Horario para o estabelecimento, colaborador e data informados
    horario_record = db.session.query(Horario).filter_by(
        estabelecimento_id=estabelecimento_id,
        colaborador_id=colaborador_id,
        data=data
    ).first()
    if not horario_record:
        return False, "Erro interno"

    # 3. Calcula a quantidade de slots necessários
    menor_time = horario_record.menor_time
    quantidade_de_slot = math.ceil(duracao_total / menor_time)

    # 4. Gera o array apenas com os horários ocupados (formato datetime.time)
    horarios_ocupados = []
    data_hora_inicial = datetime.strptime(f"{data} {horario}", "%Y-%m-%d %H:%M:%S")
    for i in range(quantidade_de_slot):
        proximo_horario = (data_hora_inicial + timedelta(minutes=menor_time * i)).time()
        horarios_ocupados.append(proximo_horario)

    # 5. Verifica se todos os horários estão disponíveis no array de horários da tabela Horario
    horarios_disponiveis = list(horario_record.horarios)
    indices_para_bloquear = []
    for h in horarios_ocupados:
        try:
            idx = horarios_disponiveis.index(h)
            indices_para_bloquear.append(idx)
        except ValueError:
            return False, "Horário indisponível"

    # 6. Bloqueia os horários substituindo por 00:00:00
    for idx in indices_para_bloquear:
        horarios_disponiveis[idx] = time(0, 0, 0)
    horario_record.horarios = horarios_disponiveis
    db.session.commit()

      # 8. Verifica se o cliente possui assinatura ativa
    assinatura = db.session.query(Assinatura).filter_by(
        cliente_id=cliente_id,
        status="ativa"
    ).first()
    assinatura_id = assinatura.id if assinatura else None

    # 9. Cria o objeto Agendamento
    agendamento = Agendamento(
        estabelecimento_id=estabelecimento_id,
        colaborador_id=colaborador_id,
        cliente_id=cliente_id,
        horario_id=horario_record.id,
        data=datetime.strptime(data, "%Y-%m-%d").date(),
        horas=horarios_ocupados,
        duracao=duracao_total,
        status="pendente",
        assinatura_id=assinatura_id
    )
    # Adiciona os serviços ao relacionamento muitos-para-muitos
    agendamento.servicos = db.session.query(Servico).filter(Servico.id.in_(servico_ids)).all()

    db.session.add(agendamento)
    db.session.commit()

    return True