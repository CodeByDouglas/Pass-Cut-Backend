import os
import jwt
from dotenv import load_dotenv
from app.models.models import Estabelecimento  # see [`Estabelecimento`](project/app/models/models.py)
from app.extensions import db              # see [`db`](project/app/extensions.py)

load_dotenv()

def validar_token_id_estabelecimento(token: str):
    """
    Descriptografa o token JWT utilizando a chave SECRET_KEY_ID_ESTABELECIMENTO do .env.
    Caso consiga extrair o 'id' do payload e exista um estabelecimento com esse ID no banco,
    retorna (True, estabelecimento_id). Caso contrário, retorna False.
    
    Parameters:
        token (str): Token JWT a ser validado.
        
    Returns:
        tuple: (True, estabelecimento_id) se o token for válido e o estabelecimento existir.
        bool: False caso a validação falhe.
    """
    secret = os.getenv("SECRET_KEY_ID_ESTABELECIMENTO")
    if not secret:
        return False

    try:
        # Tenta decodificar o token JWT usando HS256
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        estabelecimento_id = payload.get("id")
        if not estabelecimento_id:
            return False
    except Exception:
        return False
    
    # Verifica se existe um estabelecimento com o ID extraído
    estabelecimento = db.session.query(Estabelecimento).filter_by(id=estabelecimento_id).first()
    if estabelecimento:
        return True, estabelecimento_id
    return False