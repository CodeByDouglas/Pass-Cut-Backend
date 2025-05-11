import uuid

def verificar_ids_servicos(ids: list) -> bool:
    """
    Verifica se o array de IDs de serviço possui no mínimo 1 e no máximo 10 itens,
    e se cada ID segue o formato UUID esperado.
    
    Parameters:
        ids (list): Lista de IDs de serviço (str).
    
    Returns:
        bool: True se o array atender os critérios, False caso contrário.
    """
    if not (1 <= len(ids) <= 10):
        return False

    for id_str in ids:
        try:
            uuid.UUID(id_str)
        except ValueError:
            return False

    return True