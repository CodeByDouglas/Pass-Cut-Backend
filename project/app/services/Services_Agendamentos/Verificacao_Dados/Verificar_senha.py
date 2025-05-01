import re

def verificar_senha(senha: str) -> bool:
    """
    Valida se a senha segue os seguintes critérios:
      - Possui entre 8 e 30 caracteres.
      - Contém pelo menos uma letra minúscula.
      - Contém pelo menos uma letra maiúscula.
      - Contém pelo menos um dígito numérico.
      - Contém pelo menos um símbolo (qualquer caractere que não seja letra ou dígito).
      - Não pode conter espaços.
    
    Além disso, a função verifica se a senha não contém padrões potencialmente maliciosos,
    como trechos de script, SQL injection ou XSS (exemplo: '<script', '--', 'OR 1=1', etc.).
    
    Parameters:
        senha (str): A senha a ser validada.
    
    Returns:
        bool: True se a senha for válida e segura, False caso contrário.
    """
    # Verifica o comprimento da senha
    if not (8 <= len(senha) <= 30):
        return False
    
    # Expressão regular para validar o padrão da senha:
    # ^(?!.*\s) => Assegura que não haja espaços.
    # (?=.*[a-z])  => Pelo menos uma letra minúscula.
    # (?=.*[A-Z])  => Pelo menos uma letra maiúscula.
    # (?=.*\d)     => Pelo menos um dígito.
    # (?=.*[^A-Za-z0-9])  => Pelo menos um símbolo.
    padrao = r'^(?!.*\s)(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,30}$'
    if not re.fullmatch(padrao, senha):
        return False

    # Verifica padrões de possíveis injeções ou códigos maliciosos.
    padroes_maliciosos = [
        r'(?i)<\s*script',        # Detecção de <script ou variantes com espaços
        r'(?i)</\s*script',       # Detecção de </script>
        r'(?i)--',                # Comentário SQL
        r'(?i)\b(OR|AND)\b\s+\d+\s*=\s*\d+',  # Padrão típico de SQL injection (ex: OR 1=1)
        r'(?i)(DROP\s+TABLE|INSERT\s+INTO|UPDATE\s+\w+\s+SET)'  # Comandos SQL perigosos
    ]
    for pad in padroes_maliciosos:
        if re.search(pad, senha):
            return False

    return True