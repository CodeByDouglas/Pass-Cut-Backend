from datetime import datetime, time, timedelta
import traceback
from app.models.models import Agendamento, Horario
from app.extensions import db

def cancelar_agendamento_db(agendamento_id: str, estabelecimento_id: str, cliente_id: str):
    """
    Cancela um agendamento e restaura os horários na tabela de disponibilidade.
    
    Parâmetros:
      - agendamento_id: Identificador único do agendamento
      - estabelecimento_id: Identificador do estabelecimento
      - cliente_id: Identificador do cliente
    
    Procedimento:
      1. Localiza o agendamento usando os IDs fornecidos
      2. Altera o status do agendamento para "cancelado"
      3. Se a data for hoje ou futura, restaura os horários na tabela Horario
      4. Salva as alterações no banco de dados
    
    Retorna:
      - True: Se o cancelamento foi realizado com sucesso
      - False: Se houve erro ou o agendamento não foi encontrado
    """
    try:
        # 1. LOCALIZAÇÃO DO AGENDAMENTO
        agendamento = db.session.query(Agendamento).filter_by(
            id=agendamento_id,
            estabelecimento_id=estabelecimento_id,
            cliente_id=cliente_id
        ).first()
        
        if not agendamento:
            return False
        
        # 2. ATUALIZAÇÃO DO STATUS
        agendamento.status = "cancelado"
        
        # 3. RESTAURAÇÃO DOS HORÁRIOS (apenas para datas atuais ou futuras)
        data_atual = datetime.now().date()
        data_agendamento = agendamento.data  # Já é do tipo date
        
        if data_agendamento >= data_atual:
            # 3.1 Busca o registro de horários relacionado
            registro_horario = db.session.query(Horario).filter_by(id=agendamento.horario_id).first()
            
            if registro_horario and (registro_horario.horario_inicial and registro_horario.horario_final):
                # 3.2 Geração da grade completa de horários do dia
                intervalo_minutos = registro_horario.menor_time
                horario_inicio = datetime.combine(data_agendamento, registro_horario.horario_inicial)
                horario_fim = datetime.combine(data_agendamento, registro_horario.horario_final)
                
                slots_esperados = []
                horario_atual = horario_inicio
                while horario_atual <= horario_fim:
                    slots_esperados.append(horario_atual.time())
                    horario_atual += timedelta(minutes=intervalo_minutos)
                
                if not slots_esperados:
                    return False
                
                # 3.3 Identificação da posição do primeiro horário agendado
                try:
                    Menor_horario_agendado = min(agendamento.horas)
                except Exception:
                    return False
                
                indice_alvo = None
                for indice, slot in enumerate(slots_esperados):
                    if slot >= Menor_horario_agendado:
                        indice_alvo = indice
                        break
                
                if indice_alvo is None:
                    indice_alvo = len(slots_esperados) - 1
                
                # 3.4 Restauração de todos os horários do agendamento em sequência
                horarios_ordenados = sorted(agendamento.horas)
                horarios_atualizados = list(registro_horario.horarios)
                for deslocamento, horario_agendado in enumerate(horarios_ordenados):
                    indice_slot = indice_alvo + deslocamento
                    if indice_slot < len(horarios_atualizados):
                        horarios_atualizados[indice_slot] = horario_agendado
                registro_horario.horarios = horarios_atualizados
        # 4. PERSISTÊNCIA DAS ALTERAÇÕES
        db.session.commit()
        return True
    
    except Exception:
        db.session.rollback()
        return False