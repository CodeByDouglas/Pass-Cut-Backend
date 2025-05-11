import uuid

def verificar_id_colaborador(id_str: str) -> bool:
    """
    Verifica se o ID fornecido segue o formato UUID esperado.
    
    Parameters:
        id_str (str): O ID a ser validado.
        
    Returns:
        bool: True se o ID for um UUID válido, False caso contrário.
    """
    try:
        uuid.UUID(id_str)
        return True
    except ValueError:
        return False