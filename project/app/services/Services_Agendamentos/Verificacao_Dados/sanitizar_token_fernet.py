import base64

def verificar_token_fernet(token: str) -> bool:
    """
    Verifica se uma string é um token Fernet válido.

    Essa função tenta decodificar o token usando base64 urlsafe e verifica se o tamanho 
    dos bytes decodificados é compatível com a estrutura mínima de um token Fernet.
    
    A estrutura básica de um token Fernet é composta por:
      - 1 byte para a versão;
      - 8 bytes para o timestamp;
      - 16 bytes para o vetor de inicialização (IV);
      - N bytes para o ciphertext;
      - 32 bytes para o HMAC;
      
    Assim, o token decodificado deve ter pelo menos 1 + 8 + 16 + 32 = 57 bytes.
    
    Parameters:
        token (str): O token a ser verificado.
    
    Returns:
        bool: True se o token parecer ser um token Fernet válido, False caso contrário.
    """
    try:
        token_bytes = base64.urlsafe_b64decode(token)
    except Exception:
        return False

    if len(token_bytes) < 57:
        return False

    return True