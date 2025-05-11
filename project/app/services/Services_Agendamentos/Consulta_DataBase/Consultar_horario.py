import math
from datetime import time, datetime
from app.extensions import db
from app.models.models import Funcionamento, Servico, Horario

def consultar_horarios_agendamento(estabelecimento_id: str, colaborador_id: str, data: str, servico_ids: list):
    """
    Recebe:
      - estabelecimento_id: o ID do estabelecimento;
      - colaborador_id: o ID do colaborador;
      - data: uma data em formato 'YYYY-MM-DD';
      - servico_ids: um array com de 1 a 10 IDs de serviço.
      
    Procedimentos:
      1. Busca na tabela Funcionamento o campo 'menor_time' usando o estabelecimento_id.
      2. Para cada ID de serviço no array, busca o serviço na tabela Servico (vinculado ao estabelecimento)
         e soma o valor do campo 'duracao'.
      3. Calcula a quantidade de horários sequenciais necessários (required_slots) como:
         required_slots = ceil(total_duracao / menor_time).
      4. Busca na tabela Horario, usando estabelecimento_id, colaborador_id e data, e extrai o array de horários.
      5. Percorre o array de horários e agrupa os horários consecutivos (diferentes de "00:00:00"). Ao final de cada bloco,
         verifica cada posição que possa iniciar uma sequência com comprimento >= required_slots e a adiciona ao array de resultados.
      6. Se nenhum horário for encontrado, retorna (True, [None]). Em caso de erro, retorna False.
      
    Returns:
        tuple: (True, array_de_horarios) se o processo ocorrer sem erro.
        Ex: (True, [<hora_inicial_da_sequencia>, ...]) ou (True, [None]) se nenhum horário disponível.
        bool: False em caso de erro.
    """
    try:
        # 1. Busca o 'menor_time' na tabela Funcionamento
        funcionamento = db.session.query(Funcionamento).filter_by(estabelecimento_id=estabelecimento_id).first()
        if not funcionamento:
            return False
        menor_time = funcionamento.menor_time

        # 2. Soma a duração de cada serviço
        total_duracao = 0
        for servico_id in servico_ids:
            servico = db.session.query(Servico).filter_by(id=servico_id, estabelecimento_id=estabelecimento_id).first()
            if servico:
                total_duracao += servico.duracao

        # 3. Calcula os espaços requeridos (arredondando para cima)
        required_slots = math.ceil(total_duracao / menor_time)

        # 4. Busca o registro de Horario para o estabelecimento, colaborador e data informados
        horario_record = db.session.query(Horario).filter_by(
            estabelecimento_id=estabelecimento_id,
            colaborador_id=colaborador_id,
            data=data
        ).first()
        if not horario_record:
            return True, [None]

        available_slots = horario_record.horarios   # array de objetos time ou strings

        # 5. Percorre o array e agrupa os horários consecutivos que não são 00:00:00,
        #    avaliando todas as posições possíveis como início de uma sequência válida.
        found_slots = []
        current_block = []
        zero_time = time(0, 0, 0)

        # Função auxiliar para processar a sequência atual
        def process_block(block):
            if len(block) >= required_slots:
                # Para cada posição que permita uma sequência de tamanho required_slots, registre o horário de início.
                for i in range(len(block) - required_slots + 1):
                    found_slots.append(block[i])
        
        for slot in available_slots:
            
            if slot != zero_time:
                current_block.append(slot)
            else:
                # Quando encontra 00:00:00, processa o bloco atual e reseta
                process_block(current_block)
                current_block = []
        # Processa o último bloco, caso exista
        process_block(current_block)

        # 6. Retorna os resultados
        if found_slots:
            return True, found_slots
        else:
            return True, [None]
    except Exception as e:
        return False