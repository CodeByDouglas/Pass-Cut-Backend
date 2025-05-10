from cryptography.fernet import Fernet

def gerar_token(chave: str, dado: str) -> str:
    """
    Recebe uma chave e uma string e gera um token criptografado utilizando Fernet.
    
    Parameters:
        chave (str): A chave de encriptação (deve ser gerada previamente com Fernet.generate_key() e codificada em str).
        dado (str): A string a ser encriptada.
        
    Returns:
        str: O token criptografado.
    """
    # Converte a chave para bytes se ela estiver em formato de string
    chave_bytes = chave.encode() if isinstance(chave, str) else chave
    fernet = Fernet(chave_bytes)
    
    # Criptografa o dado, convertendo-o para bytes
    token = fernet.encrypt(dado.encode())
    print(token.decode())
    
    # Retorna o token como string
    return token.decode()

gerar_token("Rus2p35nJ38ft1xsqCP9nq91rZ2TOXQFB_q_ScPOdkY=", "Urfm1VW0R5xxXzEM6eCxvcjoBgSDKiZO96T7Yo98qOEQq93GR4eK3W2t1pElwG4BymAFtlqrLJXryVy9JxHXilZfh9n9d5O3r286")