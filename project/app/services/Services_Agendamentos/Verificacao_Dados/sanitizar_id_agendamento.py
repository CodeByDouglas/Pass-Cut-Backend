import uuid

def verificar_id_agendamento(agendamento_id: str) -> bool:
    """
    Verifica se o agendamento_id fornecido segue o padrão UUID esperado pelo modelo.

    Parâmetros:
        agendamento_id (str): O ID do agendamento a ser validado.

    Retorna:
        bool: True se for um UUID válido, False caso contrário.
    """
    try:
        uuid.UUID(agendamento_id)
        return True
    except ValueError:
        return False