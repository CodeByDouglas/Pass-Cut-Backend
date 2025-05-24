import os
import jwt
from dotenv import load_dotenv
from app.models.models import Cliente  # see [`Cliente`](project/app/models/models.py)
from app.extensions import db           # see [`db`](project/app/extensions.py)

load_dotenv()

def validar_token_id_user(estabelecimento_id: str, token: str):
    """
    Descriptografa o token JWT utilizando a chave SECRET_KEY_ID_USER do .env.
    Caso consiga extrair o 'id' do payload e exista um Cliente que esteja relacionado 
    ao estabelecimento informado com esse user id, retorna (True, user_id). Caso contrário, retorna False.
    
    Parameters:
        estabelecimento_id (str): O ID do estabelecimento (base).
        token (str): Token JWT a ser validado (ID de user).
        
    Returns:
        tuple: (True, user_id) se o token for válido e o cliente existir.
        bool: False caso a validação falhe.
    """
    secret = os.getenv("SECRET_KEY_ID_USER")
    if not secret:
        return False

    try:
        # Tenta decodificar o token JWT usando HS256
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = payload.get("id")
        if not user_id:
            return False
    except Exception:
        return False

    # Verifica se existe um Cliente com o ID extraído que está relacionado ao estabelecimento informado
    cliente = db.session.query(Cliente).filter_by(id=user_id, estabelecimento_id=estabelecimento_id).first()
    if cliente:
        return True, user_id
    return False