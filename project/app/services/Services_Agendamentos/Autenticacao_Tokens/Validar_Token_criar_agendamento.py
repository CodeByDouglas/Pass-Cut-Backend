import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

def validar_token_consultar_servico(token: str) -> bool:
    """
    Descriptografa o token usando a chave CHAVE_API_CRIAR_AGENDAMENTO do .env e compara
    com o token esperado, definido em TOKEN_API_CRIAR_AGENDAMENTO.
    
    Returns:
        bool: True se os tokens coincidirem, False caso contrário.
    """
    chave = os.getenv("CHAVE_API_CRIAR_AGENDAMENTO")
    expected_token = os.getenv("TOKEN_API_CRIAR_AGENDAMENTO")
    
    if not (chave and expected_token):
        return False
    
    try:
        # Remove possíveis aspas extras
        chave_limpa = chave.strip().strip('"')
        expected_limpo = expected_token.strip().strip('"')
        
        fernet = Fernet(chave_limpa)
        decrypted = fernet.decrypt(token.encode())
        return decrypted.decode() == expected_limpo
    except Exception:
        return False