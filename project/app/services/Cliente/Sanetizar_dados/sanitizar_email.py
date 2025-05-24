import re

def verificar_email(email: str) -> bool:
    """
    Verifica se o email recebido é válido e não contém padrões maliciosos, como injeção de script ou SQL.
    
    Essa função utiliza uma expressão regular que valida o formato de email padrão
    (permitindo letras, dígitos, pontos, underscores e hífens) e garante que o endereço
    possua um "@" seguido de um domínio com pelo menos um ponto.
    
    Parameters:
        email (str): O email a ser validado.
        
    Returns:
        bool: True se o email for válido e seguro, False caso contrário.
    """
    # Expressão regular para validar emails simples e evitar caracteres potencialmente maliciosos.
    padrao = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    
    # Verifica se o email bate exatamente com o padrão.
    if re.fullmatch(padrao, email):
        return True
    else:
        return False