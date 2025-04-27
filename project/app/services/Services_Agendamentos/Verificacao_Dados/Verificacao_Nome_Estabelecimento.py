import re

def verificar_nome_estabelecimento(nome: str) -> bool:
    """
    Verifica se o 'nome' recebido é seguro, isto é, se não contém caracteres especiais 
    ou padrões maliciosos, permitindo apenas letras, dígitos e espaços. Além disso, o nome deve 
    possuir no máximo 100 caracteres.

    Parameters:
        nome (str): Nome a ser validado.
        
    Returns:
        bool: True se o nome estiver dentro dos padrões aceitos, False caso contrário.
    """
    # Verifica se o nome possui no máximo 100 caracteres.
    if len(nome) > 100:
        return False
    
    # Regex que permite apenas letras (A-Z, a-z), números (0-9) e espaços.
    padrao = r'^[A-Za-z0-9 ]+$'
    
    if re.fullmatch(padrao, nome):
        return True
    else:
        return False